from manim import *
import re
from collections import defaultdict

class KenKenGenerator(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors = ["#67DB6E", "#7DE083", "#AAECAF", "#D4F7D7"]
        
    def parse_descriptor_content(self, content):
        """Parse the KenKen descriptor content"""
        # Extract puzzle size
        size_match = re.search(r'size:\s*(\d+)', content)
        if not size_match:
            raise ValueError("Could not find puzzle size")
        size = int(size_match.group(1))
        
        # Extract cages
        cages = []
        lines = content.split('\n')
        
        # Find the start of cage definitions
        cage_start = -1
        for i, line in enumerate(lines):
            if line.strip() == "hint,cells,anchor":
                cage_start = i + 1
                break
        
        if cage_start == -1:
            # Try to find cages without header
            cage_start = 0
            for i, line in enumerate(lines):
                if re.search(r'\d+[x+\-]|^\d+,', line):
                    cage_start = i
                    break
        
        for line in lines[cage_start:]:
            line = line.strip()
            if not line or line.startswith("Hello!") or line.startswith("Analyzing"):
                break
                
            parts = line.split(',')
            if len(parts) < 3:
                continue
                
            hint = parts[0].strip()
            cells_str = parts[1].strip()
            anchor_str = parts[2].strip()
            
            # Parse cells - handle both (r,c) and (r,c);(r,c) formats
            cells = []
            cell_matches = re.findall(r'\((\d+),(\d+)\)', cells_str)
            for match in cell_matches:
                cells.append((int(match[0]), int(match[1])))
            
            # Parse anchor
            anchor_match = re.search(r'\((\d+),(\d+)\)', anchor_str)
            if anchor_match:
                anchor = (int(anchor_match.group(1)), int(anchor_match.group(2)))
            else:
                anchor = cells[0] if cells else (0, 0)
            
            if cells:
                cages.append({
                    'hint': hint,
                    'cells': cells,
                    'anchor': anchor
                })
        
        return size, cages
    
    def build_adjacency_graph(self, cages):
        """Build adjacency graph for cage coloring"""
        cage_adjacency = defaultdict(set)
        cell_to_cage = {}
        
        # Map cells to cage indices
        for cage_idx, cage in enumerate(cages):
            for cell in cage['cells']:
                cell_to_cage[cell] = cage_idx
        
        # Find adjacent cages
        for cage_idx, cage in enumerate(cages):
            for cell in cage['cells']:
                r, c = cell
                # Check 4-directional neighbors
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor_cell = (r + dr, c + dc)
                    if neighbor_cell in cell_to_cage:
                        neighbor_cage = cell_to_cage[neighbor_cell]
                        if neighbor_cage != cage_idx:
                            cage_adjacency[cage_idx].add(neighbor_cage)
                            cage_adjacency[neighbor_cage].add(cage_idx)
        
        return cage_adjacency
    
    def color_cages_greedy(self, cage_adjacency, num_cages):
        """Color cages using greedy coloring algorithm"""
        cage_colors = {}
        
        for cage_idx in range(num_cages):
            # Find colors used by adjacent cages
            used_colors = set()
            for adj_cage in cage_adjacency[cage_idx]:
                if adj_cage in cage_colors:
                    used_colors.add(cage_colors[adj_cage])
            
            # Assign first available color
            for color_idx in range(len(self.colors)):
                if color_idx not in used_colors:
                    cage_colors[cage_idx] = color_idx
                    break
        
        return cage_colors
    
    def construct(self):
        # Sample descriptor content (replace with file reading if needed)
        descriptor_content = """
Puzzle 1:
size: 4
allowed_numbers: 2 4 8 9
hint,cells,anchor
32x,(0,0);(0,1),(0,0)
10+,(0,2);(1,2),(0,2)
5-,(0,3);(1,3),(0,3)
16x,(1,0);(2,0),(1,0)
15+,(1,1);(2,1);(3,1),(1,1)
72x,(2,2);(2,3);(3,2),(2,2)
9,(3,0),(3,0)
8,(3,3),(3,3)
"""
        
        # Parse descriptor
        try:
            size, cages = self.parse_descriptor_content(descriptor_content)
        except Exception as e:
            print(f"Error parsing descriptor: {e}")
            return
        
        # Build adjacency graph and color cages
        cage_adjacency = self.build_adjacency_graph(cages)
        cage_colors = self.color_cages_greedy(cage_adjacency, len(cages))
        
        # Calculate cell size and grid position
        cell_size = 1.0
        grid_width = size * cell_size
        grid_height = size * cell_size
        
        # Center the grid
        start_x = -grid_width / 2
        start_y = grid_height / 2
        
        # Create background
        self.camera.background_color = WHITE
        
        # Create cage rectangles first
        all_rectangles = VGroup()
        
        for cage_idx, cage in enumerate(cages):
            color = self.colors[cage_colors[cage_idx]]
            
            # Create rectangles for each cell in the cage
            for cell in cage['cells']:
                row, col = cell
                x = start_x + col * cell_size + cell_size / 2
                y = start_y - row * cell_size - cell_size / 2
                
                rect = Rectangle(
                    width=cell_size,
                    height=cell_size,
                    fill_color=color,
                    fill_opacity=0.6,
                    stroke_color=BLACK,
                    stroke_width=1
                ).move_to([x, y, 0])
                
                all_rectangles.add(rect)
        
        # Create grid lines
        grid_lines = VGroup()
        
        # Vertical lines
        for i in range(size + 1):
            x = start_x + i * cell_size
            line = Line(
                start=[x, start_y, 0],
                end=[x, start_y - grid_height, 0],
                stroke_color=BLACK,
                stroke_width=2
            )
            grid_lines.add(line)
        
        # Horizontal lines
        for i in range(size + 1):
            y = start_y - i * cell_size
            line = Line(
                start=[start_x, y, 0],
                end=[start_x + grid_width, y, 0],
                stroke_color=BLACK,
                stroke_width=2
            )
            grid_lines.add(line)
        
        # Create hint texts
        hint_texts = VGroup()
        
        for cage_idx, cage in enumerate(cages):
            # Add hint text at anchor position
            anchor_row, anchor_col = cage['anchor']
            anchor_x = start_x + anchor_col * cell_size + 0.15
            anchor_y = start_y - anchor_row * cell_size - 0.15
            
            hint_text = Text(
                cage['hint'],
                font_size=18,
                color=BLACK
            ).move_to([anchor_x, anchor_y, 0])
            
            # Align to top-left of cell
            hint_text.align_to([anchor_x - cell_size/2, anchor_y + cell_size/2, 0], UL)
            hint_text.shift(0.1 * RIGHT + 0.1 * DOWN)
            
            hint_texts.add(hint_text)
        
        # Create title
        title = Text(
            f"KenKen Puzzle ({size}×{size})",
            font_size=24,
            color=BLACK
        ).to_edge(UP, buff=0.5)
        
        # Add all elements to scene
        self.add(all_rectangles)
        self.add(grid_lines)
        self.add(hint_texts)
        self.add(title)

# To use with external file, modify the construct method to read from file:
# with open("descriptor_.txt", "r") as f:
#     descriptor_content = f.read()

from manim import *
import re
from collections import defaultdict, deque

class KenKenGenerator(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.colors = ["#67DB6E", "#7DE083", "#AAECAF", "#D4F7D7"]
        
    def parse_descriptor(self, filename):
        """Parse the KenKen descriptor file"""
        with open(filename, 'r') as f:
            content = f.read()
        
        # Extract puzzle size
        size_match = re.search(r'size:\s*(\d+)', content)
        if not size_match:
            raise ValueError("Could not find puzzle size")
        size = int(size_match.group(1))
        
        # Extract allowed numbers
        numbers_match = re.search(r'allowed_numbers:\s*([\d\s]+)', content)
        if not numbers_match:
            raise ValueError("Could not find allowed numbers")
        allowed_numbers = list(map(int, numbers_match.group(1).split()))
        
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
            raise ValueError("Could not find cage definitions")
        
        for line in lines[cage_start:]:
            line = line.strip()
            if not line or line.startswith("Hello!"):
                break
                
            parts = line.split(',')
            if len(parts) < 3:
                continue
                
            hint = parts[0].strip()
            cells_str = parts[1].strip()
            anchor_str = parts[2].strip()
            
            # Parse cells
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
        
        return size, allowed_numbers, cages
    
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
        # Parse descriptor file
        try:
            size, allowed_numbers, cages = self.parse_descriptor("descriptor_.txt")
        except Exception as e:
            # Fallback to sample data if file not found
            size = 4
            cages = [
                {'hint': '32×', 'cells': [(0,0), (0,1)], 'anchor': (0,0)},
                {'hint': '10+', 'cells': [(0,2), (1,2)], 'anchor': (0,2)},
                {'hint': '5-', 'cells': [(0,3), (1,3)], 'anchor': (0,3)},
                {'hint': '16×', 'cells': [(1,0), (2,0)], 'anchor': (1,0)},
                {'hint': '15+', 'cells': [(1,1), (2,1), (3,1)], 'anchor': (1,1)},
                {'hint': '72×', 'cells': [(2,2), (2,3), (3,2)], 'anchor': (2,2)},
                {'hint': '9', 'cells': [(3,0)], 'anchor': (3,0)},
                {'hint': '8', 'cells': [(3,3)], 'anchor': (3,3)}
            ]
        
        # Build adjacency graph and color cages
        cage_adjacency = self.build_adjacency_graph(cages)
        cage_colors = self.color_cages_greedy(cage_adjacency, len(cages))
        
        # Calculate cell size and grid position
        cell_size = 1.2
        grid_width = size * cell_size
        grid_height = size * cell_size
        
        # Center the grid
        start_x = -grid_width / 2
        start_y = grid_height / 2
        
        # Create cage groups
        cage_groups = []
        
        for cage_idx, cage in enumerate(cages):
            color = self.colors[cage_colors[cage_idx]]
            cage_group = VGroup()
            
            # Create rectangles for each cell in the cage
            for cell in cage['cells']:
                row, col = cell
                x = start_x + col * cell_size + cell_size / 2
                y = start_y - row * cell_size - cell_size / 2
                
                rect = Rectangle(
                    width=cell_size,
                    height=cell_size,
                    fill_color=color,
                    fill_opacity=0.7,
                    stroke_color=WHITE,
                    stroke_width=2
                ).move_to([x, y, 0])
                
                cage_group.add(rect)
            
            # Add hint text at anchor position
            anchor_row, anchor_col = cage['anchor']
            anchor_x = start_x + anchor_col * cell_size + cell_size / 4
            anchor_y = start_y - anchor_row * cell_size - cell_size / 4
            
            hint_text = Text(
                cage['hint'],
                font_size=20,
                color=BLACK,
                font="Arial"
            ).move_to([anchor_x, anchor_y, 0])
            
            cage_group.add(hint_text)
            cage_groups.append(cage_group)
        
        # Create outer grid lines
        grid_lines = VGroup()
        
        # Vertical lines
        for i in range(size + 1):
            x = start_x + i * cell_size
            line = Line(
                start=[x, start_y, 0],
                end=[x, start_y - grid_height, 0],
                stroke_color=BLACK,
                stroke_width=3
            )
            grid_lines.add(line)
        
        # Horizontal lines
        for i in range(size + 1):
            y = start_y - i * cell_size
            line = Line(
                start=[start_x, y, 0],
                end=[start_x + grid_width, y, 0],
                stroke_color=BLACK,
                stroke_width=3
            )
            grid_lines.add(line)
        
        # Add title
        title = Text(
            f"KenKen Puzzle ({size}×{size})",
            font_size=36,
            color=BLACK
        ).to_edge(UP, buff=0.5)
        
        # Add all elements to scene
        self.add(title)
        for cage_group in cage_groups:
            self.add(cage_group)
        self.add(grid_lines)


# To generate the image, save this as kenken_generator.py and run:
# manim -p -s kenken_generator.py KenKenGenerator

if __name__ == "__main__":
    # Example usage
    scene = KenKenGenerator()
    scene.construct()

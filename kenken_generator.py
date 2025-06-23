from manim import *
import re
from collections import defaultdict
import argparse

class KenKenGenerator(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Define four colors for cages
        self.colors = ["#D4F7D7", "#CFE4F9", "#E0D5F7", "#F7D4D4"]

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
            raise ValueError("Could not find cage definitions header")

        for line in lines[cage_start:]:
            line = line.strip()
            if not line or line.startswith("Hello!") or line.startswith("Analyzing"):
                break

            # Split by comma, but be careful with parentheses
            # Format: hint,cells,anchor where cells can be (r,c);(r,c);(r,c)
            parts = []
            current_part = ""
            paren_count = 0

            for char in line:
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif char == ',' and paren_count == 0:
                    parts.append(current_part.strip())
                    current_part = ""
                    continue
                current_part += char

            if current_part.strip():
                parts.append(current_part.strip())

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
                print(f"Parsed cage: {hint} with {len(cells)} cells at {cells}")

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
        # Try to read from descriptor file, fall back to hardcoded if not found
        try:
            with open("descriptor_.txt", "r") as f:
                descriptor_content = f.read()
            size, cages = self.parse_descriptor_content(descriptor_content)
            print(f"Successfully loaded from descriptor_.txt: {len(cages)} cages for {size}x{size} puzzle")
        except FileNotFoundError:
            print("descriptor_.txt not found, using hardcoded sample data")
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
        except Exception as e:
            print(f"Error parsing descriptor file: {e}")
            return

        # Build adjacency graph and color cages
        cage_adjacency = self.build_adjacency_graph(cages)
        cage_colors = self.color_cages_greedy(cage_adjacency, len(cages))

        print(f"Cage colors: {cage_colors}")

        # Calculate cell size and grid position
        cell_size = 1.0
        grid_width = size * cell_size
        grid_height = size * cell_size

        # Center the grid
        start_x = -grid_width / 2
        start_y = grid_height / 2

        # Create background
        self.camera.background_color = BLACK

        # Create cage rectangles first
        all_rectangles = VGroup()

        for cage_idx, cage in enumerate(cages):
            color = self.colors[cage_colors[cage_idx]]
            print(f"Cage {cage_idx}: {cage['hint']} with color {color} at cells {cage['cells']}")

            # Create rectangles for each cell in the cage
            for cell in cage['cells']:
                row, col = cell
                x = start_x + col * cell_size + cell_size / 2
                y = start_y - row * cell_size - cell_size / 2

                rect = Rectangle(
                    width=cell_size,
                    height=cell_size,
                    fill_color=color,
                    fill_opacity=0.8,
                    stroke_color=BLACK,
                    stroke_width=0.5
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
            anchor_x = start_x + anchor_col * cell_size
            anchor_y = start_y - anchor_row * cell_size

            hint_text = Text(
                cage['hint'],
                font_size=16,
                color=BLACK,
                weight=BOLD
            )

            # Position at top-left corner of the anchor cell
            hint_text.move_to([anchor_x + cell_size/2 - 0.25, anchor_y - cell_size/2 + 0.35, 0])

            hint_texts.add(hint_text)
            print(f"Added hint '{cage['hint']}' at position ({anchor_x - cell_size/2 + 0.15}, {anchor_y + cell_size/2 - 0.15})")

        # Create title
        title = Text(
            f"KenKen Puzzle ({size}×{size})",
            font_size=24,
            color=BLACK
        ).to_edge(UP, buff=0.5)

        # Add all elements to scene
        print(f"Adding {len(all_rectangles)} rectangles")
        print(f"Adding {len(hint_texts)} hint texts")
        print(f"Adding {len(grid_lines)} grid lines")

        self.add(all_rectangles)
        self.add(hint_texts)
        self.add(grid_lines)
        self.add(title)

# To use with external file, modify the construct method to read from file:
# with open("descriptor_.txt", "r") as f:
#     descriptor_content = f.read()

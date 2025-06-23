from manim import *
import re

class KenKenPuzzle(Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set your puzzle file path here
        self.puzzle_file = "4x4_kenken_puzzle_words.txt"  # Change this path as needed

    def parse_puzzle_file(self, content):
        """Parse the KenKen puzzle descriptor format"""
        lines = content.strip().split('\n')

        # Parse header info
        size = None
        allowed_numbers = []
        cages = []

        for line in lines:
            line = line.strip()
            if line.startswith('size:'):
                size = int(line.split(':')[1].strip())
            elif line.startswith('allowed_numbers:'):
                allowed_numbers = list(map(int, line.split(':')[1].strip().split()))
            elif line.startswith('hint,cells,anchor'):
                continue  # Header line
            elif ',' in line and '(' in line:
                # Parse cage line: hint,cells,anchor
                parts = line.split(',')
                if len(parts) >= 3:
                    hint = parts[0].strip()
                    cells_part = parts[1].strip()
                    anchor_part = parts[2].strip()

                    # Parse cells: (0,0);(0,1) format
                    cells = []
                    cell_matches = re.findall(r'\((\d+),(\d+)\)', cells_part)
                    for match in cell_matches:
                        cells.append((int(match[0]), int(match[1])))

                    # Parse anchor
                    anchor_match = re.search(r'\((\d+),(\d+)\)', anchor_part)
                    if anchor_match:
                        anchor = (int(anchor_match.group(1)), int(anchor_match.group(2)))
                    else:
                        anchor = cells[0] if cells else (0, 0)

                    cages.append({
                        'hint': hint,
                        'cells': cells,
                        'anchor': anchor
                    })

        return {
            'size': size or 4,
            'allowed_numbers': allowed_numbers or [1, 2, 3, 4],
            'cages': cages
        }

    def get_cage_colors(self, num_cages):
        """Generate distinct colors for cages"""
        colors = [
            RED, YELLOW, GREEN, ORANGE, PURPLE, PINK,
            BLUE_B, GREEN_C, MAROON, TEAL,
            GOLD, GRAY, BLUE, LIGHT_PINK, "#00FFFF"
        ]
        return colors[:num_cages]

    def construct(self):
        # Default puzzle data (fallback)
        default_content = """Puzzle 1:
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
8,(3,3),(3,3)"""

        # Parse puzzle data
        try:
            with open(self.puzzle_file, 'r') as f:
                content = f.read()
            print(f"Successfully loaded puzzle from {self.puzzle_file}")
        except FileNotFoundError:
            print(f"File {self.puzzle_file} not found, using default puzzle")
            content = default_content
        except Exception as e:
            print(f"Error reading file: {e}, using default puzzle")
            content = default_content

        puzzle_data = self.parse_puzzle_file(content)

        # Title
        title = Text("KenKen Puzzle", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))

        # Grid parameters
        grid_size = puzzle_data['size']
        cell_size = 8.0 / grid_size  # Adaptive cell size

        # Create the main grid
        grid = VGroup()
        grid_offset = grid_size * cell_size / 2

        for i in range(grid_size + 1):
            # Vertical lines
            line = Line(
                start=[i * cell_size - grid_offset, grid_offset, 0],
                end=[i * cell_size - grid_offset, -grid_offset, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)

            # Horizontal lines
            line = Line(
                start=[-grid_offset, grid_offset - i * cell_size, 0],
                end=[grid_offset, grid_offset - i * cell_size, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)

        self.play(Create(grid))

        # Helper function to get cell center position
        def get_cell_center(row, col):
            x = col * cell_size - grid_offset + cell_size/2
            y = grid_offset - row * cell_size - cell_size/2
            return [x, y, 0]

        # Create cage backgrounds and labels
        cage_groups = VGroup()
        cage_colors = self.get_cage_colors(len(puzzle_data['cages']))

        for i, cage in enumerate(puzzle_data['cages']):
            cage_group = VGroup()
            color = cage_colors[i % len(cage_colors)]

            # Create background rectangles for each cell in the cage
            for row, col in cage["cells"]:
                center = get_cell_center(row, col)
                rect = Rectangle(
                    width=cell_size * 0.9,
                    height=cell_size * 0.9,
                    fill_color=color,
                    fill_opacity=0.3,
                    stroke_color=color,
                    stroke_width=3
                ).move_to(center)
                cage_group.add(rect)

            # Add operation label to the anchor cell
            anchor_row, anchor_col = cage["anchor"]
            anchor_center = get_cell_center(anchor_row, anchor_col)

            # Position label in top-left corner of the anchor cell
            label_pos = [
                anchor_center[0] - cell_size/2 + 0.15,
                anchor_center[1] + cell_size/2 - 0.15,
                0
            ]

            # Adjust font size based on grid size
            font_size = max(16, 32 - grid_size * 2)

            operation_label = Text(
                cage["hint"],
                font_size=font_size,
                color=BLACK,
                weight=BOLD
            ).move_to(label_pos)

            cage_group.add(operation_label)
            cage_groups.add(cage_group)

        # Animate cage creation
        self.play(
            *[Create(cage_group) for cage_group in cage_groups],
            run_time=2
        )

        # Add instructions
        allowed_nums_str = ", ".join(map(str, puzzle_data['allowed_numbers']))
        instructions = VGroup(
            Text(f"Fill each row and column with: {allowed_nums_str}", font_size=20),
            Text("Each cage must satisfy its operation", font_size=20),
            Text("No repeated numbers in any row or column", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT)
        instructions.to_edge(DOWN, buff=0.5)

        self.play(Write(instructions))

        # Categorize and highlight cages by operation type
        self.wait(1)

        multiply_cages = []
        add_cages = []
        subtract_cages = []
        divide_cages = []
        single_cages = []

        for i, cage in enumerate(puzzle_data['cages']):
            hint = cage['hint'].lower()
            if 'x' in hint or '*' in hint:
                multiply_cages.append(cage_groups[i])
            elif '+' in hint:
                add_cages.append(cage_groups[i])
            elif '-' in hint:
                subtract_cages.append(cage_groups[i])
            elif '/' in hint or '÷' in hint:
                divide_cages.append(cage_groups[i])
            else:
                single_cages.append(cage_groups[i])

        # Highlight different cage types
        if multiply_cages:
            mult_label = Text("Multiplication Cages", font_size=28, color=RED)
            mult_label.to_edge(LEFT, buff=1)
            self.play(Write(mult_label))
            self.play(*[Indicate(cage, color=RED) for cage in multiply_cages])
            self.play(FadeOut(mult_label))

        if add_cages:
            add_label = Text("Addition Cages", font_size=28, color=YELLOW)
            add_label.to_edge(LEFT, buff=1)
            self.play(Write(add_label))
            self.play(*[Indicate(cage, color=YELLOW) for cage in add_cages])
            self.play(FadeOut(add_label))

        if subtract_cages:
            sub_label = Text("Subtraction Cages", font_size=28, color=GREEN)
            sub_label.to_edge(LEFT, buff=1)
            self.play(Write(sub_label))
            self.play(*[Indicate(cage, color=GREEN) for cage in subtract_cages])
            self.play(FadeOut(sub_label))

        if divide_cages:
            div_label = Text("Division Cages", font_size=28, color=ORANGE)
            div_label.to_edge(LEFT, buff=1)
            self.play(Write(div_label))
            self.play(*[Indicate(cage, color=ORANGE) for cage in divide_cages])
            self.play(FadeOut(div_label))

        if single_cages:
            single_label = Text("Fixed Values", font_size=28, color=BLUE)
            single_label.to_edge(LEFT, buff=1)
            self.play(Write(single_label))
            self.play(*[Indicate(cage, color=BLUE) for cage in single_cages])
            self.play(FadeOut(single_label))

        # Final pause
        self.wait(3)

        # Fade out everything
        self.play(
            FadeOut(title),
            FadeOut(grid),
            FadeOut(cage_groups),
            FadeOut(instructions)
        )

        # End screen
        end_text = Text("Solve the KenKen Puzzle!", font_size=40, color=GOLD)
        self.play(Write(end_text))
        self.wait(2)

# Usage Instructions:
# 1. Save this file as kenken_puzzle.py
# 2. Put your puzzle file (4x4_kenken_puzzle_words.txt) in the same directory
# 3. Run: manim kenken_puzzle.py KenKenPuzzle -pqh
#
# To use a different puzzle file, change the puzzle_file path in the __init__ method above

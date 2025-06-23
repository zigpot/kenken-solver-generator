from manim import *
import numpy as np
import argparse
import sys
import os
import re

class KenKenInputSolver(Scene):
    def __init__(self, input_file=None, **kwargs):
        super().__init__(**kwargs)
        #self.input_file = input_file or "5x5_puzzle.txt"
        self.input_file = "descriptors/9x9_puzzle.txt"
        self.puzzle_data = None
        self.solution_data = None
        
    def parse_input_file(self):
        """Parse the input file to extract puzzle data and solution"""
        try:
            with open(self.input_file, 'r') as f:
                content = f.read().strip()
            
            # Split into puzzle definition and solution log
            parts = content.split("Hello! Starting KenKen solver.")
            if len(parts) != 2:
                raise ValueError("Invalid file format - missing solver log")
            
            puzzle_part = parts[0].strip()
            solution_part = parts[1].strip()
            
            # Parse puzzle definition
            lines = puzzle_part.split('\n')
            puzzle_info = {}
            cages = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('Puzzle'):
                    continue
                
                if line.startswith('size:'):
                    puzzle_info['size'] = int(line.split(':')[1].strip())
                elif line.startswith('allowed_numbers:'):
                    numbers_str = line.split(':')[1].strip()
                    puzzle_info['allowed_numbers'] = [int(x) for x in numbers_str.split()]
                elif line.startswith('hint,cells,anchor'):
                    continue
                else:
                    # Find positions of commas
                    comma_positions = [i for i, c in enumerate(line) if c == ',']
                    if len(comma_positions) >= 2:
                        split_index = comma_positions[-2]  # 2nd comma from the right
                        left = line[:split_index]
                        right = line[split_index + 1:]
                    else:
                        print("Not enough commas to split.")
                        continue
                    operation = left.strip().split(',',1)[0]
                    cells_str = left.strip().split(',',1)[1]
                    anchor_str = right.strip()
                    """print("operation:", operation)
                    print("cells_str:", cells_str)
                    print("anchor:", anchor)"""


                    parts = line.split(',', 2)  # Only split at the first 2 commas
                    if len(parts) < 2:
                        continue

                    """operation = parts[0].strip()
                    cells_str = parts[1].strip()
                    anchor_str = parts[2].strip() if len(parts) > 2 else None"""
                    """print("operation:", operation)
                    print("cells_str:", cells_str)
                    print("anchor_str:", anchor_str)"""

                    # Parse cells
                    cells = []
                    for cell_str in cells_str.split(';'):
                        cell_str = cell_str.strip()
                        if cell_str.startswith('(') and cell_str.endswith(')'):
                            coords = cell_str[1:-1].split(',')
                            if len(coords) == 2:
                                row, col = int(coords[0]), int(coords[1])
                                cells.append((row, col))

                    # Parse anchor
                    anchor = None
                    if anchor_str and anchor_str.startswith('(') and anchor_str.endswith(')'):
                        print("Parsing anchor:", anchor_str)
                        coords = anchor_str[1:-1].split(',')
                        if len(coords) == 2:
                            anchor = (int(coords[0]), int(coords[1]))

                    if cells:
                        cages.append({
                            'operation': operation,
                            'cells': cells,
                            'anchor': anchor or cells[0]
                        })
            
            # Parse solution from the log
            solution = {}
            solution_lines = solution_part.split('\n')
            


            for line in solution_lines:
                if line.startswith('Solution:'):
                    print("Found solution line:", line)
                    solution_str = line.split('Solution:')[1].strip()
                    # Parse the dictionary string
                    # Remove outer braces and split by commas
                    solution_str = solution_str.strip()[1:-1]  # Remove { }
                    # Match patterns like (x, y): z
                    pattern = r'\(\s*(\d+)\s*,\s*(\d+)\s*\):\s*(\d+)'
                    solution = {
                        (int(row), int(col)): int(val)
                        for row, col, val in re.findall(pattern, solution_str)
                    }
                    break
            
            self.puzzle_data = {
                'info': puzzle_info,
                'cages': cages
            }
            self.solution_data = solution
            print("Solution:", self.solution_data)
            
        except Exception as e:
            print(f"Error parsing input file: {e}")
            sys.exit(1)
    
    def assign_cage_colors(self):
        """Assign colors to cages"""
        colors = [RED, YELLOW, GREEN, ORANGE, PURPLE, PINK, BLUE_A, GREEN_A, 
                 TEAL, MAROON, LIGHT_BROWN, DARK_BLUE, GOLD, GRAY]
        
        for i, cage in enumerate(self.puzzle_data['cages']):
            cage['color'] = colors[i % len(colors)]
    
    def construct(self):
        # Parse input file
        self.parse_input_file()
        
        if not self.puzzle_data:
            print("No puzzle data found in the input file.")
        if not self.solution_data:
            print("No solution data found in the input file.")
        if not self.puzzle_data or not self.solution_data:
            # Show error message
            error_text = Text("Failed to parse input file!", font_size=36, color=RED)
            self.play(Write(error_text))
            self.wait(3)
            return
        
        # Assign colors to cages
        self.assign_cage_colors()
        
        # Get puzzle parameters
        grid_size = self.puzzle_data['info']['size']
        allowed_numbers = self.puzzle_data['info']['allowed_numbers']
        cages = self.puzzle_data['cages']
        
        # Title
        title = Text(f"KenKen Puzzle {grid_size}×{grid_size} - Step by Step Solution", 
                    font_size=40, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Grid parameters
        cell_size = 1.0
        grid_offset = grid_size * cell_size / 2
        
        # Create the main grid
        grid = VGroup()
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
        
        for cage in cages:
            cage_group = VGroup()
            
            # Create background rectangles for each cell in the cage
            for row, col in cage["cells"]:
                center = get_cell_center(row, col)
                rect = Rectangle(
                    width=cell_size * 0.9,
                    height=cell_size * 0.9,
                    fill_color=cage["color"],
                    fill_opacity=0.2,
                    stroke_color=cage["color"],
                    stroke_width=2
                ).move_to(center)
                cage_group.add(rect)
            
            # Add operation label to the anchor cell
            anchor_row, anchor_col = cage["anchor"]
            anchor_center = get_cell_center(anchor_row, anchor_col)
            
            # Position label in top-left corner
            label_pos = [
                anchor_center[0] - cell_size/2 + 0.1 + len(cage["operation"]) * 0.05,
                anchor_center[1] + cell_size/2 - 0.2,
                0
            ]
            
            operation_label = Text(
                cage["operation"],
                font_size=13,
                color=WHITE
            ).move_to(label_pos)
            
            cage_group.add(operation_label)
            cage_groups.add(cage_group)
        
        self.play(Create(cage_groups))
        
        # Create number tracking for each cell
        cell_numbers = {}
        
        # Initialize with empty
        for row in range(grid_size):
            for col in range(grid_size):
                cell_numbers[(row, col)] = None
        
        # Step 1: Show initial setup
        step_text = Text("Step 1: Analyze cage constraints", font_size=24, color=WHITE)
        step_text.to_edge(DOWN, buff=0.5)
        self.play(Write(step_text))
        
        # Show available numbers
        numbers_str = ", ".join(map(str, allowed_numbers))
        available = Text(f"Available numbers: {numbers_str}", font_size=20, color=YELLOW)
        available.next_to(title, DOWN)
        self.play(Write(available))
        
        self.wait(2)
        
        # Step 2: Show cage analysis
        self.play(Transform(step_text, Text("Step 2: Analyze each cage", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # Highlight each cage
        for cage in cage_groups:
            self.play(Indicate(cage, color=WHITE))
            self.wait(0.5)
        
        # Step 3: Place solution step by step
        self.play(Transform(step_text, Text("Step 3: Solve using logical deduction", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # Sort solution by some logical order (you might want to adjust this)
        solution_order = []
        
        # First, place single-cell cages (fixed values)
        for cage in cages:
            if len(cage['cells']) == 1:
                row, col = cage['cells'][0]
                if (row, col) in self.solution_data:
                    solution_order.append((row, col))
        
        # Then place other cells
        for (row, col), value in self.solution_data.items():
            if (row, col) not in solution_order:
                solution_order.append((row, col))
        
        explanation_text = Text("", font_size=18, color=YELLOW)
        explanation_text.to_edge(LEFT, buff=0.5)
        
        for i, (row, col) in enumerate(solution_order):
            if (row, col) not in self.solution_data:
                continue
                
            value = self.solution_data[(row, col)]
            
            # Highlight the cell being filled
            highlight = Rectangle(
                width=cell_size * 0.9,
                height=cell_size * 0.9,
                fill_color=YELLOW,
                fill_opacity=0.5,
                stroke_color=YELLOW,
                stroke_width=3
            ).move_to(get_cell_center(row, col))
            
            self.play(Create(highlight))
            
            # Find which cage this cell belongs to
            cage_info = ""
            for cage in cages:
                if (row, col) in cage['cells']:
                    cage_info = f"Cage: {cage['operation']}"
                    break
            
            # Show explanation
            explanation = f"Cell ({row},{col}) = {value}. {cage_info}"
            self.play(Transform(explanation_text, Text(explanation, font_size=18, color=YELLOW).to_edge(LEFT, buff=0.5)))
            
            # Place the number
            num_text = Text(str(value), font_size=36, color=BLACK, weight=BOLD)
            num_text.move_to(get_cell_center(row, col))
            self.play(Write(num_text))
            cell_numbers[(row, col)] = num_text
            
            self.play(FadeOut(highlight))
            self.wait(0.3)
        
        # Step 4: Verification
        self.play(Transform(step_text, Text("Step 4: Verify solution", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        self.play(FadeOut(explanation_text))
        
        # Check rows
        self.play(Transform(step_text, Text(f"Checking rows: each contains {numbers_str}", font_size=24, color=GREEN).to_edge(DOWN, buff=0.5)))
        
        for row in range(grid_size):
            row_highlight = Rectangle(
                width=cell_size * grid_size,
                height=cell_size * 0.3,
                fill_color=GREEN,
                fill_opacity=0.3,
                stroke_color=GREEN,
                stroke_width=2
            ).move_to([0, grid_offset - row * cell_size - cell_size/2, 0])
            
            self.play(Create(row_highlight))
            self.wait(0.5)
            self.play(FadeOut(row_highlight))
        
        # Check columns
        self.play(Transform(step_text, Text(f"Checking columns: each contains {numbers_str}", font_size=24, color=GREEN).to_edge(DOWN, buff=0.5)))
        
        for col in range(grid_size):
            col_highlight = Rectangle(
                width=cell_size * 0.3,
                height=cell_size * grid_size,
                fill_color=GREEN,
                fill_opacity=0.3,
                stroke_color=GREEN,
                stroke_width=2
            ).move_to([col * cell_size - grid_offset + cell_size/2, 0, 0])
            
            self.play(Create(col_highlight))
            self.wait(0.5)
            self.play(FadeOut(col_highlight))
        
        # Check cages
        self.play(Transform(step_text, Text("Checking cages: all operations satisfied", font_size=24, color=GREEN).to_edge(DOWN, buff=0.5)))
        
        for cage in cage_groups:
            self.play(Indicate(cage, color=GREEN))
            self.wait(0.3)
        
        # Final celebration
        self.play(Transform(step_text, Text("✓ PUZZLE SOLVED! ✓", font_size=32, color=GOLD).to_edge(DOWN, buff=0.5)))
        
        # Add some celebratory effects
        for row in range(grid_size):
            for col in range(grid_size):
                if cell_numbers[(row, col)]:
                    self.play(
                        cell_numbers[(row, col)].animate.scale(1.2).set_color(GOLD),
                        run_time=0.1
                    )
                    self.play(
                        cell_numbers[(row, col)].animate.scale(1/1.2).set_color(BLACK),
                        run_time=0.1
                    )
        
        self.wait(2)
        
        # Show final solution grid
        final_text = Text("Final Solution:", font_size=28, color=BLUE)
        final_text.to_edge(DOWN, buff=1.5)
        
        # Build solution grid string
        solution_grid_str = ""
        for row in range(grid_size):
            row_str = ""
            for col in range(grid_size):
                if (row, col) in self.solution_data:
                    row_str += str(self.solution_data[(row, col)]) + " "
                else:
                    row_str += "? "
            solution_grid_str += row_str.strip() + "\n"
        
        solution_grid = Text(
            solution_grid_str.strip(),
            font_size=24,
            color=WHITE,
            font="monospace"
        )
        solution_grid.next_to(final_text, DOWN)
        
        self.play(Write(final_text))
        self.play(Write(solution_grid))
        
        self.wait(3)


# Command line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate KenKen puzzle solution animation")
    parser.add_argument("input_file", help="Path to the input puzzle file")
    parser.add_argument("--output", "-o", help="Output file name (without extension)")
    parser.add_argument("--quality", "-q", choices=["low", "medium", "high"], 
                       default="medium", help="Video quality")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found!")
        sys.exit(1)
    
    # Create scene with input file
    scene = KenKenInputSolver(input_file=args.input_file)
    
    print(f"Generating animation for puzzle: {args.input_file}")
    print("This may take a few minutes...")
    
    # You would typically run this with manim command line:
    # manim kenken_input_solver.py KenKenInputSolver -p --input_file your_puzzle.txt
from manim import *
import argparse
import math
import sys
import os
import re

class MyText(Text):
    def __init__(self, text, **kwargs):
        kwargs.setdefault('font', 'sans-serif')
        super().__init__(text, **kwargs)


class KenKenGenerator(Scene):
    def __init__(self, input_file=None, **kwargs):
        super().__init__(**kwargs)
        self.input_file = input_file or "descriptors/8x8_puzzle_CLEAN.txt"
        self.puzzle_data = None
        self.solution_data = None
        self.solving_steps = []
        
    def parse_input_file(self):
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
            solving_steps = []
            solution_lines = solution_part.split('\n')
            
            for line in solution_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Parse different types of solving steps
                if line.startswith('The cage covering'):
                    # Cage analysis step
                    solving_steps.append({
                        'type': 'cage_analysis',
                        'description': line,
                        'cells': self.extract_cells_from_description(line)
                    })
                elif line.startswith('Valid combos:'):
                    # Add combos to the last cage analysis
                    if solving_steps and solving_steps[-1]['type'] == 'cage_analysis':
                        solving_steps[-1]['combos'] = line.split('Valid combos: ')[1]
                elif line.startswith('Perm-prune'):
                    # Constraint propagation step
                    solving_steps.append({
                        'type': 'constraint_propagation', 
                        'description': line,
                        'cell': self.extract_cell_from_pruning(line),
                        'old_values': self.extract_old_values_from_pruning(line),
                        'new_values': self.extract_new_values_from_pruning(line)
                    })
                elif line.startswith('Pruned'):
                    # Pruning step using "parse_line_regex"
                    cell, old_values, new_values = self.parse_line_regex(line)
                    solving_steps.append({
                        'type': 'constraint_propagation',
                        'description': line,
                        'cell': cell,
                        'old_values': old_values,
                        'new_values': new_values
                    })
                elif line.startswith('Cage-line elim:'):
                    # Cage-line elimination step
                    solving_steps.append({
                        'type': 'cage_line_elimination',
                        'description': line,
                        'cell': self.extract_cell_from_elimination(line),
                        'value_removed': self.extract_removed_value(line)
                    })
                elif line.startswith('Cage-single-combo:'):
                    # Final assignment step
                    cell_match = re.search(r'Cell \((\d+),(\d+)\) = (\d+)', line)
                    if cell_match:
                        row, col, value = int(cell_match.group(1)), int(cell_match.group(2)), int(cell_match.group(3))
                        solving_steps.append({
                            'type': 'assignment',
                            'description': line,
                            'cell': (row, col),
                            'value': value
                        })
                elif line.startswith('Peer elim:'):
                    # Peer elimination step
                    cell_match = re.search(r'remove (\d+) from \((\d+), (\d+)\)', line)
                    if cell_match:
                        value, row, col = int(cell_match.group(1)), int(cell_match.group(2)), int(cell_match.group(3))
                        solving_steps.append({
                            'type': 'cage_line_elimination',
                            'description': line,
                            'cell': (row, col),
                            'value_removed': value
                        })
                elif line.startswith('Naked single:'):
                    # Naked single assignment step
                    cell_match = re.search(r'Cell \((\d+),(\d+)\) = (\d+)', line)
                    if cell_match:
                        row, col, value = int(cell_match.group(1)), int(cell_match.group(2)), int(cell_match.group(3))
                        solving_steps.append({
                            'type': 'assignment',
                            'description': line,
                            'cell': (row, col),
                            'value': value
                        })
                # another line example: "Updated combos for 'The cage covering (0,5), (0,6) must have a product of 14.': [(7, 2)]"
                elif line.startswith('Updated combos for'):
                    # Update combos for a cage
                    cage_desc = line.split('for ')[1].split(':')[0].strip()
                    combos_str = line.split(': ')[1].strip()
                    if solving_steps and solving_steps[-1]['type'] == 'cage_analysis':
                        solving_steps[-1]['combos'] = combos_str
                elif line.startswith('Solution:'):
                    # Parse final solution
                    solution_str = line.split('Solution:')[1].strip()
                    solution_str = solution_str.strip()[1:-1]  # Remove { }
                    pattern = r'\(\s*(\d+)\s*,\s*(\d+)\s*\):\s*(\d+)'
                    solution = {
                        (int(row), int(col)): int(val)
                        for row, col, val in re.findall(pattern, solution_str)
                    }
            
            self.puzzle_data = {
                'info': puzzle_info,
                'cages': cages
            }
            self.solution_data = solution
            self.solving_steps = solving_steps
            
        except Exception as e:
            print(f"Error parsing input file: {e}")
            sys.exit(1)
    
    def extract_cells_from_description(self, description):
        """Extract cell coordinates from cage description"""
        pattern = r'\((\d+),(\d+)\)'
        matches = re.findall(pattern, description)
        return [(int(row), int(col)) for row, col in matches]
    
    def extract_cell_from_pruning(self, line):
        """Extract cell from pruning line"""
        match = re.search(r'\((\d+), (\d+)\)', line)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None
    
    def extract_old_values_from_pruning(self, line):
        """Extract old possible values from pruning line"""
        match = re.search(r'\[([0-9, ]+)\]→', line)
        if match:
            return [int(x.strip()) for x in match.group(1).split(',')]
        return []
    
    def extract_new_values_from_pruning(self, line):
        """Extract new possible values from pruning line"""
        match = re.search(r'→\[([0-9, ]+)\]', line)
        if match:
            return [int(x.strip()) for x in match.group(1).split(',')]
        return []
    
    def parse_line_regex(self, line):
        match = re.search(r'\((\d+), (\d+)\): \[(.*?)\]→\[(.*?)\]', line)
        if match:
            x, y = int(match.group(1)), int(match.group(2))
            old_vals = list(map(int, match.group(3).split(', ')))
            new_vals = list(map(int, match.group(4).split(', ')))
            return (x, y), old_vals, new_vals

    def extract_cell_from_elimination(self, line):
        """Extract cell from elimination line"""
        match = re.search(r'from \((\d+),(\d+)\)', line)
        if match:
            return (int(match.group(1)), int(match.group(2)))
        return None
    
    def extract_removed_value(self, line):
        """Extract removed value from elimination line"""
        match = re.search(r'remove (\d+)', line)
        if match:
            return int(match.group(1))
        return None
    
    def assign_cage_colors(self):
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
            error_text = MyText("Failed to parse input file!", font_size=36, color=RED)
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
        # Title
        # Title
        title = MyText(f"KenKen Puzzle {grid_size}×{grid_size} - Logical Solution Process", 
                        font_size=36, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Grid parameters
        # cell_size = 1.0
        cell_size = (0.4 + 2.4 / grid_size)
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
        
        # Position grid slightly to the right to make room for explanations
        #grid.shift(RIGHT * 2)
        self.play(Create(grid))
        
        # Helper function to get cell center position
        def get_cell_center(row, col):
            x = col * cell_size - grid_offset + cell_size/2  # +2 for grid shift
            y = grid_offset - row * cell_size - cell_size/2
            return [x, y, 0]
        
            
        def format_possibilities(values, max_per_line=3):
            """Format possibilities with line breaks to fit in cell."""
            if not values:
                return ""
            
            possibilities = list(map(str, values))
            lines = []
            
            # Group by max_per_line
            for i in range(0, len(possibilities), max_per_line):
                line_values = possibilities[i:i+max_per_line]
                lines.append(",".join(line_values))
            
            return "\n".join(lines)
        
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
                anchor_center[0] - cell_size/2 + 0.05 + len(cage["operation"]) * 0.05,
                anchor_center[1] + cell_size/2 - 0.15,
                0
            ]
            
            operation_label = MyText(
                cage["operation"],
                font_size = math.ceil(13 * cell_size),
                color=WHITE
            ).move_to(label_pos)
            
            cage_group.add(operation_label)
            cage_groups.add(cage_group)
        
        self.play(Create(cage_groups))
        
        # Show available numbers
        # Smooth transition to subtitle
        numbers_str = ", ".join(map(str, allowed_numbers))
        available = MyText(f"Available numbers: {numbers_str}", font_size=18, color=YELLOW)
        available.to_edge(UP)
        self.play(FadeOut(title), Write(available))
        
        
        # # Create explanation area on the left
        # explanation_box = Rectangle(
        #     #width=5, height=3.5,
        #     fill_color=BLACK, fill_opacity=0.8,
        #     stroke_color=WHITE, stroke_width=2
        # ).to_edge(DOWN, buff=0.5).shift(UP * 0.5)

        # #self.play(Transform(step_text, MyText("Step 4: Verify solution", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # explanation_title = MyText("Solving Process:", font_size=20, color=YELLOW)
        # explanation_title.next_to(explanation_box, UP, buff=0.1)
        
        # self.play(Create(explanation_box), Write(explanation_title))
        
        # Track cell possibilities and values
        cell_possibilities = {}
        cell_values = {}
        possibility_texts = {}
        
        # Initialize possibilities
        for row in range(grid_size):
            for col in range(grid_size):
                cell_possibilities[(row, col)] = allowed_numbers.copy()
                cell_values[(row, col)] = None
        
        # Process solving steps
        step_counter = 1
        
        for step in self.solving_steps:
            if step['type'] == 'cage_analysis':
                continue  # Skip cage analysis for now
                # Show cage analysis
                explanation_text = f"Step {step_counter}: Analyzing cage\n"
                if 'combos' in step:
                    explanation_text += f"Valid combinations:\n{step['combos'][:50]}..."
                else:
                    explanation_text += step['description'][:60] + "..."
                
                exp_obj = MyText(
                    explanation_text,
                    font_size=14,
                    color=WHITE
                ).to_edge(DOWN, buff=0.5)
                
                self.play(Write(exp_obj))
                
                # Highlight the relevant cage
                if 'cells' in step and step['cells']:
                    for cage_group in cage_groups:
                        # Check if this cage group matches the cells
                        self.play(Indicate(cage_group, color=WHITE))
                        break
                
                #self.wait(1.5)
                self.play(FadeOut(exp_obj))
                step_counter += 1
            
            elif step['type'] == 'constraint_propagation':
                # Show constraint propagation
                cell = step['cell']
                if cell:
                    explanation_text = f"Step {step_counter}: Constraint Propagation\n"
                    explanation_text += f"Cell ({cell[0]},{cell[1]}): "
                    explanation_text += f"{step['old_values']} → {step['new_values']}"
                    
                    exp_obj = MyText(
                        explanation_text,
                        font_size=14,
                        color=ORANGE
                    ).to_edge(DOWN, buff=0.5)
                    
                    self.play(Write(exp_obj))
                    
                    # Highlight the cell
                    highlight = Rectangle(
                        width=cell_size * 0.9,
                        height=cell_size * 0.9,
                        fill_color=ORANGE,
                        fill_opacity=0.5,
                        stroke_color=ORANGE,
                        stroke_width=3
                    ).move_to(get_cell_center(cell[0], cell[1]))
                    
                    self.play(Create(highlight))
                    
                    # Update cell possibilities
                    cell_possibilities[cell] = step['new_values']

                    # Show possibilities in cell
                    if not cell_values[cell]:
                        poss_str = format_possibilities(step['new_values'], max_per_line=3)
                        
                        poss_text = MyText(
                            poss_str,
                            font_size=10 * cell_size,
                            color=GRAY,
                            line_spacing=0.8  # Adjust line spacing
                        ).move_to(get_cell_center(cell[0], cell[1]))
                        
                        if cell in possibility_texts:
                            self.play(Transform(possibility_texts[cell], poss_text))
                        else:
                            self.play(Write(poss_text))
                            possibility_texts[cell] = poss_text
                    # # Show possibilities in cell
                    # #if len(step['new_values']) <= 3 and not cell_values[cell]:
                    # if not cell_values[cell]:
                    #     poss_str = ",".join(map(str, step['new_values']))
                    #     poss_text = MyText(
                    #         poss_str,
                    #         font_size=10 * cell_size,
                    #         color=GRAY
                    #     ).move_to(get_cell_center(cell[0], cell[1]))
                        
                    #     if cell in possibility_texts:
                    #         self.play(Transform(possibility_texts[cell], poss_text))
                    #     else:
                    #         self.play(Write(poss_text))
                    #         possibility_texts[cell] = poss_text
                    
                    self.wait(1)
                    self.play(FadeOut(highlight), FadeOut(exp_obj))
                    step_counter += 1
            
            elif step['type'] == 'cage_line_elimination':
                # Show cage-line elimination
                cell = step['cell']
                value = step['value_removed']
                if cell and value:
                    explanation_text = f"Step {step_counter}: Cage-Line Elimination\n"
                    explanation_text += f"Remove {value} from ({cell[0]},{cell[1]})"
                    
                    exp_obj = MyText(
                        explanation_text,
                        font_size=14,
                        color=RED
                    ).to_edge(DOWN, buff=0.5)
                    
                    self.play(Write(exp_obj))
                    
                    # Highlight the cell
                    highlight = Rectangle(
                        width=cell_size * 0.9,
                        height=cell_size * 0.9,
                        fill_color=RED,
                        fill_opacity=0.3,
                        stroke_color=RED,
                        stroke_width=3
                    ).move_to(get_cell_center(cell[0], cell[1]))
                    
                    self.play(Create(highlight))
                    
                    # Update possibilities
                    if value in cell_possibilities[cell]:
                        cell_possibilities[cell].remove(value)

                    if not cell_values[cell]:
                        poss_str = format_possibilities(cell_possibilities[cell])
                        print(f"Possibilities for cell {cell}: {poss_str}")
                        poss_text = MyText(
                            poss_str,
                            font_size=10 * cell_size,
                            color=GRAY
                        ).move_to(get_cell_center(cell[0], cell[1]))
                        
                        if cell in possibility_texts:
                            self.play(Transform(possibility_texts[cell], poss_text))
                        else:
                            self.play(Write(poss_text))
                            possibility_texts[cell] = poss_text
                    
                    
                    self.wait(1)
                    self.play(FadeOut(highlight), FadeOut(exp_obj))
                    step_counter += 1
            
            elif step['type'] == 'assignment':
                # Show final assignment
                cell = step['cell']
                value = step['value']
                
                explanation_text = f"Step {step_counter}: Assignment\n"
                explanation_text += f"Cell ({cell[0]},{cell[1]}) = {value}"
                
                exp_obj = MyText(
                    explanation_text,
                    font_size=14,
                    color=GREEN
                ).to_edge(DOWN, buff=0.5)
                
                self.play(Write(exp_obj))
                
                # Highlight the cell
                highlight = Rectangle(
                    width=cell_size * 0.9,
                    height=cell_size * 0.9,
                    fill_color=GREEN,
                    fill_opacity=0.5,
                    stroke_color=GREEN,
                    stroke_width=3
                ).move_to(get_cell_center(cell[0], cell[1]))
                
                self.play(Create(highlight))
                
                # Remove possibility text if present
                if cell in possibility_texts:
                    self.play(FadeOut(possibility_texts[cell]))
                    del possibility_texts[cell]
                
                # Place the number
                num_text = MyText(str(value), font_size=28, color=WHITE, weight=BOLD)
                num_text.move_to(get_cell_center(cell[0], cell[1]))
                self.play(Write(num_text))
                cell_values[cell] = num_text
                
                self.play(FadeOut(highlight))
                self.wait(0.5)
                self.play(FadeOut(exp_obj))
                step_counter += 1
        
        # Final celebration
        final_text = MyText("Puzzle Solved!", font_size=32, color=GOLD)
        final_text.to_edge(DOWN, buff=0.5)
        
        self.play(Write(final_text))
        
        # for x in self.solution_data.keys():
        #     row, col = x
        #     value = self.solution_data[(row, col)]
        #     cell_center = get_cell_center(row, col)
            
        #     # Create a number text for the solution
        #     num_text = MyText(str(value), font_size=28, color=WHITE, weight=BOLD)
        #     num_text.move_to(cell_center)
            
        #     # If the cell already has a value, update it
        #     if (row, col) in cell_values:
        #         self.play(Transform(cell_values[(row, col)], num_text))
        #     else:
        #         self.play(Write(num_text))
        #         cell_values[(row, col)] = num_text

        # Celebratory effects
        for cell, num_text in cell_values.items():
            get_cell_center(row, col)
            if num_text:
                self.play(
                    num_text.animate.scale(1.3).set_color(GOLD),
                    run_time=0.1
                )
                self.play(
                    num_text.animate.scale(1/1.3).set_color(WHITE),
                    run_time=0.1
                )
        
        self.wait(3)

# Command line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate enhanced KenKen puzzle solution animation")
    parser.add_argument("input_file", help="Path to the input puzzle file")
    parser.add_argument("--output", "-o", help="Output file name (without extension)")
    parser.add_argument("--quality", "-q", choices=["low", "medium", "high"], 
                       default="medium", help="Video quality")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found!")
        sys.exit(1)
    
    # Create scene with input file
    scene = KenKenGenerator(input_file=args.input_file)
    
    print(f"Generating enhanced animation for puzzle: {args.input_file}")
    print("This may take a few minutes...")
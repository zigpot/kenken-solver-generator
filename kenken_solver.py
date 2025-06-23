from manim import *
import numpy as np

class KenKenSolution(Scene):
    def construct(self):
        # Title
        title = Text("KenKen Puzzle - Step by Step Solution", font_size=40, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Grid parameters
        grid_size = 4
        cell_size = 1.0
        
        # Create the main grid
        grid = VGroup()
        for i in range(grid_size + 1):
            # Vertical lines
            line = Line(
                start=[i * cell_size - 2, 2, 0],
                end=[i * cell_size - 2, -2, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)
            
            # Horizontal lines
            line = Line(
                start=[-2, 2 - i * cell_size, 0],
                end=[2, 2 - i * cell_size, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)
        
        self.play(Create(grid))
        
        # Define cage data
        cages = [
            {"cells": [(0,0), (0,1)], "operation": "32×", "color": RED},
            {"cells": [(0,2), (1,2)], "operation": "10+", "color": YELLOW},
            {"cells": [(0,3), (1,3)], "operation": "5−", "color": GREEN},
            {"cells": [(1,0), (2,0)], "operation": "16×", "color": ORANGE},
            {"cells": [(1,1), (2,1), (3,1)], "operation": "15+", "color": PURPLE},
            {"cells": [(2,2), (2,3), (3,2)], "operation": "72×", "color": PINK},
            {"cells": [(3,0)], "operation": "9", "color": BLUE_A},
            {"cells": [(3,3)], "operation": "8", "color": GREEN_A}
        ]
        
        # Helper function to get cell center position
        def get_cell_center(row, col):
            x = col * cell_size - 2 + cell_size/2
            y = 2 - row * cell_size - cell_size/2
            return [x, y, 0]
        
        # Create cage backgrounds and labels
        cage_groups = VGroup()
        
        for i, cage in enumerate(cages):
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
            
            # Add operation label to the first cell (anchor)
            anchor_row, anchor_col = cage["cells"][0]
            anchor_center = get_cell_center(anchor_row, anchor_col)
            
            # Position label in top-left corner
            label_pos = [
                anchor_center[0] - cell_size/2 + 0.1 + len(cage["operation"]) * 0.05, #move slightly right based on text length
                anchor_center[1] + cell_size/2 - 0.2, #move slightly down
                0
            ]
            
            operation_label = Text(
                cage["operation"],
                font_size=13,
                color=WHITE#,weight=BOLD
            ).move_to(label_pos)
            
            cage_group.add(operation_label)
            cage_groups.add(cage_group)
        
        self.play(Create(cage_groups))
        
        # Create number tracking for each cell
        cell_numbers = {}
        cell_possibilities = {}
        
        # Initialize with empty possibilities
        for row in range(4):
            for col in range(4):
                cell_numbers[(row, col)] = None
                cell_possibilities[(row, col)] = VGroup()
        
        # Step 1: Show initial setup
        step_text = Text("Step 1: Analyze cage constraints", font_size=24, color=WHITE)
        step_text.to_edge(DOWN, buff=0.5)
        self.play(Write(step_text))
        
        # Show available numbers
        available = Text("Available numbers: 2, 4, 8, 9", font_size=20, color=YELLOW)
        available.next_to(title, DOWN)
        self.play(Write(available))
        
        self.wait(2)
        
        # Step 2: Show cage analysis
        self.play(Transform(step_text, Text("Step 2: Find valid combinations for each cage", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # Highlight and explain each cage
        cage_explanations = [
            "32× with 2 cells: (4,8) or (8,4)",
            "10+ with 2 cells: (2,8) or (8,2)", 
            "5− with 2 cells: (4,9) or (9,4)",
            "16× with 2 cells: (2,8) or (8,2)",
            "15+ with 3 cells: various combinations",
            "72× with 3 cells: various combinations",
            "Fixed value: 9",
            "Fixed value: 8"
        ]
        
        for i, (cage, explanation) in enumerate(zip(cage_groups, cage_explanations)):
            self.play(Indicate(cage, color=WHITE))
            exp_text = Text(explanation, font_size=18, color=WHITE)
            exp_text.to_edge(LEFT, buff=0.5)
            self.play(Write(exp_text))
            self.wait(1)
            self.play(FadeOut(exp_text))
        
        # Step 3: Place fixed values first
        self.play(Transform(step_text, Text("Step 3: Place fixed values", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # Place 9 at (3,0)
        nine_text = Text("9", font_size=36, color=BLACK, weight=BOLD)
        nine_text.move_to(get_cell_center(3, 0))
        self.play(Write(nine_text))
        cell_numbers[(3, 0)] = nine_text
        
        # Place 8 at (3,3)
        eight_text = Text("8", font_size=36, color=BLACK, weight=BOLD)
        eight_text.move_to(get_cell_center(3, 3))
        self.play(Write(eight_text))
        cell_numbers[(3, 3)] = eight_text
        
        self.wait(1)
        
        # Step 4: Logical deduction
        self.play(Transform(step_text, Text("Step 4: Apply logical constraints", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        
        # Show the solving process step by step
        solution_steps = [
            # Based on the log, showing key deductions
            ((0, 0), "4", "32× cage: must be 4×8"),
            ((0, 1), "8", "32× cage: must be 4×8"),
            ((0, 2), "2", "10+ cage: must be 2+8"),
            ((1, 2), "8", "10+ cage: must be 2+8"),
            ((0, 3), "9", "5− cage: must be 9−4"),
            ((1, 3), "4", "5− cage: must be 9−4"),
            ((1, 0), "2", "16× cage: must be 2×8"),
            ((2, 0), "8", "16× cage: must be 2×8"),
            ((1, 1), "9", "Deduced from constraints"),
            ((2, 1), "4", "15+ cage constraint"),
            ((3, 1), "2", "15+ cage constraint"),
            ((2, 2), "9", "72× cage constraint"),
            ((2, 3), "2", "72× cage constraint"),
            ((3, 2), "4", "72× cage constraint")
        ]
        
        explanation_text = Text("", font_size=18, color=YELLOW)
        explanation_text.to_edge(LEFT, buff=0.5)
        
        for (row, col), number, explanation in solution_steps:
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
            
            # Show explanation
            self.play(Transform(explanation_text, Text(explanation, font_size=18, color=YELLOW).to_edge(LEFT, buff=0.5)))
            
            # Place the number
            num_text = Text(number, font_size=36, color=BLACK, weight=BOLD)
            num_text.move_to(get_cell_center(row, col))
            self.play(Write(num_text))
            cell_numbers[(row, col)] = num_text
            
            self.play(FadeOut(highlight))
            self.wait(0.5)
        
        # Step 5: Verification
        self.play(Transform(step_text, Text("Step 5: Verify solution", font_size=24, color=WHITE).to_edge(DOWN, buff=0.5)))
        self.play(FadeOut(explanation_text))
        
        # Check rows
        self.play(Transform(step_text, Text("Checking rows: each contains 2, 4, 8, 9", font_size=24, color=GREEN).to_edge(DOWN, buff=0.5)))
        
        for row in range(4):
            row_highlight = Rectangle(
                width=cell_size * 4,
                height=cell_size * 0.3,
                fill_color=GREEN,
                fill_opacity=0.3,
                stroke_color=GREEN,
                stroke_width=2
            ).move_to([0, 2 - row * cell_size - cell_size/2, 0])
            
            self.play(Create(row_highlight))
            self.wait(0.5)
            self.play(FadeOut(row_highlight))
        
        # Check columns
        self.play(Transform(step_text, Text("Checking columns: each contains 2, 4, 8, 9", font_size=24, color=GREEN).to_edge(DOWN, buff=0.5)))
        
        for col in range(4):
            col_highlight = Rectangle(
                width=cell_size * 0.3,
                height=cell_size * 4,
                fill_color=GREEN,
                fill_opacity=0.3,
                stroke_color=GREEN,
                stroke_width=2
            ).move_to([col * cell_size - 2 + cell_size/2, 0, 0])
            
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
        for row in range(4):
            for col in range(4):
                if cell_numbers[(row, col)]:
                    self.play(
                        cell_numbers[(row, col)].animate.scale(1.2).set_color(GOLD),
                        run_time=0.1
                    )
                    self.play(
                        cell_numbers[(row, col)].animate.scale(1/1.2).set_color(BLACK),
                        run_time=0.1
                    )
        
        self.wait(3)
        
        # Show final solution clearly
        final_text = Text("Final Solution:", font_size=28, color=BLUE)
        final_text.to_edge(DOWN, buff=1.5)
        solution_grid = Text(
            "4 8 2 9\n2 9 8 4\n8 4 9 2\n9 2 4 8",
            font_size=24,
            color=WHITE,
            font="monospace"
        )
        solution_grid.next_to(final_text, DOWN)
        
        self.play(Write(final_text))
        self.play(Write(solution_grid))
        
        self.wait(4)
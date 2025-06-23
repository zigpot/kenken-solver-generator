from manim import *
import numpy as np

class KenKenPuzzle(Scene):
    def construct(self):
        # Title
        title = Text("KenKen Puzzle", font_size=48, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))
        
        # Grid parameters
        grid_size = 4
        cell_size = 1.2
        
        # Create the main grid
        grid = VGroup()
        for i in range(grid_size + 1):
            # Vertical lines
            line = Line(
                start=[i * cell_size - 2.4, 2.4, 0],
                end=[i * cell_size - 2.4, -2.4, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)
            
            # Horizontal lines
            line = Line(
                start=[-2.4, 2.4 - i * cell_size, 0],
                end=[2.4, 2.4 - i * cell_size, 0],
                color=BLACK,
                stroke_width=3
            )
            grid.add(line)
        
        self.play(Create(grid))
        
        # Define cage data based on the puzzle
        cages = [
            {"cells": [(0,0), (0,1)], "operation": "32×", "color": RED},
            {"cells": [(0,2), (1,2)], "operation": "10+", "color": YELLOW},
            {"cells": [(0,3), (1,3)], "operation": "5−", "color": GREEN},
            {"cells": [(1,0), (2,0)], "operation": "16×", "color": ORANGE},
            {"cells": [(1,1), (2,1), (3,1)], "operation": "15+", "color": PURPLE},
            {"cells": [(2,2), (2,3), (3,2)], "operation": "72×", "color": PINK},
            #{"cells": [(3,0)], "operation": "9", "color": LIGHT_BLUE_},
            #{"cells": [(3,3)], "operation": "8", "color": LIGHT_GREEN},
            {"cells": [(3,0)], "operation": "9", "color": BLUE_A},
            {"cells": [(3,3)], "operation": "8", "color": GREEN_A}
        ]
        
        # Helper function to get cell center position
        def get_cell_center(row, col):
            x = col * cell_size - 2.4 + cell_size/2
            y = 2.4 - row * cell_size - cell_size/2
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
                    fill_opacity=0.3,
                    stroke_color=cage["color"],
                    stroke_width=3
                ).move_to(center)
                cage_group.add(rect)
            
            # Add operation label to the first cell (anchor)
            anchor_row, anchor_col = cage["cells"][0]
            anchor_center = get_cell_center(anchor_row, anchor_col)
            
            # Position label in top-left corner of the anchor cell
            label_pos = [
                anchor_center[0] - cell_size/2 + 0.2 + len(cage["operation"]) * 0.05, #move slightly right based on text length
                anchor_center[1] + cell_size/2 - 0.3, #move slightly down
                0
            ]
            
            operation_label = Text(
                cage["operation"],
                font_size=15,
                color=WHITE,
                weight=NORMAL
            ).move_to(label_pos)
            
            cage_group.add(operation_label)
            cage_groups.add(cage_group)
        
        # Animate cage creation
        self.play(
            *[Create(cage_group) for cage_group in cage_groups],
            run_time=2
        )
        
        # Add instructions
        instructions = VGroup(
            Text("Fill each row and column with: 2, 4, 8, 9", font_size=24),
            Text("Each cage must satisfy its operation", font_size=24),
            Text("No repeated numbers in any row or column", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT)
        instructions.to_edge(DOWN, buff=0.5)
        
        self.play(Write(instructions))
        
        # Add some visual flair - highlight each cage type
        self.wait(1)
        
        # Group cages by operation type
        multiply_cages = [cage_groups[i] for i in [0, 3, 5]]  # 32×, 16×, 72×
        add_cages = [cage_groups[i] for i in [1, 4]]  # 10+, 15+
        subtract_cages = [cage_groups[i] for i in [2]]  # 5−
        single_cages = [cage_groups[i] for i in [6, 7]]  # 9, 8
        
        # Highlight multiplication cages
        mult_label = Text("Multiplication Cages", font_size=32, color=RED)
        mult_label.to_edge(LEFT, buff=1)
        self.play(Write(mult_label))
        self.play(*[Indicate(cage, color=RED) for cage in multiply_cages])
        self.play(FadeOut(mult_label))
        
        # Highlight addition cages
        add_label = Text("Addition Cages", font_size=32, color=YELLOW)
        add_label.to_edge(LEFT, buff=1)
        self.play(Write(add_label))
        self.play(*[Indicate(cage, color=YELLOW) for cage in add_cages])
        self.play(FadeOut(add_label))
        
        # Highlight subtraction cage
        sub_label = Text("Subtraction Cage", font_size=32, color=GREEN)
        sub_label.to_edge(LEFT, buff=1)
        self.play(Write(sub_label))
        self.play(Indicate(subtract_cages[0], color=GREEN))
        self.play(FadeOut(sub_label))
        
        # Highlight single number cages
        single_label = Text("Fixed Values", font_size=32, color=BLUE)
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
        end_text = Text("Solve the KenKen Puzzle!", font_size=48, color=GOLD)
        self.play(Write(end_text))
        self.wait(2)

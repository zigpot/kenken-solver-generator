# Todos

| No. |                                                           Task                                                           |        |
|:---:|:------------------------------------------------------------------------------------------------------------------------:|:------:|
|   1 | Modularize construct() into smaller functions                                                                            | High   |
|   2 | Improve input parsing robustness                                                                                         | High   |
|   3 | Fix __init__() override so CLI input_file is used                                                                        | High   |
|   4 | Validate descriptor data (cages, solution, allowed numbers)                                                              | High   |
|   5 | Add real cage verification logic                                                                                         | High   |
|   6 | Remove ineffective scene creation in __main__                                                                            | High   |
|   7 | Remove commented-out and debug code                                                                                      | High   |
|   8 | Modularize `construct()` into smaller functions like `render_grid()`, `render_cages()`, `animate_solution()`, etc.       | High   |
|   9 | Improve input parsing robustness (e.g., avoid fragile `split("Hello! Starting KenKen solver.")`).                        | High   |
|  10 | Fix `__init__()` override so CLI-provided `input_file` is not ignored.                                                   | High   |
|  11 | Validate descriptor data: ensure cages cover all cells, solution is complete, and `allowed_numbers` matches puzzle size. | High   |
|  12 | Add real cage verification logic instead of just visual animation.                                                       | High   |
|  13 | Remove ineffective scene creation in `__main__` — Manim doesn’t execute that code path.                                  | High   |
|  14 | Remove commented-out and debug code to clean up the source.                                                              | High   |
|  15 | Separate logic and animation                                                                                             | Medium |
|  16 | Use animation utilities (Succession, etc.)                                                                               | Medium |
|  17 | Parameterize animation durations                                                                                         | Medium |
|  18 | Extract reusable animation helpers (e.g. highlight_cell())                                                               | Medium |
|  19 | Add CLI options (--only-puzzle, --skip-verification)                                                                     | Medium |
|  20 | Use logging instead of print()                                                                                           | Medium |
|  21 | Replace magic numbers with named constants                                                                               | Medium |
|  22 | Extract and test parsing logic in isolation                                                                              | Medium |
|  23 | Auto-scale grid/cell size based on puzzle dimension                                                                      | Medium |
|  24 | Separate logic and animation to improve testability and reuse.                                                           | Medium |
|  25 | Use animation utilities like `Succession`, `LaggedStart`, or `AnimationGroup` to reduce repetitive `play()` calls.       | Medium |
|  26 | Parameterize durations like `wait(2)` instead of hardcoding.                                                             | Medium |
|  27 | Extract reusable animation helpers, e.g., `highlight_cell()`.                                                            | Medium |
|  28 | Add CLI options like `--only-puzzle`, `--skip-verification`.                                                             | Medium |
|  29 | Use `logging` instead of `print()` for better diagnostics and log control.                                               | Medium |
|  30 | Replace magic numbers with named constants (e.g., font sizes, cell size).                                                | Medium |
|  31 | Extract and test parsing logic in isolation using `unittest` or `pytest`.                                                | Medium |
|  32 | Auto-scale the grid or cell size based on puzzle dimension to better fit the frame.                                      | Medium |
|  33 | Use consistent f-strings                                                                                                 | Low    |
|  34 | Add a visual legend or color key                                                                                         | Low    |
|  35 | Use consistent f-strings instead of old formatting or concatenation.                                                     | Low    |
|  36 | Add a visual legend or color key to explain cage highlights and operations.                                              | Low    |
# KenKen Puzzle Solver Animation

This project generates an animated, step-by-step video that visually explains how a KenKen puzzle is solved logically. It's powered by [Manim](https://docs.manim.community/) for beautiful math-based animations.

## 📂 Features

- Parses KenKen puzzle descriptors with solution logs
- Animates puzzle grid, cage constraints, and deduction steps
- Highlights constraint propagation and value assignments
- Outputs a high-quality educational video

## 🖥️ Requirements

- Python 3.8+
- [Manim Community Edition](https://docs.manim.community/)
- See `requirements.txt` for dependencies

Install with:

```bash
pip install -r requirements.txt
````

## 📄 Input Format

Place your puzzle descriptor `.txt` in `descriptors/`. It should contain:

* Puzzle size, allowed numbers
* Cage definitions
* Solver log with logical deduction steps

Example snippet:

```
size: 6
allowed_numbers: 1 2 3 4 5 6
hint,cells,anchor
6x,(0,0);(1,0),(0,0)
...
Hello! Starting KenKen solver.
The cage covering (0,0)... 
```

## ▶️ Usage

```bash
manim kenken_generator.py KenkenGenerator
```

Optional flags:

```bash
-p # play preview by the end of rendering
-qh # high quality (1080p)
-qm # medium quality (720p, default)
-ql # low quality (480p)
```

flags can be combined, e.g. `manim kenken_generator.py KenkenGenerator -pqh`

## 📦 Project Structure

```
kenken_solver/
├── kenken_generator.py       # main animation script
├── input_sanitizer.py        # optional input cleaning
├── descriptors/              # sample input files
├── output/                   # (ignored) video outputs
├── requirements.txt
├── pyproject.toml
├── README.md
└── TODOS.md
```

## 📹 Output

The result is a `.mp4` animation showing:

* Grid creation
* Cage constraint coloring
* Logical steps visualized
* Final solved grid

## 🛠️ TODO

See `TODOS.md` for future plans and features.

## 📝 License

MIT.

---

> Built with ❤️ using Python and Manim by Jimmy Keng and team


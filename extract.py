import argparse

parser = argparse.ArgumentParser(description="Extract KenKen puzzle header block.")
parser.add_argument("filename", help="Path to the input file")
args = parser.parse_args()

with open(args.filename, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Collect lines from "Puzzle 1:" until the first empty line
block_lines = []
in_block = False
for line in lines:
    if not in_block:
        if line.strip().startswith("Puzzle 1:"):
            in_block = True
            block_lines.append(line.rstrip())
    else:
        if line.strip() == "":
            break
        block_lines.append(line.rstrip())

default_content = "\n".join(block_lines)
print(default_content)


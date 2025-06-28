import re
import sys

def convert_coordinates_1_to_0(text):
    """Convert 1-based coordinates to 0-based coordinates in a string."""
    def replace_coord(match):
        x, y = int(match.group(1)), int(match.group(2))
        return f"({x-1},{y-1})"
    
    # Pattern to match coordinates like (1,2) or (10,5)
    coord_pattern = r'\((\d+),(\d+)\)'
    return re.sub(coord_pattern, replace_coord, text)

def fix_kenken_coordinates(input_text):
    """Fix coordinate indexing inconsistencies in KenKen puzzle descriptor."""
    lines = input_text.strip().split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        
        # Check if line starts with patterns that need coordinate conversion
        if (line.startswith('The cage covering') or 
            line.startswith('Cage-line elim:') or 
            line.startswith('Updated combos') or 
            line.startswith('Cage-single-combo') or
            line.startswith('Naked single') or
            line.startswith('Peer elim')):
            
            # Convert all coordinates in the line from 1-based to 0-based
            fixed_line = convert_coordinates_1_to_0(line)
            fixed_lines.append(fixed_line)
            
        elif line.startswith('Perm-prune '):
            # For Perm-prune lines, only convert coordinates before the colon
            if ':' in line:
                before_colon, after_colon = line.split(':', 1)
                # Convert coordinates in the part before the colon
                fixed_before_colon = convert_coordinates_1_to_0(before_colon)
                # Keep the part after colon unchanged
                fixed_line = fixed_before_colon + ':' + after_colon
                fixed_lines.append(fixed_line)
            else:
                # If no colon found, convert all coordinates (shouldn't happen based on format)
                fixed_line = convert_coordinates_1_to_0(line)
                fixed_lines.append(fixed_line)
        else:
            # For all other lines, keep them unchanged
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(input_filename, output_filename=None):
    """Process a KenKen descriptor file and fix coordinate indexing."""
    try:
        with open(input_filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        fixed_content = fix_kenken_coordinates(content)
        
        if output_filename:
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            print(f"Fixed content written to: {output_filename}")
        else:
            # If no output filename specified, create one based on input filename
            if input_filename.endswith('.txt'):
                output_filename = input_filename[:-4] + '_fixed.txt'
            else:
                output_filename = input_filename + '_fixed'
            
            with open(output_filename, 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            print(f"Fixed content written to: {output_filename}")
        
        return fixed_content
        
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' not found.")
        return None
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def main():
    """Main function to handle command line arguments or interactive input."""
    if len(sys.argv) > 1:
        # Command line usage
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        process_file(input_file, output_file)
    else:
        # Interactive usage
        input_file = input("Enter the input filename: ").strip()
        output_file = input("Enter the output filename (press Enter for auto-generated name): ").strip()
        output_file = output_file if output_file else None
        process_file(input_file, output_file)

# Example usage and test
if __name__ == "__main__":
    # Test with sample text
    sample_text = """Puzzle 1:
size: 4
allowed_numbers: 2 4 8 9
The cage covering (1,1), (1,2) must have a product of 32.
Perm-prune in 'The cage covering (1,3), (2,3) must have a sum of 10.': (1, 2) [2, 8]→[8]
Cage-line elim: remove 4 from (1,4) by row in 'The cage covering (1,1), (1,2) must have a product of 32.'
Updated combos for 'The cage covering (2,1), (3,1) must have a product of 16.': [(2, 8)]
Cage-single-combo: Cell (1,1) = 4"""
    
    print("Sample input:")
    print(sample_text)
    print("\nFixed output:")
    print(fix_kenken_coordinates(sample_text))
    print("\n" + "="*50)
    
    # Run main function for file processing
    main()

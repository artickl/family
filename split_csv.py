#!/usr/bin/env python3
"""
Split family_tree.csv into separate files based on record type headers.
"""
import csv
import sys
from pathlib import Path

# Define headers for each section type
SECTION_HEADERS = {
    'places': ['Place', 'Title', 'Name', 'Type', 'Latitude', 'Longitude', 'Code', 'Enclosed_by', 'Date'],
    'persons': ['Person', 'Surname', 'Given', 'Call', 'Nickname', 'Suffix', 'Prefix', 'Title', 'Gender', 
                'Birth date', 'Birth place', 'Birth source', 'Baptism date', 'Baptism place', 
                'Baptism source', 'Death date', 'Death place', 'Death source', 'Burial date', 
                'Burial place', 'Burial source', 'Note'],
    'marriages': ['Marriage', 'Husband', 'Wife', 'Date', 'Place', 'Source', 'Note'],
    'families': ['Family', 'Child']
}

def split_csv(input_file, output_dir=None):
    """
    Split the input CSV file into separate files based on headers.
    
    Args:
        input_file: Path to the input CSV file
        output_dir: Directory to write output files (defaults to same as input)
    """
    input_path = Path(input_file)
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
    
    # Create output files
    output_files = {
        'places': output_dir / 'family_tree_places.csv',
        'persons': output_dir / 'family_tree_persons.csv',
        'marriages': output_dir / 'family_tree_marriages.csv',
        'families': output_dir / 'family_tree_families.csv'
    }
    
    # Open all output files for writing
    writers = {}
    file_handles = {}
    for section_type, filepath in output_files.items():
        file_handles[section_type] = open(filepath, 'w', newline='', encoding='utf-8')
        writers[section_type] = csv.DictWriter(
            file_handles[section_type], 
            fieldnames=SECTION_HEADERS[section_type]
        )
        writers[section_type].writeheader()
    
    # Read and distribute input file
    current_section = None
    with open(input_path, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        for row_num, row in enumerate(reader, 1):
            if not row or row[0].strip() == '':
                # Skip empty rows
                continue
            
            # Check if this is a header row
            header_matched = False
            for section_type, headers in SECTION_HEADERS.items():
                if row == headers:
                    current_section = section_type
                    header_matched = True
                    print(f"Found {section_type} section at line {row_num}")
                    break
            
            if header_matched:
                continue
            
            # Write data row to current section
            if current_section:
                try:
                    # Create dict from row data
                    row_dict = {
                        SECTION_HEADERS[current_section][i]: (row[i] if i < len(row) else '')
                        for i in range(len(SECTION_HEADERS[current_section]))
                    }
                    writers[current_section].writerow(row_dict)
                except Exception as e:
                    print(f"Warning: Could not write row {row_num}: {e}", file=sys.stderr)
                    print(f"  Row data: {row}", file=sys.stderr)
    
    # Close all output files
    for fh in file_handles.values():
        fh.close()
    
    # Print summary
    print("\nCSV split completed successfully!")
    for section_type, filepath in output_files.items():
        line_count = sum(1 for _ in open(filepath)) - 1  # Exclude header
        print(f"  {filepath.name}: {line_count} records")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python split_csv.py <input_file> [output_dir]")
        print("Example: python split_csv.py family_tree.csv .")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        split_csv(input_file, output_dir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

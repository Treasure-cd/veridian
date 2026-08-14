import csv
import os

# Your massive file
input_file = '/home/treasure/Desktop/veridian/synthetic_data/output/transaction_line_items.csv'
output_prefix = '/home/treasure/Desktop/veridian/synthetic_data/output/transaction_line_items_part_'

chunk_size = 100000  # Number of rows per file

with open(input_file, 'r', newline='') as infile:
    reader = csv.reader(infile)
    header = next(reader) # Save the header row
    
    file_count = 1
    row_count = 0
    outfile = None
    writer = None
    
    for row in reader:
        if row_count % chunk_size == 0:
            if outfile:
                outfile.close()
            # Open a new chunk file
            outfile = open(f'{output_prefix}{file_count}.csv', 'w', newline='')
            writer = csv.writer(outfile)
            writer.writerow(header) # Write the header to every chunk
            file_count += 1
            
        writer.writerow(row)
        row_count += 1
        
    if outfile:
        outfile.close()

print(f"Done! Split into {file_count - 1} files.")
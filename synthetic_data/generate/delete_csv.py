import csv

file_name = '/home/treasure/Desktop/veridian/synthetic_data/output/customers_init.csv'
output_file = '/home/treasure/Desktop/veridian/synthetic_data/output/customers.csv'
column_indices = [0, 1, 2, 3, 4, 5, 6, 8]

with open(file_name, 'r') as csv_file, open(output_file, 'w', newline='') as fh:
    reader = csv.reader(csv_file)
    writer = csv.writer(fh)
    
    for row in reader:
        tmp_row = [row[i] for i in column_indices]
    
        writer.writerow(tmp_row)
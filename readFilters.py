import csv

filters = []

with open('filters.csv', mode='r', newline=None) as file:
    reader = csv.reader(file, delimiter='\n', quoting=csv.QUOTE_NONE)
    filters = [row[0].strip() for row in reader]

print(filters)
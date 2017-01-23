import csv

with open('/tmp/names.csv', 'w') as csvfile:
    fieldnames = ['first_name', 'last_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'first_name': 'Baked', 'last_name': 1.1})
    writer.writerow({'first_name': 'Lovely', 'last_name': 2.1})
    writer.writerow({'first_name': 'Wonderful', 'last_name': 3.1})
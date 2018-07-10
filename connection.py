import csv


def get_data(filename):
    lst = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lst.append(row)
    return lst


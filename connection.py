import csv


def get_data(filename):
    lst = []
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            lst.append(row)
    return lst


def write_data(filename):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile)
        writer.writerow(data)
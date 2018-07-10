import connection
import csv

question_tags = ['id', 'submisson_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_questions():
    return connection.get_data("sample_data/question.csv")


def add_question(new_question):
    with open(connection.get_data("sample_data/question.csv"), "a") as file:
        write_file = csv.DictWriter(file)
        write_file.writerow(new_question)

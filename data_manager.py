import connection


def get_questions():
    return connection.get_data("sample_data/question.csv")
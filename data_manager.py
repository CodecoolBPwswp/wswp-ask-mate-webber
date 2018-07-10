import connection

question_table = connection.get_data('sample_data/question.csv') #list of dict
answer_table = connection.get_data('sample_data/answer.csv') #list of dict


def get_next_answer_id():
    last_id = 0
    for key, value in answer_table:
        if key == 'id' and int(value) > last_id:
            last_id = int(value)
    next_id = last_id + 1
    return next_id


def get_questions():
    return connection.get_data("sample_data/question.csv")


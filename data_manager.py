import connection, server

question_table = connection.get_data('sample_data/question.csv') #list of dict
answer_table = connection.get_data('sample_data/answer.csv') #list of dict


def get_next_answer_id():
    last_id = 0
    for sublist in answer_table:
        for key, value in sublist.items():
            if key == 'id' and int(value) > last_id:
                last_id = int(value)
    next_id = last_id + 1
    return next_id


#unfinished
#def question_vote_up(question_id):
#    for key, value in question_table:
#        if key == 'id' and int(value) == int(question_id):



def get_questions():
    return connection.get_data("sample_data/question.csv")


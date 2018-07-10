import connection

question_table = connection.get_data('sample_data/question.csv') #list of dict
answer_table = connection.get_data('sample_data/answer.csv') #list of dict

QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message,image"]
ANSWER_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message","image"]

def get_next_answer_id():
    last_id = 0
    for key, value in answer_table:
        if key == 'id' and int(value) > last_id:
            last_id = int(value)
    next_id = last_id + 1
    return next_id


def get_question_byid(q_id):
    question = [question for question in question_table if int(question['id']) == q_id][0]
    answers = [answer for answer in answer_table if int(answer['question_id']) == q_id]
    return question, answers




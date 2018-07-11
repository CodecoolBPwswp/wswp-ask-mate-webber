import connection
import time


question_table = connection.get_data('sample_data/question.csv') #list of dict
answer_table = connection.get_data('sample_data/answer.csv') #list of dict

QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWER_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message", "image"]


def time_generator():
    return str(time.time()).split(".")[0]


def get_question_byid(q_id):
    question = [question for question in question_table if int(question['id']) == q_id][0]
    answers = [answer for answer in answer_table if int(answer['question_id']) == q_id]
    return question, answers


def new_answer(answer):
    for answers in answer_table:
        answers["id"] = str(int(answers["id"]) + 1)
    answer_table.insert(0, answer)
    return answer_table


def new_question(question):
    for questions in question_table:
        questions["id"] = str(int(questions["id"]) + 1)
    question_table.insert(0, question)
    return question_table


def increment_question_ids():
    for answers in answer_table:
        answers["question_id"] = str(int(answers["question_id"]) + 1)
    return answer_table


def put_new_data_to_file(filename, data, headers):
    return connection.write_data(filename, data, headers)


def render_question_or_answer(data, question, question_id):
    if "question_id" in data:
        updated_answers = new_answer(data)
        put_new_data_to_file('sample_data/answer.csv', updated_answers, ANSWER_HEADERS)
        answers = get_question_byid(question_id)[1]
        return question, answers
    else:
        updated_questions = new_question(data)
        increment_question_ids()
        answers = get_question_byid(question_id)[1]
        put_new_data_to_file('sample_data/question.csv', updated_questions, QUESTION_HEADERS)
        return  data, answers



#unfinished
#def question_vote_up(question_id):
#    for key, value in question_table:
#        if key == 'id' and int(value) == int(question_id):

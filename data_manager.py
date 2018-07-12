import connection
import time


QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWER_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message", "image"]

def get_all_questions():
    question_table = connection.get_data('sample_data/question.csv')
    return question_table


def get_all_answer():
    answer_table = connection.get_data('sample_data/answer.csv')
    return answer_table


def time_generator():
    return str(time.time()).split(".")[0]


def get_question_byid(q_id):
    question_table = get_all_questions()
    answer_table = get_all_answer()
    question = [question for question in question_table if int(question['id']) == q_id][0]
    answers = [answer for answer in answer_table if int(answer['question_id']) == q_id]
    return question, answers


def new_answer(answer):
    answer_table = get_all_answer()
    for answers in answer_table:
        answers["id"] = str(int(answers["id"]) + 1)
    answer_table.insert(0, answer)
    return answer_table


def new_question(question):
    question_table = get_all_questions()
    for questions in question_table:
        questions["id"] = str(int(questions["id"]) + 1)
    question_table.insert(0, question)
    return question_table


def delete(question_id):
    question_table = get_all_questions()
    answer_table = get_all_answer()
    answer_table = [answer for answer in answer_table if answer['question_id'] != question_id]
    question_table = [question for question in question_table if question['id'] != question_id]

    for i, question in enumerate(question_table):
        for answer in answer_table:
            if question['id'] == answer["question_id"]:
                answer['question_id'] = i

    for i, question in enumerate(question_table):
        question['id'] = i

    put_new_data_to_file('sample_data/question.csv', question_table, QUESTION_HEADERS)
    put_new_data_to_file('sample_data/answer.csv', answer_table, ANSWER_HEADERS)
    return question_id


def delete_answer(answer_id):
    answer_table = get_all_answer()
    for answer in answer_table:
        if answer["id"] == answer_id:
            answer_table.remove(answer)
    for i, answer in enumerate(answer_table):
        answer['id'] = i
    put_new_data_to_file('sample_data/answer.csv', answer_table, ANSWER_HEADERS)
    return answer_table


def increment_answer_ids():
    answer_table = get_all_answer()
    for answers in answer_table:
        answers["question_id"] = str(int(answers["question_id"]) + 1)
    put_new_data_to_file('sample_data/answer.csv', answer_table, ANSWER_HEADERS)
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
        increment_answer_ids()
        answers = get_question_byid(question_id)[1]
        put_new_data_to_file('sample_data/question.csv', updated_questions, QUESTION_HEADERS)
        return data, answers


def question_under_update(question_id):
    question_table = get_all_questions()
    for question in question_table:
        if question['id'] == str(question_id):
            return question


def update_question_table(new_data, question_id):
    update_question_table = []
    quest_tab = connection.get_data('sample_data/question.csv')
    for i, question in enumerate(quest_tab):
        if question['id'] == str(question_id):
            update_question_table.append(new_data)
        else:
            update_question_table.append(question)
    connection.write_data('sample_data/question.csv', update_question_table, QUESTION_HEADERS)
    return


def vote(question_id, data, button_data, operatorr):
    question_table = get_all_questions()
    answer_table = get_all_answer()
    if isinstance(data, dict):
        data['vote_number'] = str(operatorr(int(data['vote_number']), 1))
        updated_questions = [data if data['id'] == question['id'] else question for question in question_table ]
        put_new_data_to_file('sample_data/question.csv', updated_questions, QUESTION_HEADERS)
    elif isinstance(data, list):
        for i, row in enumerate(data):
            if row['question_id'] == str(question_id) and row['id'] == button_data.get("answer"):
                row['vote_number'] = str(operatorr(int(row['vote_number']), 1))
                updated_answers = [row if i == ind else answer for ind, answer in enumerate(answer_table)]
                put_new_data_to_file('sample_data/answer.csv', updated_answers, ANSWER_HEADERS)
    return data

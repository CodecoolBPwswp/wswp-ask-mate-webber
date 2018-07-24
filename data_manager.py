import database_common
import datetime
import os


def time_generator():
    dt = datetime.now()
    return dt

@database_common.connection_handler
def get_all_questions_start_with_latest(cursor):
    cursor.execute("SELECT * FROM question ORDER BY submission_time DESC")
    question_table = cursor.fetchall()

    return question_table


@database_common.connection_handler
def get_all_answer(cursor):
    cursor.execute("SELECT * FROM answer")
    answer_table = cursor.fetchall()

    return answer_table


@database_common.connection_handler
def get_question_byid(cursor, q_id):
    cursor.execute("SELECT * FROM question WHERE id=%s", (q_id,))
    question = cursor.fetchall()

    cursor.execute("SELECT * FROM answer WHERE question_id=%s", (q_id,))
    answers = cursor.fetchall()

    return question, answers


@database_common.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("SELECT question_id FROM answer WHERE id=%s", (answer_id,))
    question_id = cursor.fetchall()

    return question_id


@database_common.connection_handler
def delete(cursor, question_id):
    cursor.execute("SELECT image FROM answer WHERE question_id=%s", (question_id,))
    images_from_answers = cursor.fetchall()
    images_from_answers = list(images_from_answers.values())
    for image in images_from_answers:
        os.remove(os.path.join('static/images', image))

    cursor.execute("DELETE FROM answer WHERE question_id=%s", (question_id,))
    cursor.execute("DELETE FROM question WHERE id=%s", (question_id,))


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("DELETE FROM answer WHERE question_id=%s", (answer_id,))

@database_common.connection_handler
def update_question_table(cursor, new_data, question_id):
    cursor.execute("""UPDATE question 
                   SET submission_time = new_data[submission_time], view_number = new_data[view_number], vote_number = new_data[vote_number], title = new_data[title], message = new_data[message], image = new_data[image]"
                   WHERE id=%s""", (question_id))


def render_question_or_answer(data, question, question_id):
    if "question_id" in data:
        updated_answers = new_answer(data)
        answers = get_question_byid(question_id)[1]
        return question, answers
    else:
        updated_questions = new_question(data)
        answers = get_question_byid(question_id)[1]
        return data, answers


@database_common.connection_handler
def vote(cursor,question_id, data, button_data, operatorr):
    if isinstance(data, dict):
        data['vote_number'] = operatorr(int(data['vote_number']), 1)
        cursor.execute("UPDATE question SET vote_number=%s WHERE id=%s", (data['vote_number'], data['id']))
    elif isinstance(data, list):
        for i, row in enumerate(data):
            if row['question_id'] == str(question_id) and row['id'] == button_data.get("answer"):
                row['vote_number'] = operatorr(int(row['vote_number']), 1)
                cursor.execute("UPDATE answer SET vote_number=%s WHERE id=%s", (row['vote_number'], row['id'],))

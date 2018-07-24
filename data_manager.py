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

    return question,answers


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

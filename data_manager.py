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


@database_common.connection_handler
def update_question_table(cursor, new_data, question_id):
    cursor.execute("""UPDATE question 
                   SET submission_time = %s, view_number = %s, vote_number = %s, title = %s, message = %s, image = %s
                   WHERE id=%s""", (new_data['submission_time'], new_data['view_number'], new_data['vote_number'], new_data['title'], new_data['message'], new_data['image'], question_id))


@database_common.connection_handler
def new_answer(cursor, answer):
    cursor.execute("""INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                    VALUES(%s, %s, %s, %s, %s)""", (answer['submission_time'], answer['vote_number'], answer['question_id'], answer['message'], answer['image']))


@database_common.connection_handler
def new_question(cursor, question):
    cursor.execute("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                        VALUES(%s, %s, %s, %s, %s, %s)""",
                   (question['submission_time'], question['view_number'], question['vote_number'], question['title'], question['message'], question['image']))

import database_common
import datetime
import os


QUESTION_HEADERS = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image", "comment"]
ANSWER_HEADERS = ["id", "submission_time", "vote_number", "question_id", "message", "image", "comment"]


def time_generator():
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
    #cursor.execute("UPDATE question SET view_number=view_number+1 WHERE id=%s", (q_id,))

    cursor.execute("SELECT * FROM question WHERE id=%s", (q_id,))
    question = cursor.fetchall()

    cursor.execute("SELECT * FROM answer WHERE question_id=%s ORDER BY submission_time DESC", (q_id,))
    answers = cursor.fetchall()

    return question, answers


@database_common.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("SELECT question_id FROM answer WHERE id=%s ", (answer_id,))
    question_id = cursor.fetchall()
    return question_id[0]


@database_common.connection_handler
def delete(cursor, question_id):
    cursor.execute("SELECT image FROM answer WHERE question_id=%s", (question_id,))
    images_from_answers = cursor.fetchall()
    for answer in images_from_answers:
        if answer['image'] != '':
            os.remove(os.path.join('static/images', answer['image']))

    cursor.execute("SELECT id FROM answer WHERE question_id=%s", (question_id,))
    ans_id_for_delete = cursor.fetchall()
    ans_ids = tuple([value['id'] for value in ans_id_for_delete])
    if ans_ids:
        cursor.execute("DELETE FROM comment WHERE answer_id IN %s", (ans_ids,))

    cursor.execute("DELETE FROM comment WHERE question_id=%s", (question_id,))
    cursor.execute("DELETE FROM answer WHERE question_id=%s", (question_id,))
    cursor.execute("DELETE FROM question WHERE id=%s", (question_id,))


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    cursor.execute("DELETE FROM comment WHERE answer_id=%s", (answer_id,))
    cursor.execute("DELETE FROM answer WHERE id=%s", (answer_id,))


@database_common.connection_handler
def question_under_update(cursor, question_id):
    cursor.execute("SELECT * FROM question WHERE id=%s", (question_id,))
    question = cursor.fetchall()
    return question[0]


@database_common.connection_handler
def answer_under_update(cursor, answer_id):
    cursor.execute("SELECT * FROM answer WHERE id=%s", (answer_id,))
    answer = cursor.fetchall()
    return answer[0]


@database_common.connection_handler
def update_question_table(cursor, new_data, question_id):
    cursor.execute("""UPDATE question 
                   SET submission_time =%s , view_number = %s, vote_number = %s, title = %s, message = %s, image = %s
                   WHERE id=%s""", (new_data['submission_time'], new_data['view_number'], new_data['vote_number'], new_data['title'], new_data['message'], new_data['image'], question_id))


@database_common.connection_handler
def update_answer_table(cursor, new_data, answer_id):
    cursor.execute("""UPDATE answer 
                   SET submission_time =%s , vote_number = %s, question_id = %s, message = %s, image = %s
                   WHERE id=%s""", (new_data['submission_time'], new_data['vote_number'], new_data['question_id'], new_data['message'], new_data['image'], answer_id))

    cursor.execute("""SELECT question_id FROM answer WHERE id=%s""", (answer_id,))
    question_id = cursor.fetchall()[0]
    return question_id

@database_common.connection_handler
def new_answer(cursor, answer):
    cursor.execute("""INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                    VALUES(%s, %s, %s, %s, %s)""", (answer['submission_time'], answer['vote_number'], answer['question_id'], answer['message'], answer['image']))

    cursor.execute("SELECT * FROM answer ORDER BY ID DESC LIMIT 1")
    answer = cursor.fetchall()
    return answer

@database_common.connection_handler
def new_question(cursor, question):
    cursor.execute("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                        VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s)""",
                   question)

    cursor.execute("SELECT * FROM question ORDER BY ID DESC LIMIT 1")
    question = cursor.fetchall()
    return question


def add_question_or_answer(data):
    if "question_id" in data:
        answer = new_answer(data)
        return answer[0]['question_id']
    else:
        question = new_question(data)
        return question[0]['id']


@database_common.connection_handler
def vote(cursor, question_id, button_data, operatorr):
    data = get_question_byid(question_id)[0][0]
    if "question" in button_data.keys():
        data['vote_number'] = operatorr(int(data['vote_number']), 1)
        cursor.execute("UPDATE question SET vote_number=%s WHERE id=%s", (data['vote_number'], data['id']))
    elif "answer" in button_data.keys():
        cursor.execute("SELECT vote_number FROM answer WHERE id=%s", (button_data['answer'],))
        data = cursor.fetchall()[0]
        data['vote_number'] = operatorr(int(data['vote_number']), 1)
        cursor.execute("UPDATE answer SET vote_number=%s WHERE id=%s AND question_id=%s ", (data['vote_number'], button_data['answer'], question_id))


@database_common.connection_handler
def question_comment(cursor, comment):
    cursor.execute("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
                      VALUES(%(question_id)s,%(answer_id)s,%(message)s,%(submission_time)s,%(edited_count)s)    
                    """, comment)


@database_common.connection_handler
def answer_comment(cursor, comment):
    cursor.execute("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
                      VALUES(%(question_id)s,%(answer_id)s,%(message)s,%(submission_time)s,%(edited_count)s)    
                    """, comment)

    cursor.execute("SELECT question_id FROM answer WHERE id=%s", (comment['answer_id'],))
    question_id = cursor.fetchall()
    return question_id[0]['question_id']


@database_common.connection_handler
def get_comments(cursor, question_id):

    cursor.execute("SELECT * FROM comment WHERE question_id=%s ORDER BY submission_time DESC", (question_id,))
    q_comments = cursor.fetchall()
    comments = q_comments

    cursor.execute("SELECT id FROM answer WHERE question_id=%s", (question_id,))
    ans_id_for_comments = cursor.fetchall()
    ans_ids = tuple([value['id'] for value in ans_id_for_comments])
    if ans_ids:
        cursor.execute("SELECT * FROM comment WHERE answer_id IN %s ORDER BY submission_time DESC", (ans_ids,))
        a_comments = cursor.fetchall()
        comments = a_comments + q_comments

    return comments


@database_common.connection_handler
def find_searched_data_in_answer_db(cursor, searched_phase):
    cursor.execute("""SELECT * FROM answer WHERE message LIKE '%{}%';""".format(searched_phase['q']))
    answer_data = cursor.fetchall()
    for data in answer_data:
        data['message'] = data['message'].replace(searched_phase['q'], "<mark>{}</mark>".format(searched_phase['q']))
    return answer_data


@database_common.connection_handler
def find_searched_data_in_question_db(cursor, searched_phase):
    cursor.execute("""SELECT * FROM question WHERE title LIKE '%{}%' OR message LIKE '%{}%';""".format(searched_phase['q'], searched_phase['q']))
    question_data = cursor.fetchall()
    for data in question_data:
        data['title'] = data['title'].replace(searched_phase['q'], "<mark>{}</mark>".format(searched_phase['q']))
        data['message'] = data['message'].replace(searched_phase['q'], "<mark>{}</mark>".format(searched_phase['q']))
    return question_data


@database_common.connection_handler
def delete_question_comment(cursor, comment_id):
    cursor.execute("DELETE FROM comment WHERE id=%s", (comment_id,))


@database_common.connection_handler
def delete_answer_comment(cursor, comment_id, answer_id):
    cursor.execute("SELECT question_id FROM answer WHERE id=%s", (answer_id['answer_id'],))
    question_id = cursor.fetchall()[0]

    cursor.execute("DELETE FROM comment WHERE id=%s ", (comment_id,))

    return question_id


@database_common.connection_handler
def get_latest_five_question(cursor):
    cursor.execute("SELECT * FROM question ORDER BY submission_time DESC LIMIT 5")
    top_five = cursor.fetchall()

    return top_five

@database_common.connection_handler
def get_comment_by_id(cursor, comment_id):
    cursor.execute("SELECT * FROM comment WHERE id=%s", (comment_id,))
    comment = cursor.fetchall()[0]

    return comment


@database_common.connection_handler
def update_question_comment_by_id(cursor, comment, comment_id):
    cursor.execute("UPDATE comment SET message = %s WHERE id=%s", (comment['message'], comment_id))

    if comment['answer_id'] == 'None':
        comment['answer_id'] = None
        cursor.execute("SELECT question_id FROM comment WHERE id=%s", (comment_id,))
        question_id = cursor.fetchall()[0]
    else:
        cursor.execute("UPDATE comment SET message = %s WHERE id=%s", (comment['message'], comment_id))

        cursor.execute("SELECT question_id FROM answer WHERE id=%s", (comment['answer_id'],))
        question_id = cursor.fetchall()[0]

    return question_id

@database_common.connection_handler
def get_tags(cursor, question_id):
    tags_to_return = []
    cursor.execute("SELECT tag_id FROM question_tag WHERE question_id=%s", (question_id,))
    tags = cursor.fetchall()
    tag_ids = tuple([value['tag_id'] for value in tags])
    if tag_ids:
        cursor.execute("SELECT * FROM tag WHERE id in %s", (tag_ids,))
        tags_to_return = cursor.fetchall()

    return tags_to_return


@database_common.connection_handler
def possible_tags(cursor, question_id):
    cursor.execute("SELECT tag_id FROM question_tag WHERE question_id=%s", (question_id,))
    tags = cursor.fetchall()
    tag_ids = tuple([value['tag_id'] for value in tags])
    if tag_ids:
        cursor.execute("SELECT name FROM tag WHERE id NOT IN %s", (tag_ids,))
        tags_to_return = cursor.fetchall()
    else:
        cursor.execute("SELECT name FROM tag")
        tags_to_return = cursor.fetchall()

    return tags_to_return


@database_common.connection_handler
def new_input_tag(cursor, tag, question_id):
    cursor.execute("INSERT INTO tag (name) VALUES (%s)", (tag,))
    cursor.execute("SELECT * FROM tag ORDER BY ID DESC LIMIT 1")
    tag_id = cursor.fetchall()[0]

    cursor.execute("INSERT INTO question_tag (question_id, tag_id) VALUES (%s, %s)", (question_id, tag_id['id']))


@database_common.connection_handler
def new_available_tag(cursor, tag, question_id):
    cursor.execute("SELECT id FROM tag WHERE name=%s", (tag["new_tag"],))
    tag_id = cursor.fetchall()[0]
    cursor.execute("INSERT INTO question_tag (question_id, tag_id) VALUES (%s, %s)", (question_id, tag_id['id']))


@database_common.connection_handler
def delete_tag(cursor, question_id, tag_id):
    cursor.execute("DELETE FROM question_tag WHERE question_id=%s and tag_id=%s", (question_id, tag_id))
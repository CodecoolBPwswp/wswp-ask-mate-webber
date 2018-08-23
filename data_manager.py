import database_common
import datetime
import os
import password_hasher


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

    cursor.execute("""SELECT question.*, users.username, users.id AS user_id
                      FROM question LEFT JOIN users ON question.user_id = users.id 
                      WHERE question.id=%s""", (q_id,))
    question = cursor.fetchall()

    cursor.execute("""SELECT answer.*, users.username, users.id AS user_id
                      FROM answer LEFT JOIN users ON answer.user_id = users.id
                      WHERE answer.question_id=%s ORDER BY submission_time DESC""", (q_id,))
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

    cursor.execute("DELETE FROM question_tag WHERE question_id=%s", (question_id,))
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
    cursor.execute("""INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                    VALUES(%s, %s, %s, %s, %s, %s)""", (answer['submission_time'], answer['vote_number'], answer['question_id'], answer['message'], answer['image'], answer["user_id"]))

    cursor.execute("SELECT * FROM answer ORDER BY ID DESC LIMIT 1")
    answer = cursor.fetchall()
    return answer

@database_common.connection_handler
def new_question(cursor, question):
    cursor.execute("""INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id)
                        VALUES(%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s, %(user_id)s)""",
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
def vote(cursor, question_id, button_data, operatorr, user_id):
    data = get_question_byid(question_id)[0][0]
    if "question" in button_data.keys():
        data['vote_number'] = operatorr(int(data['vote_number']), 1)
        cursor.execute("UPDATE question SET vote_number=%s WHERE id=%s", (data['vote_number'], data['id']))
        cursor.execute("""INSERT INTO votes (user_id, question_id) 
                          VALUES (%s, %s)""", (user_id, data['id']))

    elif "answer" in button_data.keys():
        cursor.execute("SELECT vote_number FROM answer WHERE id=%s", (button_data['answer'],))
        data = cursor.fetchall()[0]
        data['vote_number'] = operatorr(int(data['vote_number']), 1)
        cursor.execute("UPDATE answer SET vote_number=%s WHERE id=%s AND question_id=%s ", (data['vote_number'], button_data['answer'], question_id))
        cursor.execute("""INSERT INTO votes (user_id, answer_id)
                          VALUES (%s, %s)""", (user_id, button_data["answer"]))


@database_common.connection_handler
def votes_for_question(cursor, question_id, user_id):
    cursor.execute("""
                    SELECT question_id FROM votes
                    WHERE user_id = %s AND question_id = %s
                  """, (user_id, question_id))

    try:
        question_vote = cursor.fetchall()[0]
        return question_vote
    except IndexError:
        return False


@database_common.connection_handler
def votes_for_answer(cursor, user_id):
    cursor.execute("""
                    SELECT answer_id FROM votes
                    WHERE user_id = %s AND answer_id IS NOT NULL
                  """, (user_id,))

    answer_votes = cursor.fetchall()
    answer_votes = tuple([answer['answer_id'] for answer in answer_votes])
    return answer_votes


@database_common.connection_handler
def question_comment(cursor, comment):
    cursor.execute("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count, user_id)
                      VALUES(%(question_id)s,%(answer_id)s,%(message)s,%(submission_time)s,%(edited_count)s, %(user_id)s)
                    """, comment)


@database_common.connection_handler
def answer_comment(cursor, comment):
    cursor.execute("""INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count,user_id)
                      VALUES(%(question_id)s,%(answer_id)s,%(message)s,%(submission_time)s,%(edited_count)s, %(user_id)s)
                    """, comment)

    cursor.execute("SELECT question_id FROM answer WHERE id=%s", (comment['answer_id'],))
    question_id = cursor.fetchall()
    return question_id[0]['question_id']


@database_common.connection_handler
def get_comments(cursor, question_id):

    cursor.execute("""SELECT comment.*, users.username, users.id AS user_id FROM comment 
                      LEFT JOIN users ON comment.user_id = users.id 
                      WHERE comment.question_id=%s ORDER BY comment.submission_time DESC""", (question_id,))
    q_comments = cursor.fetchall()
    comments = q_comments

    # cursor.execute("SELECT id FROM answer WHERE question_id=%s", (question_id,))
    # ans_id_for_comments = cursor.fetchall()
    # ans_ids = tuple([value['id'] for value in ans_id_for_comments])
    # if ans_ids:
    #     cursor.execute("""SELECT comment.*, users.username, users.id AS user_id FROM comment
    #                       LEFT JOIN users ON comment.user_id = users.id
    #                       WHERE comment.answer_id IN %s ORDER BY comment.submission_time DESC""", (ans_ids,))
    #     a_comments = cursor.fetchall()
    #     comments = a_comments + q_comments
    print(comments)
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


@database_common.connection_handler
def user_name_check(cursor, username):
    cursor.execute("""SELECT CASE WHEN EXISTS (
                    SELECT *
                    FROM users
                    WHERE username = %s
                    )
                    THEN CAST(1 AS BIT)
                    ELSE CAST(0 AS BIT) END""", (username,))

    used = cursor.fetchall()[0]['case']

    return int(used)


@database_common.connection_handler
def insert_new_user(cursor, username, password_hash):
    date = time_generator()
    cursor.execute(""" 
                    INSERT INTO users (username, hashed_pw, date) 
                    VALUES (%s, %s, %s) 
                    """, (username, password_hash, date))


@database_common.connection_handler
def verify_login(cursor, username, password):
    cursor.execute("""
                    SELECT username, hashed_pw FROM users
                    WHERE username = %s
                    """, (username,))
    try:
        user = cursor.fetchall()[0]
        verified = password_hasher.verify_password(password, user['hashed_pw'])

        return verified
    except IndexError:
        verified = False
        return verified


@database_common.connection_handler
def get_user_id_by_name(cursor, username):
    cursor.execute("""
                    SELECT id FROM users WHERE username = %s
                """, (username,))

    user_id = cursor.fetchall()[0]['id']
    return user_id


@database_common.connection_handler
def get_users_questions(cursor, user_id):
    cursor.execute("""SELECT question.id, question.submission_time, question.title, users.username 
                      FROM question LEFT JOIN users ON question.user_id = users.id 
                      WHERE question.user_id = %s""", (user_id,))

    users_questions = cursor.fetchall()

    return users_questions


@database_common.connection_handler
def get_users_answers(cursor, user_id):
    cursor.execute("""SELECT answer.question_id, answer.submission_time, answer.message, users.username 
                      FROM answer LEFT JOIN users ON answer.user_id = users.id 
                      WHERE answer.user_id = %s""", (user_id,))

    users_answers = cursor.fetchall()

    return users_answers


@database_common.connection_handler
def get_users_comments(cursor, user_id):
    cursor.execute("""SELECT comment.question_id, comment.submission_time, comment.message, users.username 
                      FROM comment LEFT JOIN users ON comment.user_id = users.id 
                      WHERE comment.user_id = %s""", (user_id,))

    users_comments = cursor.fetchall()

    return users_comments


@database_common.connection_handler
def get_all_tag(cursor):
    cursor.execute("""
                    SELECT tag.name, COUNT(question_tag.tag_id) 
                    FROM tag LEFT JOIN question_tag ON tag.id = question_tag.tag_id 
                    GROUP BY tag.name 
                    ORDER BY COUNT(question_tag.tag_id) DESC
                    """)

    tags = cursor.fetchall()
    return tags


@database_common.connection_handler
def accepted_answer_and_return_question_id(cursor, answer_id):
    cursor.execute("""
                UPDATE answer SET accepted = True
                WHERE id = %s   
                """, (answer_id,))

    cursor.execute("SELECT question_id FROM answer WHERE id=%s", (answer_id,))

    question_id = cursor.fetchall()[0]['question_id']

    return question_id


@database_common.connection_handler
def accepted_question_answer(cursor, question_id):
    cursor.execute("""
                UPDATE question SET accepted_answer = True
                WHERE id = %s
                """, (question_id,))


@database_common.connection_handler
def all_users_data(cursor):
    cursor.execute("""SELECT users.id, users.username, users.date, users.reputation, comments.sum_comment, questions.sum_question, answers.sum_answer
                        
                          FROM users
                             LEFT JOIN (
                              SELECT COUNT(comment.user_id) AS sum_comment, comment.user_id FROM comment GROUP BY comment.user_id
                              ) AS comments ON users.id = comments.user_id
                             LEFT JOIN (
                              SELECT COUNT(question.user_id) AS sum_question, question.user_id FROM question GROUP BY question.user_id
                              ) AS questions ON comments.user_id = questions.user_id
                             LEFT JOIN (
                              SELECT COUNT(answer.user_id) AS sum_answer, answer.user_id FROM answer GROUP BY answer.user_id
                              ) AS answers ON questions.user_id = answers.user_id ORDER BY users.reputation DESC""")
    users_data = cursor.fetchall()
    return users_data


@database_common.connection_handler
def reputation_handler_for_votes(cursor,dir, operatorr, data, question_id):

    if "question" in data.keys():
        cursor.execute("SELECT user_id FROM question WHERE id = %s", (question_id,))
        user_id = cursor.fetchall()[0]['user_id']

        cursor.execute("SELECT reputation FROM users WHERE id=%s", (user_id,))
        reputation = cursor.fetchall()[0]['reputation']

        rep = operatorr(reputation, 5) if dir == "up" else operatorr(reputation, 2)

    elif "answer" in data.keys():
        cursor.execute("SELECT user_id FROM answer WHERE id = %s", (data['answer'],))
        user_id = cursor.fetchall()[0]['user_id']

        cursor.execute("SELECT reputation FROM users WHERE id=%s", (user_id,))
        reputation = cursor.fetchall()[0]['reputation']

        rep = operatorr(reputation, 10) if dir == "up" else operatorr(reputation, 2)

    cursor.execute("UPDATE users SET reputation= %s WHERE id = %s", (rep, user_id))


@database_common.connection_handler
def accepted_answer_reputation(cursor, answer_id):
    cursor.execute("SELECT user_id FROM answer WHERE id = %s", (answer_id,))
    user_id = cursor.fetchall()[0]['user_id']

    cursor.execute("SELECT reputation FROM users WHERE id=%s", (user_id,))
    reputation = cursor.fetchall()[0]['reputation']

    reputation += 15

    cursor.execute("UPDATE users SET reputation= %s WHERE id = %s", (reputation, user_id))
import database_common


@database_common.connection_handler
def get_all_questions(cursor):
    cursor.execute("SELECT * FROM question")
    question_table = cursor.fetchall()

    return question_table


@database_common.connection_handler
def get_all_answer(cursor):
    cursor.execute("SELECT * FROM answer")
    answer_table = cursor.fetchall()

    return answer_table
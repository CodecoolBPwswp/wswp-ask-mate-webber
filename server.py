from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    questions = data_manager.question_table
    return render_template("list.html", questions=questions)


@app.route('/add-question', methods=['GET','POST'])
def add_question():
    if request.method == 'POST':
        submission_time = data_manager.time_generator()
        return render_template("question.html",next_id=0,submission_time=submission_time)


@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
def question(question_id):
    html_file = "question_with_answers.html"
    q_head = data_manager.QUESTION_HEADERS
    a_head = data_manager.ANSWER_HEADERS
    question, answers = data_manager.get_question_byid(question_id)
    if request.method == "POST":
        data = request.form.to_dict()
        question, answers= data_manager.render_question_or_answer(data, question, question_id)
        return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)

    return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def write_answer(question_id):
    if request.method == 'POST':
        submission_time = data_manager.time_generator()
        return render_template('new_answer.html', next_id=0, question_id=question_id, submission_time=submission_time)



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    questions =  data_manager.question_table
    return render_template("list.html", questions=questions)


@app.route("/question/<int:question_id>")
def question(question_id):
    question, answers = data_manager.get_question_byid(question_id)
    q_head = data_manager.QUESTION_HEADERS
    a_head = data_manager.ANSWER_HEADERS
    return render_template("question_with_answers.html", question=question, answers=answers, q_head=q_head, a_head=a_head)



@app.route('/question/<question_id>/new-answer', methods=['GET','POST'])
def write_answer(question_id):
    if request.method == 'GET':
        next_id = data_manager.get_next_answer_id()
        return render_template('new_answer.html', next_id=next_id, question_id=question_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        return redirect('/list', new_answer=data)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

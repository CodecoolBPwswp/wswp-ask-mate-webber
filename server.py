from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    questions =  data_manager.question_table
    return render_template("list.html", questions=questions)


@app.route('/add-question/', methods=['GET','POST'])
def add_question():
    if request.method == 'GET':
        return redirect(url_for('/list'))
    elif request.method == 'POST':
        render_template("question.html")


@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
def question(question_id):
    q_head = data_manager.QUESTION_HEADERS
    a_head = data_manager.ANSWER_HEADERS
    question, answers = data_manager.get_question_byid(question_id)
    if request.method == "POST":
        data = request.form.to_dict()
        if "question_id" in data:
            new_answers = data_manager.new_answer(data)
            data_manager.put_answers_to_file('sample_data/answer.csv', new_answers)
            answers = data_manager.get_question_byid(question_id)[1]
            return render_template("question_with_answers.html", question=question, answers=answers, q_head=q_head,
                                   a_head=a_head)
        else:
            pass
    return render_template("question_with_answers.html", question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def write_answer(question_id):
    if request.method == 'POST':
        submission_time = data_manager.time_generator()
        return render_template('new_answer.html', next_id=0, question_id=question_id, submission_time=submission_time)


# unfinished
@app.route('/question/<question_id>/vote-up')
def question_vote_up():
    question_data = data_manager.question_table

    return redirect('/question/<question_id>')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

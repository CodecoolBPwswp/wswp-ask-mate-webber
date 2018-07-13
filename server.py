from flask import Flask, render_template, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
import data_manager
import operator
from operator import itemgetter
import time


app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = "static/images"
configure_uploads(app, photos)

q_head = data_manager.QUESTION_HEADERS
a_head = data_manager.ANSWER_HEADERS


@app.route('/')
@app.route('/list')
def index():
    command = request.args.to_dict()
    questions = data_manager.get_all_questions()
    if command and command['order_direction'] == 'desc':
        questions = sorted(questions, key=itemgetter(command['order_by']), reverse=True)
    elif command and command['order_direction'] == 'asc':
        questions = sorted(questions, key=itemgetter(command['order_by']))
    return render_template("list.html", questions=questions)


@app.route('/add-question', methods=['POST'])
def add_question():
    submission_time = data_manager.time_generator()
    return render_template("question.html", next_id=0, submission_time=submission_time)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_manager.delete(question_id)
    return redirect('/list')


@app.route("/answer/<answer_id>/delete", methods=['POST'])
def delete_answer(answer_id):
    html_file = "question_with_answers.html"
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data_manager.delete_answer(answer_id)
    question, answers = data_manager.get_question_byid(int(question_id))
    return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
def question(question_id):
    html_file = "question_with_answers.html"
    question, answers = data_manager.get_question_byid(question_id)
    if request.method == 'POST' and 'photo' in request.files:
        try:
            filename = photos.save(request.files['photo'])
            data = request.form.to_dict()
            data["image"] = filename
            question, answers = data_manager.render_question_or_answer(data, question, question_id)
            return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)
        except:
            data = request.form.to_dict()
            question, answers = data_manager.render_question_or_answer(data, question, question_id)
            return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)

    return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def write_answer(question_id):
    submission_time = data_manager.time_generator()
    if request.method == 'POST':
        return render_template('new_answer.html', next_id=0, question_id=question_id, submission_time=submission_time)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def update_question(question_id):
    if request.method == 'GET':
        update = True
        question_needs_update = data_manager.question_under_update(question_id)
        return render_template('question.html', question=question_needs_update, update=update)
    else:
        data = request.form.to_dict()
        data_manager.update_question_table(data, data['id'])
        return redirect('/list')


@app.route('/question/<int:question_id>/vote-up', methods=["POST"])
def up_vote(question_id):
    operatorr = operator.__add__
    html_file = "question_with_answers.html"
    question, answers = data_manager.get_question_byid(question_id)
    data = request.form.to_dict()
    if "question" in data.keys():
        question = data_manager.vote(question_id, question, data, operatorr)
        return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)
    elif "answer" in data.keys():
        answers = data_manager.vote(question_id, answers, data, operatorr)
        return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.route('/question/<int:question_id>/vote-down', methods=["POST"])
def down_vote(question_id):
    operatorr = operator.__sub__
    html_file = "question_with_answers.html"
    question, answers = data_manager.get_question_byid(question_id)
    data = request.form.to_dict()
    if "question" in data.keys():
        question = data_manager.vote(question_id, question, data, operatorr)
        return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)
    elif "answer" in data.keys():
        answers = data_manager.vote(question_id, answers, data, operatorr)
        return render_template(html_file, question=question, answers=answers, q_head=q_head, a_head=a_head)


@app.template_filter('ctime')
def timectime(s):
    return time.ctime(int(s))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

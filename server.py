from flask import Flask, render_template, request, redirect
from flask_uploads import UploadSet, configure_uploads, IMAGES
import data_manager
import operator
import os
from operator import itemgetter


app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = "static/images"
configure_uploads(app, photos)

q_head = data_manager.QUESTION_HEADERS
a_head = data_manager.ANSWER_HEADERS


@app.route('/')
def main():
    questions = data_manager.get_latest_five_question()
    first = True
    return render_template("list.html", questions=questions, first=first)


@app.route('/list')
def index():
    command = request.args.to_dict()
    questions = data_manager.get_all_questions_start_with_latest()
    if command and command['order_direction'] == 'desc':
        questions = sorted(questions, key=itemgetter(command['order_by']), reverse=True)
    elif command and command['order_direction'] == 'asc':
        questions = sorted(questions, key=itemgetter(command['order_by']))
    return render_template("list.html", questions=questions)


@app.route('/add-question', methods=['POST'])
def add_question():
    submission_time = data_manager.time_generator()

    return render_template("question.html", submission_time=submission_time)


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data = request.args.to_dict()
    if data['image'] != '':
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], data['image']))
    data_manager.delete(question_id)
    return redirect('/list')


@app.route("/answer/<int:answer_id>/delete")
def delete_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    data = request.args.to_dict()
    print(data)
    if data['image'] != '':
        os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], data['image']))
    data_manager.delete_answer(answer_id)
    return redirect('question/{}'.format(question_id['question_id']))


@app.route("/answer/", methods=['POST'])
@app.route("/question/", methods=['POST'])
def save_question():
    if request.method == 'POST' and 'photo' in request.files:
        try:
            filename = photos.save(request.files['photo'])
            data = request.form.to_dict()
            data["image"] = filename
            id_var = data_manager.add_question_or_answer(data)
        except:
            data = request.form.to_dict()
            id_var = data_manager.add_question_or_answer(data)

        return redirect('question/{}'.format(id_var))


@app.route("/question/<int:question_id>", methods=['GET', 'POST'])
def question(question_id):
    html_file = "question_with_answers.html"
    question, answers = data_manager.get_question_byid(question_id)
    comments = data_manager.get_comments(question_id)

    return render_template(html_file, question=question[0], answers=answers, q_head=q_head, a_head=a_head, comments=comments)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def write_answer(question_id):
    submission_time = data_manager.time_generator()
    if request.method == 'POST':
        return render_template('new_answer.html', question_id=question_id, submission_time=submission_time)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def update_question(question_id):
    if request.method == 'GET':
        update = True
        question_needs_update = data_manager.question_under_update(question_id)
        return render_template('question.html', question=question_needs_update, update=update)
    else:
        data = request.form.to_dict()
        data_manager.update_question_table(data, data['id'])
        return redirect('/question/{}'.format(question_id))

@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    submission_time = data_manager.time_generator()
    if request.method == 'GET':
        update = True
        answer_needs_update = data_manager.answer_under_update(answer_id)
        return render_template('new_answer.html', submission_time=submission_time, answer=answer_needs_update, update=update)
    else:
        data = request.form.to_dict()
        question_id = data_manager.update_answer_table(data, answer_id)
        return redirect('/question/{}'.format(question_id['question_id']))


@app.route('/question/<int:question_id>/vote-<dir>', methods=["POST"])
def voter(question_id, dir):
    operatorr = operator.__add__ if dir == "up" else operator.__sub__
    data = request.form.to_dict()
    data_manager.vote(question_id, data, operatorr)
    return redirect('question/{}'.format(question_id))


@app.route('/question/<int:question_id>/new-comment', methods=['GET', 'POST'])
def new_comment_to_question(question_id):
    if request.method == 'GET':
        question_comment = True
        submission_time = data_manager.time_generator()
        return render_template('new_comment.html', question_id=question_id, submission_time=submission_time, question_comment=question_comment)
    else:
        comment = request.form.to_dict()
        comment["question_id"] = question_id
        comment["answer_id"] = None
        comment["edited_count"] = None
        data_manager.question_comment(comment)
        return redirect('question/{}'.format(question_id))


@app.route('/answer/<int:answer_id>/new-comment', methods=['GET', 'POST'])
def new_comment_to_answer(answer_id):
    if request.method == 'GET':
        question_comment = False
        submission_time = data_manager.time_generator()
        return render_template('new_comment.html', answer_id=answer_id, submission_time=submission_time, question_comment=question_comment)
    else:
        comment = request.form.to_dict()
        comment["answer_id"] = answer_id
        comment["question_id"] = None
        comment["edited_count"] = None
        question_id = data_manager.answer_comment(comment)
        return redirect('question/{}'.format(question_id))


@app.route('/search', methods=['GET'])
def search():
    searched_data = request.args.to_dict()
    question_results = []
    answer_results = []
    found_answer_data = data_manager.find_searched_data_in_answer_db(searched_data)
    if len(found_answer_data) != 0:
        answer_results.append(found_answer_data)
    found_question_data = data_manager.find_searched_data_in_question_db(searched_data)
    if len(found_question_data) != 0:
        question_results.append(found_question_data)
    return render_template('searched_data.html', question_result=question_results, answer_result=answer_results)


@app.route('/comments/<int:comment_id>/delete')
def delete_comment(comment_id):
    data_id = request.args.to_dict()
    if 'question_id' in data_id.keys():
        data_manager.delete_question_comment(comment_id)
        return redirect('question/{}'.format(data_id['question_id']))
    elif 'answer_id' in data_id.keys():
        question_id = data_manager.delete_answer_comment(comment_id, data_id)
        return redirect('question/{}'.format(question_id['question_id']))


@app.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
def edit_question_comment(comment_id):
    if request.method == 'GET':
        data_id = request.args.to_dict()
        if 'question_id' in data_id.keys():
            question_comment = True
        comment_update = True
        comment = data_manager.get_comment_by_id(comment_id)[0]
        return render_template('new_comment.html', comment_update=comment_update, comment=comment, question_comment=question_comment)
    else:
        comment_message = request.form.to_dict()
        question_id = data_manager.update_question_comment_by_id(comment_message,comment_id)
        return redirect('question/{}'.format(question_id['question_id']))




if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

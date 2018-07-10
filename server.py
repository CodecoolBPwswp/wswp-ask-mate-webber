from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/list')
def index():
    return




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
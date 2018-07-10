from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    questions =  data_manager.get_questions()
    return render_template("list.html", questions=questions)



@app.route('/question/<question_id>/new-answer', methods=['GET','POST'])
def write_answer(question_id):
    if request.method == 'GET':
        next_id = data_manager.get_next_answer_id()
        return render_template('new_answer.html', next_id=next_id, question_id=question_id)
    if request.method == 'POST':
        data = request.form.to_dict()
        return render_template('/question/<question_id>') #data ->data_man/connection ->beleírni


#unfinished
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

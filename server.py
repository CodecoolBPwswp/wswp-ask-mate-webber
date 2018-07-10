from flask import Flask, render_template, request, redirect, url_for
import data_manager


app = Flask(__name__)


@app.route('/')
@app.route('/list')
def index():
    questions =  data_manager.get_questions()
    return render_template("list.html", questions=questions)

@app.route('/add-question/', methods=['GET','POST'])
def add_question():
    if request.method == 'POST':
            new_question = {
            "id": request.form["id"],
            "submission_time":request.form["submission_time"],
            "view_number":request.form["view_number"],
            "vote_number":request.form["vote_number"],
            "title": request.form["title"],
            "message": request.form["message"],
            "image":"image"
            }
    data_manager.add_question(new_question)
    return redirect(url_for('/list'))



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )

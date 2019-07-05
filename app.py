"""
    The Tabel
"""
import datetime
import os
import tabel_analysis
import atestat_analizer
import pyexcel
import tempfile
import shutil

from flask import Flask, render_template, request, send_file, send_from_directory, session, redirect, url_for, escape
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'randomkey'

app.config['UPLOADED_PATH'] = os.path.join(app.root_path, 'upload')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/return_result')
def return_result():
    # tabel_analysis.main()

    # for path in app.config['UPLOADED_PATH']:
    grades = []
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    # for path in os.listdir(app.config['UPLOADED_PATH']):
    for path in os.listdir(session['tempdir']):
        print(path)
        # atestat = atestat_analizer.Atestat(os.path.join(app.config['UPLOADED_PATH'], path))
        atestat = atestat_analizer.Atestat(os.path.join(session['tempdir'], path))
        grades.append([atestat.grades['mean_grade']] + [grade for grade in atestat.grades['subjects_grades'].values()])
    shutil.rmtree(session['tempdir'])
    del session['tempdir']
    pyexcel.save_as(array=grades, dest_file_name=os.path.join(app.root_path, 'result.xlsx'), encoding="utf-8")



    # time.sleep(5)

    # return Response(
    #     csv,
    #     mimetype="text/csv",
    #     headers={"Content-disposition":
    #              "attachment; filename=results.csv"})

    return add_header(send_file(os.path.join(app.root_path, 'result.xlsx'), attachment_filename='result.xlsx'))
    # send_from_directory("result1.xlsx", as_attachment=True)

# @app.route('/return_result/', methods=['GET', 'POST'])
# def return_result(filename='results.csv'):
#     uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
#     return send_from_directory(directory=static, filename=filename)


@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        format = "%Y-%m-%dT%H:%M:%S"
        now = datetime.datetime.utcnow().strftime(format)

        if 'tempdir' not in session:
            tempdir = tempfile.mkdtemp()
            print("00000000000000000000000000000000000")
            session['tempdir'] = tempdir

        tempdir = session['tempdir']

        for f in request.files.getlist('file'):
            filename = secure_filename(session['username'] + now + f.filename)
            filepath = os.path.join(tempdir, filename)
            print(filepath + "EEEEEEEEEEE")
            # f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
            f.save(filepath)
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            print(username)
        session['username'] = request.form['username']
        return render_template('index.html')
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)

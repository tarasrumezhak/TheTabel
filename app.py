"""
    The Tabel
"""
import datetime
import os
import atestat_analizer
import pyexcel
import tempfile
import format_functions
import shutil

from flask import Flask, render_template, request, send_file, send_from_directory, session, redirect, url_for, escape
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'randomkey'

app.config['UPLOADED_PATH'] = os.path.join(app.root_path, 'upload')

# The idea is these headers should avoid caching (Not sure if it works). SRC - stackoverflow
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/return_result')
def return_result():
    grades = []
    for path in os.listdir(session['tempdir']):

        atestat = atestat_analizer.Atestat(os.path.join(session['tempdir'], path))
        name = format_functions.name_from_secure_name(path)
        grades.append([name] + [atestat.grades['mean_grade']] + [grade for grade in atestat.grades['subjects_grades']])
    # DELETE FILES FROM CREATED DIRECTORY

    temp_res_dir = tempfile.mkdtemp()
    session['temp_result_dir'] = temp_res_dir

    temp_res_dir = session['temp_result_dir']
    pyexcel.save_as(array=grades, dest_file_name=os.path.join(temp_res_dir, 'result.xlsx'), encoding="utf-8")

    return add_header(send_file(os.path.join(temp_res_dir, 'result.xlsx'), attachment_filename='result.xlsx'))



@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        format = "%Y-%m-%dT%H:%M:%S"
        now = datetime.datetime.utcnow().strftime(format)

        if 'tempdir' not in session.keys():
            tempdir = tempfile.mkdtemp()
            session['tempdir'] = tempdir


        tempdir = session['tempdir']

        for f in request.files.getlist('file'):
            filename = secure_filename(session['username'] + now + f.filename)
            filepath = os.path.join(tempdir, filename)
            print(filepath + "EEEEEEEEEEE")
            f.save(filepath)
    return render_template('index.html')


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            print(username)
        session['username'] = request.form['username']

        if 'tempdir' in session:
            for the_file in os.listdir(session['tempdir']):
                file_path = os.path.join(session['tempdir'], the_file)
                print("DELDELDELDELDELDDLE")
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(e)

        return render_template('index.html')

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)

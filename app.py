"""
    The Tabel
"""
import os
import tabel_analysis
import atestat_analizer
import pyexcel

from flask import Flask, render_template, request, send_file, send_from_directory

app = Flask(__name__)
app.config['UPLOADED_PATH'] = os.path.join(app.root_path, 'upload')


@app.route('/return_result')
def return_result():
    # tabel_analysis.main()

    # for path in app.config['UPLOADED_PATH']:
    grades = []
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    for path in os.listdir(app.config['UPLOADED_PATH']):
        print(path)
        atestat = atestat_analizer.Atestat(os.path.join(app.config['UPLOADED_PATH'], path))
        grades.append([atestat.grades['mean_grade']] + [grade for grade in atestat.grades['subjects_grades'].values()])
    pyexcel.save_as(array=grades, dest_file_name=os.path.join(app.root_path, 'result1.xlsx'), encoding="utf-8")



    # time.sleep(5)

    # return Response(
    #     csv,
    #     mimetype="text/csv",
    #     headers={"Content-disposition":
    #              "attachment; filename=results.csv"})

    return send_file(os.path.join(app.root_path, 'result1.xlsx'), attachment_filename='result1.xlsx')
    # send_from_directory("result1.xlsx", as_attachment=True)

# @app.route('/return_result/', methods=['GET', 'POST'])
# def return_result(filename='results.csv'):
#     uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
#     return send_from_directory(directory=static, filename=filename)


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for f in request.files.getlist('file'):
            f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

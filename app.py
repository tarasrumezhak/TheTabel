"""
    The Tabel
"""
import os
import time
import tabel_analysis

from flask import Flask, render_template, request, send_file, send_from_directory

app = Flask(__name__)
app.config['UPLOADED_PATH'] = os.path.join(app.root_path, 'upload')

@app.route('/return_result')
def return_result():
    #tabel_analysis.main()
    time.sleep(5)

    # return Response(
    #     csv,
    #     mimetype="text/csv",
    #     headers={"Content-disposition":
    #              "attachment; filename=results.csv"})
    return send_file('static/result.xlsx', attachment_filename='result.xlsx')

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

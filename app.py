#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for
# from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

from werkzeug.utils import secure_filename
from pathlib import Path
from forms import *
import process_name
import csv
import json
import os
import match_names
from io import StringIO

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
#db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

uploads_dir = f"{app.instance_path}/uploads"
Path(uploads_dir).mkdir(parents=True, exist_ok=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # save each "files" file
        for file in request.files.getlist('files'):
            file.save(os.path.join(uploads_dir, secure_filename(file.filename)))
        return redirect(url_for('upload'))
    return render_template('pages/upload.html')

@app.route('/clean')
def clean():
    '''this  page shows a list of the current files in the uploads directory'''
    file_list = os.listdir(uploads_dir)
    print (file_list)
    for file in file_list:
        print (file)
    return render_template('pages/filebrowser.html', files=file_list)

@app.route('/docviewer', methods=['GET', 'POST'])
def docviewpage():
    if request.method == 'POST':
        for item in request.form:
            print (item)
    return render_template('pages/filebrowser.html')

@app.route('/')
def home():
    return render_template('pages/upload.html')

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')

@app.route("/generate", methods=["POST"])
def generate_csv():
    with open("mapping.json") as map:
        mapping_dict = json.load(map)
    global input_filename
    gold = []
    with open("fund_sample.csv") as funds: ##TODO this should be the list of all funds
        funds_rows = csv.reader(funds)
        funds_list = [row[0] for row in funds_rows]
        #print (funds_list)
    if 'csv' in request.files:
        input_file = request.files['csv']
        # print (input_file.read().decode("utf-8"))
        reader = csv.reader(StringIO(input_file.read().decode("utf-8")), delimiter=",")
        suggestions = []
        originals = []
        input_filename = input_file.filename
        with open("input.csv", "w") as input:
            writer = csv.writer(input)
            for line in reader:
                writer.writerow(line)
                if len(line[0]) > 1:
                    if line[0] in mapping_dict:
                        gold.append(mapping_dict[line[0]])
                    elif line[0].lower() in mapping_dict:
                        gold.append(mapping_dict[line[0].lower()])
                    else:
                        gold.append("")
                    names = [x[0] for x in process_name.get_matches(line[0], funds_list, 3)]
                    suggestions.append(names)
                    originals.append(line[0])
            #res = [process_name.get_matches(line[0], funds_list, 3) for line in reader if len(line[0]) > 2]
        print(request.files["csv"].filename)
        return render_template("pages/process.html", inputs=zip(list(suggestions), originals, gold))

@app.route("/tooutput", methods=["POST"])
def generate_output():
    with open("mapping.json") as map:
        mapping_dict = json.load(map)
    with open('input.csv') as orig,  open('../output/{}.csv'.format(input_filename[:-4] + "_out"), "w") as outfile, open("fund_sample.csv", "r") as fs:
        names_and_tickers = csv.reader(fs)
        ticker_dict = {}
        for row in names_and_tickers:
            ticker_dict[row[0]] = row[1]
        original = csv.reader(orig)
        out_csv = csv.writer(outfile)
        for line in original:
            if len(line) > 0:
                corrected = request.form.get(line[0],"")
                out_csv.writerow([corrected]+line+[ticker_dict[corrected] if corrected else ""])
            else:
                out_csv.writerow(line)
    for k in request.form:
        if request.form[k] != "":
            if k.lower() not in mapping_dict:
                mapping_dict[k.lower()] = request.form[k]
    with open("mapping.json", "w") as map:
        json.dump(mapping_dict, map)
    os.system("python3 match_names.py " +  '../output/{}.csv '.format(input_filename[:-4] + "_out") + '../output/{}.csv'.format(input_filename[:-4] + "_out_matched" ))
    return render_template("pages/result.html")

@app.route('/login')
def login():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form=form)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

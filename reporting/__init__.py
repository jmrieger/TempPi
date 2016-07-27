from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

import models

@app.route('/')
def index():
	return render_template('charts.html')

@app.route('/charts/')
def charts():
    return render_template('chart.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


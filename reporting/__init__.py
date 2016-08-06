from flask import Flask, render_template, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from pprint import pprint

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from reporting import models
from reporting.models import TempPi

@app.route('/')
def index():
	batches = []
	TempPi = models.TempPi;

	for batch in db.session.query(TempPi.batchname, \
			func.min(TempPi.tstamp).label('startdate'), \
			func.max(TempPi.tstamp).label('enddate') \
		).group_by(TempPi.batchname) \
		.order_by(TempPi.tstamp.desc(), TempPi.batchname) \
		.all():
		batches.append(batch)

	return render_template('charts.html',
		batches = batches
	)

@app.route('/chart/<string:batchname>/')
def chart(batchname):
	data = db.session.query(TempPi).filter_by(batchname=batchname).all()

	return render_template('chart.html',
		batchname = batchname,
		data = data,
		jsondata = json.dumps( [itm.serialize() for itm in data ] ),
		json = json
	)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


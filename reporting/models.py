from app import db

class TempPi(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	batchname = db.Column(db.String(256), index=True)
	tempc = db.Column(db.Integer)
	tempf = db.Column(db.Integer)
	tstamp = db.Column(db.DateTime)

	def __repr__(self):
		return '<Temp %r>' % (self.batchname)

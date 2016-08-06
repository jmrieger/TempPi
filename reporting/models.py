from reporting import db
import json

class TempPi(db.Model):
	__tablename__ = 'temppi'
	tempid = db.Column(db.Integer, primary_key=True)
	batchname = db.Column(db.String(256), index=True)
	tempc = db.Column(db.Integer)
	tempf = db.Column(db.Integer)
	tstamp = db.Column(db.DateTime)

	def serialize(self):
		return {
			'tempid'	:	self.tempid,
			'batchname'	:	self.batchname,
			'tempc'		:	self.tempc,
			'tempf'		:	self.tempf,
			'tstamp'	:	self.tstamp.isoformat(),
		}

	def __repr__(self):
		return json.dumps(self.serialize())

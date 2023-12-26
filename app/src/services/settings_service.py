from db import db, ts, Keys
from services import cleaner
import dateutil.parser as dp
from datetime import datetime

def getReadingsRetention():
	retention = db.hget(Keys.getSettings(), 'retention')
	if not retention:
		return 1000 * 60 * 60 * 24 * 365 # one year
	return retention

def setReadingsRetention(retention):
	db.hset(Keys.getSettings(), 'retention', retention)

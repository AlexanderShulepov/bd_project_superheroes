import pymongo
from pymongo import MongoClient
import time
import postgresql
p_db = postgresql.open('pq://postgres:842839@localhost:5432/geo2.0')

client = MongoClient()
db = client.alarms

last_id=db.alarms.find().sort([("_id", -1)]).limit(1)[0]["_id"]
print(last_id)
while(True):
	cur_id=db.alarms.find().sort([("_id", -1)]).limit(1)[0]["_id"]
	if last_id!=cur_id:
		print(cur_id)
		alarms=db.alarms.find({"_id":{"$gt":last_id,"$lte":cur_id}})##less cur id
		for alarm in alarms:
			last_id=alarm["_id"]
			location=alarm["location"][0]
			#print(str(alarm["_id"]))
			#p_db.query("select * from addalarm(ST_GeomFromEWKT('SRID=4326;POINT("+str(location[0])+" "+str(location[1])+")'"'),"'+str(alarm["_id"])+'"  )')
			p_db.query("select * from addalarm(ST_GeomFromEWKT('SRID=4326;POINT({0} {1})'),'{2}')".format( str(location[0]), str(location[1]), str(alarm["_id"]) ))

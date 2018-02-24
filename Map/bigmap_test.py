import codecs
import postgresql
import json

p_db = postgresql.open('pq://postgres:842839@localhost:5432/geo2.0')

from flask import Flask, request, jsonify
                   
app = Flask(__name__)

import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Heroes')
m_db = conn.cursor()

def MYquery(query):	#mysql
	m_db.execute("call "+query)
	return[x for x in m_db]



html=codecs.open("bigmap_test.html", 'r').read()
@app.route('/')
def index():
    return html
        
        
@app.route('/ajax', methods = ['POST'])
def ajax_request():
    
    if request.form['type']=='1':
        ret = {"alarms": [], "heroes": [], "calls": [], "hospitals": []}
        query = p_db.query('select showall()')
        print(query)
        for dow in query:
            row = dow[0]
            nones = row.count(None)
            if nones == 0:
                ret["calls"].append([row[0],
                                     json.loads(row[1])["coordinates"],
                                     json.loads(row[2])["coordinates"],
                                     json.loads(row[3])["coordinates"],
                                     row[4]])
            elif nones == 2:
                ret["heroes"].append([row[0], json.loads(row[1])["coordinates"],row[4]])
            else:
                if row[2]!=None:
                    ret["alarms"].append(json.loads(row[2])["coordinates"])
                else:
                    ret["hospitals"].append(json.loads(row[3])["coordinates"])
        print(ret)
        return jsonify(ret)
    elif request.form['type']=='2':
        query_res = MYquery('showstathero({0})'.format(request.form['id']))
        #print ("Show hero:\n",query_res)
        return jsonify(answer=query_res)
    
    
if __name__ == "__main__":
    app.run(debug = True,host= '0.0.0.0',port=5000)

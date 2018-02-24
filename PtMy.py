import postgresql


import pymysql
p_db = postgresql.open('pq://postgres:842839@localhost:5432/geo2.0')

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Heroes')
m_db = conn.cursor()

def MYquery(query):	#mysql
	m_db.execute(query)
	return[x for x in m_db]


def Pquery(query):	#postgresq query
	return p_db.query("select "+query)

for row in Pquery("copytowalk()"):
    MYquery("select addwalk({0},{1})".format(row[0][0],row[0][1]))
    conn.commit()

for row in Pquery("copytoarch()"):
	print(row)
	hid=0
	if row[0][1]==None:
		hid=0
	else:
		hid=row[0][1]
	loc='null'
	if row[0][3]!=None:
		loc=row[0][3]
		MYquery("call addarch({0},ST_POINTFROMTEXT('{1}'),{2},ST_POINTFROMTEXT('{3}'),'{4}')".format(hid, row[0][0], row[0][2],loc,row[0][4]))
		conn.commit()

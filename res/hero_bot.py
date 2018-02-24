import time
import   json
from bson.objectid import ObjectId

from io import BytesIO
###################################		Postgres
import postgresql
p_db = postgresql.open('pq://postgres:842839@localhost:5432/geo2.0')

###################################		mongo
from pymongo import MongoClient
import gridfs

client = MongoClient()
db = client.alarms
fs = gridfs.GridFS(db)
################################### 	telegram
import telebot
from telebot import types
token = '485942541:AAHWa3SLwHizMdbPQKVr-WNHrpPEHzAbKSI'
bot = telebot.TeleBot(token)

###################################		MySQL
import pymysql
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='Heroes')
cur = conn.cursor()

###################################		Goodes
active_heroes={}

def isActive(c_id):#check for hero activity
	active=False
	if c_id  in active_heroes:
		return True
	else:
		return False

def send(id,msg,kb=None):#sending msgs to users
	if kb is None:
		bot.send_message(id, msg)
	else:
		bot.send_message(id, msg,reply_markup=kb)

def Pquery(query):	#postgresq query
	return p_db.query("select "+query)

def MYquery(query):	#mysql querygridfs collection
	cur.execute("call "+query)
	return[x for x in cur]

	

 
###################################k	eyboards
main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(types.KshowheroeyboardButton(text="update position",request_location=True))
main_keyboard.add(types.KeyboardButton(text="MyAlarms"))
main_keyboard.add(types.KeyboardButton(text="end alarm"))

empty_keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
empty_keyboard.add(types.KeyboardButton(text="nothing"))
###############################################################################################################################################################################

###################################		Command Handlers
@bot.message_handler(commands=['start','help'])
def handle_commands(message):
		if message.text=="/start":
			send(message.chat.id, "Добро пожаловать!\n /auth - для авторизации,\n /logoff - для выхода")
		elif message.text=="/help":
			send(message.chat.id, "Да прибудет с вами сила!")
		

@bot.message_handler(commands=['auth','logout'])
def handle_commands(message):
		active=isActive(message.chat.id)

		if message.text=="/auth":
			if active:
				send(message.chat.id, "Вы уже в системе, для перелога выйдите- /logout")
			else:
				send(message.chat.id, "Введите 'Логин пароль'")
				active_heroes.update({message.chat.id:{"status":"auth"}})

		elif message.text=="/logout":
			if active and  active_heroes[message.chat.id]["status"]==True:
				Pquery("logoff({0})".format(active_heroes[message.chat.id]["id"]))
				active_heroes.pop(message.chat.id,None)
				send(message.chat.id, "Bye!",empty_keyboard)

###################################		Text Handlers
@bot.message_handler(content_types=["text"])
def text_messages(message): 
		#print(message.text)
		active=isActive(message.chat.id)
		if active:
			if active_heroes[message.chat.id]["status"] == "auth":
				auth_info=message.text.split(" ")
				if len(auth_info)>1 :
					auth_res=MYquery("aut('{0}','{1}')".format(auth_info[0],auth_info[1]))
					print(auth_res)
					if auth_res[0][0]:
						active_heroes[message.chat.id].update({"id":auth_res[0][1],"speed":auth_res[0][2],"status":True })
						send(message.chat.id,"Welcome abroad!",main_keyboard)
					else:
						send(message.chat.id,"Введенные данные неверны")
				else:
					send(message.chat.id,"Введите  строку формата 'Логин пароль'")
			elif message.text == "MyAlarms":
				alarm_info=Pquery("showhero({0})".format(active_heroes[message.chat.id]["id"]))
				if alarm_info:
					alarm_info=alarm_info[0][0]##this is texted josn list('json','json','json')
					send(message.chat.id,"Цель")
					##getting coordinates by jsoning
					print(alarm_info)
					coords=json.loads(alarm_info[1])["coordinates"]
					bot.send_location(message.chat.id,coords[0],coords[1])

					send(message.chat.id,"Ближайший Госпиталь")
					coords=json.loads(alarm_info[2])["coordinates"]
					bot.send_location(message.chat.id,coords[0],coords[1])
					###getting files from alarm
					files=db.alarms.find_one({"_id": ObjectId(alarm_info[3])},{"_id":0,"location":0})
					try:
						send(message.chat.id,files.pop("text",None))###		text
					except:
						pass

					for file_type in files:
						send(message.chat.id,file_type+"'s:")
						for file_id in files[file_type]:	
							file = fs.get(file_id)
							print (file_type)
							if file_type=="photo":
								bot.send_photo(message.chat.id,file.read())
							elif file_type=="voice":
								bot.send_voice(message.chat.id,file.read())
				else:
					send(message.chat.id,"Вызовов нет")

			elif message.text == "end alarm":
				end_alarm=Pquery("endalarm({0})".format(active_heroes[message.chat.id]["id"]))
				if end_alarm[0][0]:
					send(message.chat.id,"Спасибо за вашу работу!")
				else:
					send(message.chat.id,"Что-то не так...")
				#alarm_info=json.loads(Pquery("showhero({0})".format(active_heroes[message.chat.id]["id"]))[0][0][0])
				#print(alarm_info["coordinates"])
				#bot.send_location(message.chat.id, alarm_info["coordinates"][0], alarm_info["coordinates"][1])


			

@bot.message_handler(content_types=["location"])
def loc_messages(message): 
	if isActive(message.chat.id) and active_heroes[message.chat.id]["status"]!="auth":
		print(message.location.latitude,message.location.longitude)
		Pquery("new({0},ST_GeomFromEWKT('SRID=4326;POINT({1} {2})'),{3})".format(
			active_heroes[message.chat.id]["id"],
			message.location.latitude,
			message.location.longitude, 
			active_heroes[message.chat.id]["speed"]))



###################################		Main loop
if __name__ == '__main__':
	while True:
		try:
			bot.polling(none_stop=True)
		except Exception as e:
			with open('crashlog.txt', 'w') as f:
				f.write(str(e))
		time.sleep(5)

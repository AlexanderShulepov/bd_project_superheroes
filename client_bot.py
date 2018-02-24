import time
from pymongo import MongoClient
import gridfs
import telebot
from telebot import types

token = '504695669:AAEJ_QdTIbkeBFLdRZ77f7quniZty7iAN0U'
bot = telebot.TeleBot(token)
alarms={}
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(types.KeyboardButton(text="cancel"))
keyboard.add(types.KeyboardButton(text="end"))
keyboard.add(types.KeyboardButton(text="location",request_location=True))
keyboard.add(types.KeyboardButton(text="alarm"))

client = MongoClient()
db = client.alarms
fs = gridfs.GridFS(db)
def download_files(old):
	new={}
	new.update({'location':old.pop('location')})
	if 'text' in old:
		new.update({'text':" ".join(old.pop('text'))})
	for file_type in old:
		new.update({file_type:[] })
		for file_id in old[file_type]:
				file_info = bot.get_file(file_id)
				downloaded_file = bot.download_file(file_info.file_path)
				Oid=fs.put(downloaded_file,filename=file_info.file_path.split('/')[-1])
				new[file_type].append(Oid)
	return new
@bot.message_handler(commands=['start','help'])
def handle_commands(message):
		alarmed=False
		if message.chat.id  in alarms:
			alarmed=True

		if message.text=="/start":
			bot.send_message(message.chat.id, "Добро пожаловать /alarm - для вызова помощи!",reply_markup=keyboard)
		elif message.text=="/help":
			bot.send_message(message.chat.id, "Управление кнопками")
		


@bot.message_handler(content_types=["text"])
def text_messages(message): 
		alarmed=False
		if message.chat.id  in alarms:
			alarmed=True
		if message.text=="alarm":
				if not alarmed:
					alarms.update({message.chat.id:{}})
					bot.send_message(message.chat.id, "Расскажите,что случилось!")
				else:
					bot.send_message(message.chat.id, "Да,да, продолжайте!")

		elif message.text=="cancel":
			if alarmed:
				alarms.pop(message.chat.id,None)
				bot.send_message(message.chat.id, "Берегите себя!")

		elif message.text=="end":
			if alarmed:

				if "location" not in alarms[message.chat.id] :
					bot.send_message(message.chat.id, "Нам необходима ваша позиция!")
				else:
					try:
						db.alarms.insert(download_files(alarms.pop(message.chat.id)))
					except Exception as e:
						print(e)
					bot.send_message(message.chat.id, "Держитесь,к вам уже едут!!")
					
					
		elif  alarmed:
			if "text" not in alarms[message.chat.id]:
				alarms[message.chat.id].update({"text":[]})
			alarms[message.chat.id]['text'].append(message.text)
			


#@bot.message_handler(content_types=['document'])
#def doc_messages(message):
	#if message.chat.id in alarms:
			#alarms[message.chat.id].update({"document":[]})
	#alarms[message.chat.id]["document"].append(message.document.file_id)



@bot.message_handler(content_types=["voice"])
def doc_messages(message):
	if message.chat.id in alarms:
		if "voice" not in alarms[message.chat.id]:
			alarms[message.chat.id].update({"voice":[]})
		alarms[message.chat.id]["voice"].append(message.voice.file_id)


@bot.message_handler(content_types=['photo'])
def img_messages(message):
	if message.chat.id in alarms:
		if "photo" not in alarms[message.chat.id]:
			alarms[message.chat.id].update({"photo":[]})
		alarms[message.chat.id]['photo'].append(message.photo[-1].file_id)


@bot.message_handler(content_types=["location"])
def loc_messages(message): # Название функции не играет никакой роли, в принципе
	if message.chat.id in alarms and message.text!="alarm" :
		if "location" not in alarms[message.chat.id]:
			alarms[message.chat.id].update({"location":[]})
			alarms[message.chat.id]['location'].append((message.location.latitude,message.location.longitude))
if __name__ == '__main__':
		try:
			bot.polling(none_stop=True)
		except Exception as e:
			with open('c_crashlog.txt', 'w') as f:
				f.write(str(e))
		
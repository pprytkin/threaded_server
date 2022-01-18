import socket
import threading
import random
import json
import datetime
import logging
import time

"""
def pr_bar(process, speed):
	print('      ' + process + ' ...')
	progress = progressbar.ProgressBar()
	for i in progress(range(200)):
		time.sleep(speed)
	print('Finished')
"""

def session():
	with open('sample.log') as f:
		f = f.readlines()

	last = 0

	for i in reversed(range(len(f[:-1]))):
		if f[i] == ('INFO:root:Порт пуст\n'):
			last = i
			break
	k = 0
	for i in range(last+1, len(f) - 1):
		if 'Присоединился к беседе' in f[i]:
			k += 1
	return "количество участников за последнюю сессию: " + str(k)

def open_f(file_name):
	try:
		with open(file_name, 'r') as f:
			data = json.load(f)
	except:
		with open(file_name, 'w') as f:
			json.dump({} ,f)
		with open(file_name, 'r') as f:
			data = json.load(f)
	return data


def record_f(file_name, data):
	try:
		with open(file_name, 'r') as f:
			data_old = json.load(f)
		data_old.update(data)
		with open(file_name, 'w') as f:
			json.dump(data_old ,f)
	except:
		with open(file_name, 'w') as f:
			json.dump(data ,f)


def open_t(file_name):
	file = open(file_name, 'r')
	return file
	file.close()


def record_t(file_name, line):
	file = open(file_name, 'a')
	file.write(line + ' ;\n')
	file.close()


def reader(conn, addr, lst, login):
	right = 1
	while right:
		msg = conn.recv(1024).decode()
		if msg != 'exit':
			date = str(datetime.datetime.now()).split(' ')[0]
			time = ':'.join(str(datetime.datetime.now()).split(' ')[1].split('.')[0].split(':')[:2])
			record_t('hist.txt', login + ', ' + str(addr[1]) + ', ' + date + ', ' + time + ") " + msg)
			for i in lst:
				if i != conn:
					i.send((str(addr[1])+', '+login+', '+ time + ') ' + msg).encode('utf-8'))
		else:
			print('Вышел из беседы: '+ login+ ', '+ str(addr[1])+', ' + str(addr[0]))
			logging.info( login+ ', '+ str(addr[1])+', ' + str(addr[0]) + ' вышел из беседы')
			lst.remove(conn)
			if len(lst) != 0:
				print('Количество пользователей: '+ str(len(lst)))
			else:
				print('Порт пуст, ' + session())
				logging.info('Порт пуст')
			break
	conn.close()


def main(lst,sock, port):
	conn, addr = sock.accept()

	right = 1
	try:
		data = open_t('book.txt')
	except:
		data = record_t('book.txt','')
		data = open_t('book.txt')
	nal = 'NO'
	for i in data:
		if i != ' ;\n':
			if i.split(', ')[2] == addr[0]:
				nal = 'YES'
				login = i.split(', ')[0]
	conn.send(str(nal).encode('utf-8'))
	if nal == 'YES':
		stata = open_f('stata.json')
		if stata[login] == conn.recv(1024).decode():
			conn.send('Верный пароль'.encode('utf-8'))
			record_t('book.txt', login+', '+str(port)+', '+str(addr[0])+ ', '+ str(addr[1]))
		else:
			conn.send('Не верный пароль'.encode('utf-8'))
			print('Не удалось подключиться')
			logging.info('Пользователю' + login + 'не удалось подключиться')
			right = 0
	else:
		login = conn.recv(1024).decode()
		password = conn.recv(1024).decode()
		record_f('stata.json',{login:password})
		record_t('book.txt', login+', '+str(port)+', '+str(addr[0])+ ', '+ str(addr[1]))

	if right == 1:
		threading.Thread(target  = reader, args = (conn, addr, lst,login), daemon=True).start()
		lst.append(conn)
		print('Присоединился к беседе: '+ login+ ', '+ str(addr[1])+', ' + str(addr[0]))
		logging.info('Присоединился к беседе: '+ login+ ', '+ str(addr[1])+', ' + str(addr[0]))
	print('Количество пользователей: '+ str(len(lst)))
	main(lst, sock, port)

def start(sock, l):
	global lst
	port = 8080
	while True:
		try:
			sock.bind(('', port))
			break
		except:
			port = random.randint(8080,8300)
	print("Свободный порт:", port)
	sock.listen(1)
	lst = []
	main(lst,sock, port)

sock = socket.socket()
s1 = threading.Thread(target = start, args = (sock,1), daemon = True)
s1.start()

def menu(): 
	choice = input('1 - Очищение данных\n2 - Удаление логов\n3 - Выход\n')
	if choice == '3':
		if len(lst) == 0:
			del_ = input('Вы уверены? (1 - Да, 2 - Нет)\n')
			if del_ == '1':
				sock.close()
			else:
				menu()
		else:
			print('Порт не пуст')
			menu()
	elif choice == '1':
		if len(lst) == 0:
			del_ = input('Вы уверены? (1 - Да, 2 - Нет)\n')
			if del_ == '1':

				with open('stata.json', 'w') as f:
					json.dump({}, f)
				book = open('book.txt', 'w')
				book.close()
				menu()
			else:
				print('Отмена')
				menu()
		else:
			print('Порт не пуст')
			menu()
	elif choice == '2':
		if len(lst) == 0:
			del_ = input('Вы уверены? (1 - Да, 2 - Нет)\n')
			if del_ == '1':
				f = open('sample.log','w')
				f.close()
				logging.info('Порт пуст')
			else:
				print('Отмена')
			menu()
		else:
			print('Порт не пуст')
			menu()
	else:
		print('Неверный ввод')
		menu()

logging.basicConfig(filename="sample.log", level=logging.INFO)
logging.info('Порт пуст')

menu()

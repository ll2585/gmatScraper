import csv
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.request import urlopen, urlretrieve, Request
import threading
import sqlite3
import json
import requests
from pprint import pprint
import re

dlFromForum = False
testFiles = True
scrape_from_import_io = False
testOnly =  18
sql_lock = threading.Lock()
questions_lock = threading.Lock()
questions_to_insert = {
	"DS": [],
    "PS": [],
    "SC": [],
    "RC": []
}
questions_already_in_db = {
	"DS": [],
    "PS": [],
    "SC": [],
    "RC": []
}

questions_to_update = []

ones_already_in_db = []

twos_already_in_db = []

replace_chars = {
	'â‰¥': '≥',
	'â‰': '≠',
    'â€“': '–'
}
''' TODO: Delete if confirm that is unneeded
def already_in_sql_database(filename, type):
	if type == "DS":
		#filename, question, one, two, answer, tags, post, imagepath
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute("SELECT EXISTS(SELECT 1 FROM DSQuestions WHERE filename= ?)",(filename,))
			return c.fetchone()[0] != 0
'''
def insert_questions_into_sql():
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		for type in questions_to_insert:
			if len(type) > 0:
				if type == "DS":
					to_tuple = [(dict["filename"], dict["question"], dict["1"], dict["2"], dict["answer"], json.dumps(dict["tags"]), dict["post"],  dict["imagepath"] if dict["image"] else "", dict['difficulty_percentage'], dict['question_percentage'],dict['sessions']) for dict in questions_to_insert[type]]
					c.executemany('INSERT INTO DSQuestions("filename", "question", "1", "2", "answer", "tags", "post", "imagepath", "difficulty_percentage", "question_percentage", "sessions") VALUES (?,?,?,?,?,?,?,?)', to_tuple)
	print(questions_to_insert)

def update_difficulties():
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		for type in questions_to_update:
			if len(type) > 0:
				if type == "DS":
					to_tuple = [(d["difficulty_percentage"], d["question_percentage"], d["sessions"]) for d in questions_to_update]
					c.executemany('UPDATE DSQuestions SET difficulty_percentage = ?, question_percentage = ?, sessions = ? WHERE filename = ?', to_tuple)
	print(questions_to_update)

def insert_into_sql(dict, type):
	if type == "DS":
		#filename, question, one, two, answer, tags, post, imagepath
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute("SELECT EXISTS(SELECT 1 FROM DSQuestions WHERE question= ?)",(dict['question'],))
			if c.fetchone()[0] != 0:
				print("Found!")
			else:
				c.execute('INSERT INTO DSQuestions("filename", "question", "1", "2", "answer", "tags", "post", "imagepath") VALUES (?,?,?,?,?,?,?,?)',
			          (dict["filename"], dict["question"], dict["1"], dict["2"], dict["answer"], json.dumps(dict["tags"]), dict["post"],  dict["imagepath"] if dict["image"] else ""))

def scrape_data_sufficiency(soup, filename):
	possible_1 = ["(1)", "1)", "1.", "i.", "I.", "a)", "Statement #1"]
	possible_2 = ["(2)", "2)", "2.", "ii.", "II.", "b)", "Statement #2"]
	result = {}
	difficulty = soup.find("div", {"class": "difficulty"})
	difficulty_percentage = difficulty.find("b").text
	question_stats = soup.find("div", {"class": "question"})
	bolded = question_stats.find_all("b")
	question_percentage = bolded[0].text
	sessions = bolded[2].text
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	one = "NOT FOUND"
	two = "NOT FOUND"
	has_attachment = posts.find(text='Attachment:') is not None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	try:
		answer = posts.find("div", {"class": "downRow"}).string.strip()
	except AttributeError:
		print("CHECK THIS SHIT FOR ATTRIBUTE ERROR NO ATTRIBUTE: {0}".format(filename))
		return
	if has_italics:
		found_italics = False
		last_c = ''
	for c in posts.contents:
		if question == "NOT FOUND":
			if has_italics:
				if type(c) != NavigableString:
					if c.name == 'span' and 'style' in c.attrs and c['style'] == 'font-style: italic':
						if not found_italics:
							found_italics = True
						last_c = last_c + c.string
				elif not found_italics:
					last_c = c.string
				else:
					last_c = last_c + c.string
			if '?' in str(c):
				if type(c) == NavigableString:
					to_strip = str(c)
					if has_italics:
						to_strip = last_c
					for character in replace_chars:
						if character in to_strip:
							to_strip = to_strip.replace(character, replace_chars[character])
					question = to_strip.replace('\t','').replace('\n','').strip()
				elif type(c) == Tag:
					for inner_contents in c.contents:
						if '?' in str(inner_contents):
							to_strip = str(inner_contents)
							for character in replace_chars:
								if character in to_strip:
									to_strip = to_strip.replace(character, replace_chars[character])
							question = to_strip.replace('\t','').replace('\n','').strip()
				else:
					print(type(c))
					pass
		if question != "NOT FOUND" and one == "NOT FOUND":
			for poss in possible_1:
				if one == "NOT FOUND":
					if poss in str(c):
						if type(c) == Tag:
							for z in c.contents:
								if one == "NOT FOUND":
									#print(re.split(r"(<br>|\t)", str(z)))
									#print('end reg')
									#splitted = str(z).split("<br>")
									splitted = re.split(r"(<br>|\t)", str(z))
									for strng in splitted:
										if poss in strng and  one == "NOT FOUND":
											one = strng.replace(poss, '').strip()
						else:
							one = c.string.replace(poss, '').strip()
		if question != "NOT FOUND" and one != "NOT FOUND" and two == "NOT FOUND":
			for poss in possible_2:
				if two == "NOT FOUND":
					if poss in str(c):
						if type(c) == Tag:
							for z in c.contents:
								if two == "NOT FOUND":
									splitted = str(z).split("<br>")
									splitted = re.split(r"(<br>|\t)", str(z))
									for strng in splitted:
										if poss in strng and  two == "NOT FOUND":
											two = strng.replace(poss, '').strip()
						else:
							two = c.string.replace(poss, '').strip()
	result["image"] = False
	if has_attachment:
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.jpg".format(filename.split(".html")[0])
		if "\DS" not in img_name:
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
			web_image_path = 'http://gmatclub.com/forum{0}'.format(src.find("img")["src"][1:])
			req = Request(web_image_path, headers={'User-Agent': 'Mozilla/5.0'})
			urlretrieve(web_image_path, image_path)
		result["image"] = True
		result["imagepath"] = image_path
	#print("{0}: {1}".format(filename,question))
	text = posts.getText()

	tags = soup.find("div", {"id": "taglist"})
	result['tags'] = tags.getText().split("\xa0 \xa0")
	result['post'] = text
	result['question'] = question
	result['1'] = one
	result['2'] = two
	result['answer'] = answer
	result['filename'] = filename
	if question == "NOT FOUND" or one == "NOT FOUND" or two == "NOT FOUND":
		print("CHECK THIS SHIT: {0}".format(filename))
	#pprint(result['question'])
	result['difficulty_percentage'] = difficulty_percentage
	result['question_percentage'] = question_percentage
	result['sessions'] = sessions
	return result

def scrape_file(filename, type):
	assert ".html" in filename
	'''TODO: delete if confirmed unneeded
	already_in_db = False
	sql_lock.acquire()
	try:
		already_in_db = already_in_sql_database(filename, type)
	finally:
		sql_lock.release()
	if already_in_db:
		return
	'''
	import os.path
	with open ( os.path.join(type, filename), "r" , encoding="utf-8") as myfile:
		try:
			page=myfile.read()
		except UnicodeDecodeError:
			print("{0} fucked up decoding".format(filename))
			return
	soup = BeautifulSoup(page)
	if type == "DS":
		data_sufficiency_questions = scrape_data_sufficiency(soup, filename)
		if data_sufficiency_questions is not None:
			questions_lock.acquire()
			try:
				other_questions = [d['question'] for d in questions_to_insert[type]]
				other_ones= [d['1'] for d in questions_to_insert[type]]
				other_twos= [d['2'] for d in questions_to_insert[type]]
				this_question = data_sufficiency_questions['question']
				this_one = data_sufficiency_questions['1']
				this_two = data_sufficiency_questions['2']
				if (this_question not in questions_already_in_db and this_question not in other_questions and this_question != "NOT FOUND" and
					this_one not in ones_already_in_db and this_one not in other_ones and this_one != "NOT FOUND" and
					this_two not in twos_already_in_db and this_two not in other_twos and this_two != "NOT FOUND"):
					questions_to_insert[type].append(data_sufficiency_questions)
				else:
					pass
					#print('question {0} is already in the db!'.format(this_question))
			finally:
				questions_lock.release()
		''' actually put it in memory...faster
		sql_lock.acquire()
		try:
			insert_into_sql(data_sufficiency_questions, type)
		finally:
			sql_lock.release()
		print("{0}: {1}".format(filename,data_sufficiency_questions['question']))
		print("{0}: {1}".format(filename,data_sufficiency_questions['1']))
		print("{0}: {1}".format(filename,data_sufficiency_questions['2']))
		print("{0}: {1}".format(filename,data_sufficiency_questions['answer']))
		'''

def get_files_in_db(type):
	if type == "DS":
		#filename, question, one, two, answer, tags, post, imagepath
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute("SELECT filename FROM DSQuestions")
			return c.fetchall()

def get_questions_in_db(type):
	if type == "DS":
		#filename, question, one, two, answer, tags, post, imagepath
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute("SELECT question FROM DSQuestions")
			return c.fetchall()

def get_ones_twos_in_ds():
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		c.execute("SELECT `1`, `2` FROM DSQuestions")
		return c.fetchall()

def scrape_array_of_files(tuples):
	for t in tuples:
		scrape_file(t[0], t[1])

def scrape_downloaded_posts(type):
	from os import listdir
	files = listdir(type)
	threads = []
	files_in_sql = get_files_in_db(type)
	questions_in_sql_type = get_questions_in_db(type)
	questions_already_in_db[type] = [question[0] for question in questions_in_sql_type]
	if type == "DS":
		one_twos_in_db = get_ones_twos_in_ds()
		ones_already_in_db = [question[0] for question in one_twos_in_db]
		twos_already_in_db = [question[1] for question in one_twos_in_db]
	as_array = [filename[0] for filename in files_in_sql]
	thread_limit = 10
	for_each_thread = []
	for i in range(thread_limit):
		for_each_thread.append([])
	test_limit = 300
	inserted = 0
	cur_thread = 0
	for t in files:
		if inserted == test_limit:
			break
		if t not in as_array and '.html' in t:
			for_each_thread[cur_thread].append((t,type))
			cur_thread += 1
			inserted += 1
			if cur_thread == thread_limit: cur_thread = 0
	print('starting threads')

	for thread in for_each_thread:
		threads.append(threading.Thread(target=scrape_array_of_files, args = (thread,)))

	for t in threads:
		t.start()
	for t in threads:
		t.join()
	insert_questions_into_sql()

def scrape_forum_post(type, filepath = None):
	#print ("Reading page {0}".format(link))
	file = filepath
	import os
	if filepath:
		file = filepath
		reopen = False
		with open (filepath, "r", encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				reopen = True
				print("{0} fucked up decoding".format(filepath))
	else:
		print("OOPS")
	soup = BeautifulSoup(page)
	if type == "DS":
		return scrape_data_sufficiency(soup, file)

def insert_into_sql_downloaded_link(link, full_filename):
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		c.execute("SELECT EXISTS(SELECT 1 FROM LinksDLed WHERE link = ?)",(str(link),))
		if c.fetchone()[0] != 0:
			print("Found in!")
		else:
			c.execute('INSERT INTO LinksDLed("link", "filename") VALUES (?,?)',
		          (str(link), full_filename))
			req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
			import time
			print('waiting two seconds..')
			time.sleep(2) #prevent bot capture?
			print('getting {0}'.format(link))
			urlretrieve(link, full_filename)

def download_forum_post(link, type):
	#print ("Downloading page {0}".format(link))
	import uuid
	import os.path
	filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	while os.path.isfile(filename_to_save):
		filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	full_filename = os.path.join(type, filename_to_save)
	sql_lock.acquire() #this has to be done each time in case it stops working
	try:
		insert_into_sql_downloaded_link(link, full_filename)
	finally:
		sql_lock.release()


def scrape_forum_index(link):
	print ("Reading page...")
	req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})

	page = urlopen(req).read()
	#requests_result = requests.get(link)

	soup = BeautifulSoup(page)

	titles = soup.find_all("span", "topicTitle")
	threads = []
	#dont thread it lol because it banned last time...
	for t in titles:
		new_link = t.parent["href"]
		download_forum_post(new_link,"DS")

	print ("done downloading!!")

def parse_data_sufficiency_io_posts(dict):
	quesitons = []
	for post in dict:
		result = {}
		this_url = post['pageUrl']
		'''
		result["image"] = False
		if has_attachment:
			src = posts.find("div", { "class" : "attachcontent" })
			#grab attachment
			import os.path
			img_name = "{0}-IMG-1.jpg".format(filename.split(".html")[0])
			if "\DS" not in img_name:
				image_path = os.path.join("DS", img_name)
			else:
				image_path = img_name
			if not (os.path.isfile(image_path)):
				print(filename)
				web_image_path = 'http://gmatclub.com/forum{0}'.format(src.find("img")["src"][1:])
				req = Request(web_image_path, headers={'User-Agent': 'Mozilla/5.0'})
				urlretrieve(req, image_path)
			result["image"] = True
			result["imagepath"] = image_path
		#print("{0}: {1}".format(filename,question))
		text = posts.getText()

		tags = soup.find("div", {"id": "taglist"})
		result['tags'] = tags.getText().split("\xa0 \xa0")
		result['post'] = text
		result['question'] = question
		result['1'] = one
		result['2'] = two
		result['answer'] = answer
		result['filename'] = filename
		'''
		if post['answeroption_value_1'] == '':
			continue
		else:
			post_content = post['itemtext_content']
			if post_content.find("?") == -1:
				print(post_content)
			else:
				possible_ones = ["(1)"]
				possible_twos = ["(2)"]
				answer_start = "[Reveal]"
				question = post_content[:post_content.find("?")+1]
				result['question'] = question
				result['url'] = post['pageUrl']
				result['1'] = None
				for one in possible_ones:
					if result['1'] is not None:
						break
					if one in post_content:
						one_start = post_content.find(one) + len(one)
						for two in possible_twos:
							if result['1'] is not None:
								break
							if two in post_content:
								one_end = post_content.find(two)
								result['1'] = post_content[one_start:one_end].strip()
								two_start = post_content.find(two) + len(two)
								two_end = post_content.find(answer_start)
								result['2'] = post_content[two_start:two_end].strip()
								print(result['2'])

def scrape_import_io_posts(file, type):
	dict = []
	with open(file, encoding="utf-8") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			dict.append(row)

	if type == "DS":
		parse_data_sufficiency_io_posts(dict)

if __name__ == '__main__':
	skip = False
	from requests import get
	print("getting ip")
	#ip = get('http://api.ipify.org').text
	#print ('My public ip address is:', ip)
	files = get_files_in_db("DS")
	as_array = [filename[0] for filename in files]
	print(as_array)
	#urlretrieve('https://magic.import.io/?site=http:%2F%2Fgmatclub.com%2Fforum%2Fviewtopic.php%3Ff%3D141%26t%3D106989%26view%3Dunread%26sid%3Dc9cdbc10207344ece642ae0c5bb6a189%23unread', 'blah.html')
	if not skip:
		if dlFromForum:
			#for since 2006: for i in range(2500,2400,-50):
			for i in range(1050,1000,-50):
				link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=180&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				scrape_forum_index(link)
				import time
				print('waiting two seconds')
				time.sleep(2)
		elif scrape_from_import_io:
			import_io_file = 'import_io_ds_cleaned.csv'
			scrape_import_io_posts(import_io_file, "DS")
		else:
			if testFiles:
				if testOnly is not None:
					test = scrape_forum_post("DS", filepath = "bs{0}.html".format(testOnly))
					print("{0}: {1}".format(testOnly,test['question']))
					print("{0}: {1}".format(testOnly,test['1']))
					print("{0}: {1}".format(testOnly,test['2']))
					print("{0}: {1}".format(testOnly,test['answer']))
					print("{0}: {1}".format(testOnly,json.dumps(test["tags"])))
				else:
					from os import listdir
					files = listdir('.')
					for f in files:
						if "bs" in f:
							test= scrape_forum_post("DS", filepath = f)
							print("{0}: {1}".format(f,test['question']))
							print("{0}: {1}".format(f,test['1']))
							print("{0}: {1}".format(f,test['2']))
							print("{0}: {1}".format(f,test['answer']))
			else:
				print('scraping dl')
				scrape_downloaded_posts("DS")
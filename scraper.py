import csv
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.request import urlopen, urlretrieve
import threading
import sqlite3
import json

import urllib.error
import sys
from pprint import pprint
from PyQt4 import QtGui

dlFromForum = True
testFiles = False
testOnly =  16
sql_lock = threading.Lock()

replace_chars = {
	'â‰¥': '≥',
	'â‰': '≠',
	'â€“': '–'
}

def insertIntoSql(dict, type):
	if(type == "DS"):
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

def scrapeDS(soup, filename):
	possible_1 = ["(1)", "1)", "1."]
	possible_2 = ["(2)", "2)", "2."]
	result = {}
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	one = "NOT FOUND"
	two = "NOT FOUND"
	has_attachment = posts.find(text='Attachment:') != None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	answer = posts.find("div", {"class": "downRow"}).string.strip()

	if has_italics:
		found_italics = False
		last_c = ''
	for c in posts.contents:
		if question == "NOT FOUND":
			if has_italics:
				if (type(c) != NavigableString):
					if(c.name == 'span' and 'style' in c.attrs and c['style'] == 'font-style: italic'):
						if(not found_italics):
							found_italics = True
						last_c = last_c + c.string
				elif not found_italics:
					last_c = c.string
				else:
					last_c = last_c + c.string
			if('?' in str(c)):
				if (type(c) == NavigableString):
					to_strip = str(c)
					if has_italics:
						to_strip = last_c
					for c in replace_chars:
						if(c in to_strip):
							to_strip = to_strip.replace(c, replace_chars[c])
					question = to_strip.replace('\t','').replace('\n','').strip()
				else:
					pass
		if question != "NOT FOUND" and one == "NOT FOUND":
			for poss in possible_1:
				if one == "NOT FOUND":
					if poss in str(c):
						if(type(c) == Tag):
							for z in c.contents:
								if one == "NOT FOUND":
									splitted = str(z).split("<br>")
									for strng in splitted:
										if poss in strng and  one == "NOT FOUND":
											one = strng.replace(poss, '').strip()
						else:
							one = c.string.replace(poss, '').strip()
		if question != "NOT FOUND" and one != "NOT FOUND" and two == "NOT FOUND":
			for poss in possible_2:
				if two == "NOT FOUND":
					if poss in str(c):
						if(type(c) == Tag):
							for z in c.contents:
								if two == "NOT FOUND":
									splitted = str(z).split("<br>")
									for strng in splitted:
										if poss in strng and  two == "NOT FOUND":
											two = strng.replace(poss, '').strip()
						else:
							two = c.string.replace(poss, '').strip()
	result["image"] = False
	if(has_attachment):
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.jpg".format(filename.split(".html")[0])
		if("\DS" not in img_name):
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
			print(filename)
			web_image_path = 'http://gmatclub.com/forum{0}'.format(src.find("img")["src"][1:])
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
	#pprint(result['question'])

	return result

def scrapeFile(filename, type):
	if ".html" not in filename:
		return
	import os.path
	with open ( os.path.join(type, filename), "r" , encoding="utf-8") as myfile:
		try:
			page=myfile.read()
		except UnicodeDecodeError:
			print("{0} fucked up decoding".format(filename))
			return
	soup = BeautifulSoup(page)
	if(type == "DS"):
		test = scrapeDS(soup, filename)
		sql_lock.acquire()
		try:
			insertIntoSql(test, type)
		finally:
			sql_lock.release()
		print("{0}: {1}".format(filename,test['question']))
		print("{0}: {1}".format(filename,test['1']))
		print("{0}: {1}".format(filename,test['2']))
		print("{0}: {1}".format(filename,test['answer']))

def scrapeDLedPosts(type):
	from os import listdir
	threads = []
	files = listdir(type)
	threads = []
	for t in files:
		threads.append(threading.Thread(target=scrapeFile, args = (t,type)))
	for t in threads:
		t.start()
	for t in threads:
		t.join()

def scrapeForumPost(type, filepath = None):
	#print ("Reading page {0}".format(link))
	file = link
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
	if(type == "DS"):
		return scrapeDS(soup, file)

def insertIntoSqlDLedLink(link, fullfilename):
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		print(link)
		c.execute("SELECT EXISTS(SELECT 1 FROM LinksDLed WHERE link = ?)",(str(link),))
		if c.fetchone()[0] != 0:
			print("Found in!")
		else:
			c.execute('INSERT INTO LinksDLed("link", "filename") VALUES (?,?)',
		          (str(link), fullfilename))
			urlretrieve(link, fullfilename)

def downloadForumPost(link, type):
	#print ("Downloading page {0}".format(link))
	import uuid
	import os.path
	filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	while os.path.isfile(filename_to_save):
		filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	fullfilename = os.path.join(type, filename_to_save)
	sql_lock.acquire()
	try:
		insertIntoSqlDLedLink(link, fullfilename)
	finally:
		sql_lock.release()


def scrapeForumIndex(link):
	print ("Reading page...")
	page = urlopen(link)
	soup = BeautifulSoup(page)
	titles = soup.find_all("span", "topicTitle")
	threads = []
	for t in titles:
		new_link = t.parent["href"]
		threads.append(threading.Thread(target=downloadForumPost, args = (new_link,"DS")))
	for t in threads:
		t.start()
	for t in threads:
		t.join()
	print ("done downloading!!")


def makeCSV(filename):
	with open(filename, 'rb') as html:
		soup = BeautifulSoup(html)

	rs = soup.find_all("tr", "headline")
	articles = []
	count = 1
	for a in rs:
		headline = {}
		headline['Title'] = a.a.get_text().strip()
		titletimedate = a.find("div", "leadFields").get_text()
		
		titletimedate = parseTitleTimeDate(titletimedate.split(","))

		headline['EventDate'] = titletimedate[2]
		headline['EventTime'] = titletimedate[1]
		headline['Citation'] = titletimedate[0]
		articleText = a.find("div", "snippet ensnippet")
		if(articleText):
			headline['ArticleText'] = articleText.get_text().strip()
		else:
			headline['ArticleText'] = ""
		count += 1

		articles.append(headline)

	headers = ['EventDate', 'EventTime', 'Title', 'Citation', 'ArticleText']
	import os
	noext = os.path.splitext(filename)[0]
	newfile = noext + ('.csv')
	with open(newfile, 'w', encoding = 'utf-8') as f:
		csvwriter = csv.DictWriter(f, headers, lineterminator='\n')
		csvwriter.writeheader()
		csvwriter.writerows(articles)

if __name__ == '__main__':
	for i in range(950,0,-50):
		link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=180&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
		if dlFromForum:
			scrapeForumIndex(link)
		else:
			if testFiles:
				if testOnly != None:
					test = scrapeForumPost("DS", filepath = "bs{0}.html".format(testOnly))
					print("{0}: {1}".format(testOnly,test['question']))
					print("{0}: {1}".format(testOnly,test['1']))
					print("{0}: {1}".format(testOnly,test['2']))
					print("{0}: {1}".format(testOnly,test['answer']))
				else:
					from os import listdir
					files = listdir('.')
					for f in files:
						if "bs" in f:
							test= scrapeForumPost("DS", filepath = f)
							print("{0}: {1}".format(f,test['question']))
							print("{0}: {1}".format(f,test['1']))
							print("{0}: {1}".format(f,test['2']))
							print("{0}: {1}".format(f,test['answer']))
			else:
				scrapeDLedPosts("DS")
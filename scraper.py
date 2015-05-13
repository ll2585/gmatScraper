import csv
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.request import urlopen, urlretrieve, Request
import threading
import sqlite3
import json
from pprint import pprint
import re
import shutil
import os
import http.client


sleep_delay = 1
dlFromForum = False
testFiles = False
testOnly =  8
sql_lock = threading.Lock()
questions_lock = threading.Lock()
questions_to_insert = {
	"DS": [],
    "PS": [],
    "SC": [],
    "RC": [],
    "CR": []
}
questions_already_in_db = {
	"DS": [],
    "PS": [],
    "SC": [],
    "RC": [],
    "CR": []
}

already_downloaded_urls = []

new_downloaded_urls = []

shitty_qs = []

limit_to_insert_into_sql = 100 #after every 100 downloads, insert into sql -> risk of not inserting if it crashes between 100s but it will download it anyways meaning if the program crashes when the number of downloaded is like 50, then those 50 will already have been downloaded but not inserted so they will be redownloaded next time

links_downloaded = 0

questions_to_update = []

ones_already_in_db = []

twos_already_in_db = []

replace_chars = {
	'â‰¥': '≥',
	'â‰': '≠',
    'â€“': '–'
}

def insert_questions_into_sql():
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		for type in questions_to_insert:
			if len(type) > 0:
				if type == "DS":
					to_tuple = [(dict["filename"], dict["question"], dict["1"], dict["2"], dict["answer"], json.dumps(dict["tags"]), dict["post"],  dict["imagepath"] if dict["image"] else "", dict['difficulty_percentage'], dict['question_percentage'],dict['sessions'],dict['url']) for dict in questions_to_insert[type]]
					c.executemany('INSERT INTO DSQuestions("filename", "question", "1", "2", "answer", "tags", "post", "imagepath", "difficulty_percentage", "question_percentage", "sessions","url") VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', to_tuple)
				elif type == "PS":
					to_tuple = [(dict["filename"], dict["question"], dict["A"], dict["B"], dict["C"], dict["D"], dict["E"], dict["answer"], json.dumps(dict["tags"]), dict["post"],  dict["imagepath"] if dict["image"] else "", dict['difficulty_percentage'], dict['question_percentage'],dict['sessions'],dict['url']) for dict in questions_to_insert[type]]
					c.executemany('INSERT INTO PSQuestions("filename", "question", "A", "B", "C", "D", "E", "answer", "tags", "post", "imagepath", "difficulty_percentage", "question_percentage", "sessions","url") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_tuple)
				elif type == "SC":
					to_tuple = [(dict["filename"], dict["question"], dict["A"], dict["B"], dict["C"], dict["D"], dict["E"], dict["answer"], json.dumps(dict["tags"]), dict["post"],  dict["imagepath"] if dict["image"] else "", dict['difficulty_percentage'], dict['question_percentage'],dict['sessions'],dict['url']) for dict in questions_to_insert[type]]
					c.executemany('INSERT INTO SCQuestions("filename", "question", "A", "B", "C", "D", "E", "answer", "tags", "post", "imagepath", "difficulty_percentage", "question_percentage", "sessions","url") VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', to_tuple)

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

def scrape_data_sufficiency(soup, filename):
	global shitty_qs
	possible_1 = ["(1)", "1)", "1.", "i.", "I.", "a)", "Statement #1", "I)"]
	possible_2 = ["(2)", "2)", "2.", "ii.", "II.", "b)", "Statement #2", "II)"]
	result = {}
	if soup.find("span", {"class": "font24margin2"}) is None:
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT OUT NO URL: {0}".format(filename))
		return
	url = soup.find("span", {"class": "font24margin2"}).find("a")['href']
	difficulty = soup.find("div", {"class": "difficulty"})
	if difficulty is not None and difficulty.find("b") is not None:
		difficulty_percentage = difficulty.find("b").text
	else:
		if difficulty is not None and difficulty.find("div") is not None and difficulty.find("div").contents[0].strip() == "(N/A)":
			difficulty_percentage = "N/A"
		else:
			difficulty_percentage = None
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT OUT NO DIFFICULTYT1: {0}".format(filename))
			return

	question_stats = soup.find("div", {"class": "question"})
	if question_stats is not None:
		bolded = question_stats.find_all("b")
		if bolded is not None:
			question_percentage = bolded[0].text
			sessions = bolded[2].text
		else:
			question_percentage = None
			sessions = None
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT OUT NO BOLD: {0}".format(filename))
			return
	else:
		question_percentage = None
		sessions = None
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT OUT NO questionstats: {0}".format(filename))
		return
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	one = "NOT FOUND"
	two = "NOT FOUND"
	has_attachment = posts.find(text='Attachment:') is not None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	try:
		answer = posts.find("div", {"class": "downRow"}).string.strip()
	except AttributeError:
		lukes_answer = soup.find("div", {"id": "lukes-answer"})
		if lukes_answer is not None:
			answer = lukes_answer.string
		else:
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT FOR NO ANSWER: {0}".format(filename))
			return
	if has_italics:
		found_italics = False
		last_c = ''
	try:
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
			if one == "NOT FOUND":
				for poss in possible_1:
					if one == "NOT FOUND":
						if poss in str(c):
							if question == "NOT FOUND":
								if str(c.previous_element) == '<br/>':
									prev_elem = c.previous_element
									while str(prev_elem) == '<br/>':
										prev_elem = prev_elem.previous_element
									to_strip = str(prev_elem)
									for character in replace_chars:
										if character in to_strip:
											to_strip = to_strip.replace(character, replace_chars[character])
									question = to_strip.replace('\t','').replace('\n','').strip()
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
	except TypeError:
		#print("CHECK THIS SHIT type error: {0}".format(filename))
		shitty_qs.append(filename)
		return
	result["image"] = False
	if has_attachment:
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.png".format(filename.split(".html")[0])
		if "\DS" not in img_name:
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
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
	result['url'] = url
	if question == "NOT FOUND" or one == "NOT FOUND" or two == "NOT FOUND":
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT no q 1 or 2: {0}".format(filename))
		return
	#pprint(result['question'])
	result['difficulty_percentage'] = difficulty_percentage
	result['question_percentage'] = question_percentage
	result['sessions'] = sessions
	return result


def scrape_problem_solving(soup, filename):
	global shitty_qs
	possible_A = ["A.", "(A)", "A)"]
	result = {}
	if soup.find("span", {"class": "font24margin2"}) is None:
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT OUT NO URL: {0}".format(filename))
		return
	url = soup.find("span", {"class": "font24margin2"}).find("a")['href']
	difficulty = soup.find("div", {"class": "difficulty"})
	if difficulty is not None and difficulty.find("b") is not None:
		difficulty_percentage = difficulty.find("b").text
	else:
		if difficulty is not None and difficulty.find("div") is not None and difficulty.find("div").contents[0].strip() == "(N/A)":
			difficulty_percentage = "N/A"
		else:
			difficulty_percentage = None
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT OUT NO DIFFICULTYT1: {0}".format(filename))
			return

	question_stats = soup.find("div", {"class": "question"})
	if question_stats is not None:
		bolded = question_stats.find_all("b")
		if bolded is not None:
			question_percentage = bolded[0].text
			sessions = bolded[2].text
		else:
			question_percentage = None
			sessions = None
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT OUT NO BOLD: {0}".format(filename))
			return
	else:
		question_percentage = None
		sessions = None
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT OUT NO questionstats: {0}".format(filename))
		return
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	options = {"A": "NOT FOUND", "B": "NOT FOUND", "C": "NOT FOUND", "D": "NOT FOUND", "E": "NOT FOUND"}
	has_attachment = posts.find(text='Attachment:') is not None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	try:
		answer = posts.find("div", {"class": "downRow"}).string.strip()
	except AttributeError:
		lukes_answer = soup.find("div", {"id": "lukes-answer"})
		if lukes_answer is not None:
			answer = lukes_answer.string
		else:
			shitty_qs.append(filename)
			#print("CHECK THIS SHIT FOR NO ANSWER: {0}".format(filename))
			return
	if has_italics:
		found_italics = False
		last_c = ''
	try:
		poss_found = None
		for c in posts.contents:
			if options["A"] == "NOT FOUND":
				for poss in possible_A:
					if options["A"] == "NOT FOUND":
						if poss in str(c):
							poss_found = poss
							q = ''
							first = True
							for sibs in c.previous_siblings:
								if str(sibs) != '<br/>':
									if not first:
										q = str(sibs).strip() + "\n" + str(q)
									else:
										q = str(sibs).strip()
										first = False
							question = q
							if question == "NOT FOUND":
								if str(c.previous_element) == '<br/>':
									prev_elem = c.previous_element
									while str(prev_elem) == '<br/>':
										prev_elem = prev_elem.previous_element
									to_strip = str(prev_elem)
									for character in replace_chars:
										if character in to_strip:
											to_strip = to_strip.replace(character, replace_chars[character])
									question = to_strip.replace('\t','').replace('\n','').strip()

							if type(c) == Tag:
								for z in c.contents:
									if options["A"] == "NOT FOUND":
										#print(re.split(r"(<br>|\t)", str(z)))
										#print('end reg')
										#splitted = str(z).split("<br>")
										splitted = re.split(r"(<br>|\t)", str(z))
										for strng in splitted:
											if poss in strng and  options["A"] == "NOT FOUND":
												options["A"] = strng.replace(poss, '').strip()

							else:
								options["A"] = c.string.replace(poss, '').strip()
								next_letters = ["B","C","D","E"]
								if str(c.next_element) == '<br/>':
									temp_elem = c
									for letter in next_letters:
										while(str(temp_elem.next_element) == '<br/>'):
											temp_elem = temp_elem.next_element
										this_opt = str(temp_elem.next_element)
										options[letter] = this_opt.replace(poss.replace("A", letter), '').strip()
										temp_elem = temp_elem.next_element
	except TypeError:
		#print("CHECK THIS SHIT type error: {0}".format(filename))
		shitty_qs.append(filename)
		return
	result["image"] = False
	if has_attachment:
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.png".format(filename.split(".html")[0])
		if "\DS" not in img_name:
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
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
	result['A'] = options["A"]
	result["B"] = options["B"]
	result["C"] = options["C"]
	result["D"] = options["D"]
	result["E"] = options["E"]
	result['answer'] = answer
	result['filename'] = filename
	result['url'] = url
	to_not_be_not_found = [question, options["A"], options["B"], options["C"], options["D"], options["E"]]
	if "NOT FOUND" in to_not_be_not_found:
		shitty_qs.append(filename)
		#print("CHECK THIS SHIT no q 1 or 2: {0}".format(filename))
		return
	#pprint(result['question'])
	result['difficulty_percentage'] = difficulty_percentage
	result['question_percentage'] = question_percentage
	result['sessions'] = sessions
	return result

def scrape_sentence_correction(soup, filename):
	global shitty_qs
	print_shit = False

	possible_A = ["A.", "(A)", "A)"]
	result = {}
	if soup.find("span", {"class": "font24margin2"}) is None:
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT OUT NO URL: {0}".format(filename))
		return
	url = soup.find("span", {"class": "font24margin2"}).find("a")['href']
	difficulty = soup.find("div", {"class": "difficulty"})
	if difficulty is not None and difficulty.find("b") is not None:
		difficulty_percentage = difficulty.find("b").text
	else:
		if difficulty is not None and difficulty.find("div") is not None and difficulty.find("div").contents[0].strip() == "(N/A)":
			difficulty_percentage = "N/A"
		else:
			difficulty_percentage = None
			shitty_qs.append(filename)
			if print_shit: print("CHECK THIS SHIT OUT NO DIFFICULTYT1: {0}".format(filename))
			return

	question_stats = soup.find("div", {"class": "question"})
	if question_stats is not None:
		bolded = question_stats.find_all("b")
		if bolded is not None:
			question_percentage = bolded[0].text
			sessions = bolded[2].text
		else:
			question_percentage = None
			sessions = None
			shitty_qs.append(filename)
			if print_shit: print("CHECK THIS SHIT OUT NO BOLD: {0}".format(filename))
			return
	else:
		question_percentage = None
		sessions = None
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT OUT NO questionstats: {0}".format(filename))
		return
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	options = {"A": "NOT FOUND", "B": "NOT FOUND", "C": "NOT FOUND", "D": "NOT FOUND", "E": "NOT FOUND"}
	has_attachment = posts.find(text='Attachment:') is not None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	answer = None
	possible_answers = ["A","B","C","D","E"]
	for p in possible_answers:
		test = "{0}'.toLowerCase".format(p)
		if str(soup).find(test) != -1:
			answer = p
			break
	if answer is None:
		try:
			answer = posts.find("div", {"class": "downRow"}).string.strip()
		except AttributeError:
			lukes_answer = soup.find("div", {"id": "lukes-answer"})
			if lukes_answer is not None:
				answer = lukes_answer.string
			else:
				shitty_qs.append(filename)
				if print_shit: print("CHECK THIS SHIT FOR NO ANSWER: {0}".format(filename))
				return
	if has_italics:
		found_italics = False
		last_c = ''
	try:
		poss_found = None
		for c in posts.contents:
			if options["A"] == "NOT FOUND":
				for poss in possible_A:
					if options["A"] == "NOT FOUND":
						if poss in str(c):
							if type(c) != Tag:
								q = ''
								first = True
								for sibs in c.previous_siblings:
									if str(sibs) != '<br/>':
										if not first:
											q = str(sibs).strip() + "\n" + str(q)
										else:
											q = str(sibs).strip()
											first = False
								question = q
								if question == "NOT FOUND":
									if str(c.previous_element) == '<br/>':
										prev_elem = c.previous_element
										while str(prev_elem) == '<br/>':
											prev_elem = prev_elem.previous_element
										to_strip = str(prev_elem)
										for character in replace_chars:
											if character in to_strip:
												to_strip = to_strip.replace(character, replace_chars[character])
										question = to_strip.replace('\t','').replace('\n','').strip()

							if type(c) == Tag:
								for z in c.contents:
									if options["A"] == "NOT FOUND":
										#print(re.split(r"(<br>|\t)", str(z)))
										#print('end reg')
										#splitted = str(z).split("<br>")
										splitted = re.split(r"(<br>|\t)", str(z))
										for strng in splitted:
											if poss in strng and options["A"] == "NOT FOUND":
												if question == "NOT FOUND":
													first = True
													q = None
													for sibs in z.previous_siblings:
														if str(sibs) != '<br/>':
															if not first:
																q = str(sibs).strip() + "\n" + str(q)
															else:
																q = str(sibs).strip()
																first = False
													if q is not None:
														question = q
													else:
														shitty_qs.append(filename)
														print("FUCK NO Q AGAIN: {0}".format(filename))
												options["A"] = strng.replace(poss, '').strip()
												next_letters = ["B","C","D","E"]
												possible_brs = ['<br/>', '<br>']
												if str(z.next_element) in possible_brs:
													temp_elem = z
													for letter in next_letters:
														while(str(temp_elem.next_element) in possible_brs):
															temp_elem = temp_elem.next_element
														this_opt = str(temp_elem.next_element)
														options[letter] = this_opt.replace(poss.replace("A", letter), '').strip()
														temp_elem = temp_elem.next_element

							else:
								options["A"] = c.string.replace(poss, '').strip()
								next_letters = ["B","C","D","E"]
								possible_brs = ['<br/>', '<br>']
								if str(c.next_element) in possible_brs:
									temp_elem = c

									for letter in next_letters:
										while(str(temp_elem.next_element) in possible_brs):
											temp_elem = temp_elem.next_element
										this_opt = str(temp_elem.next_element)
										options[letter] = this_opt.replace(poss.replace("A", letter), '').strip()
										temp_elem = temp_elem.next_element
	except TypeError:
		if print_shit: print("CHECK THIS SHIT type error: {0}".format(filename))
		shitty_qs.append(filename)
		return
	result["image"] = False
	if has_attachment:
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.png".format(filename.split(".html")[0])
		if "\DS" not in img_name:
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
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
	result['A'] = options["A"]
	result["B"] = options["B"]
	result["C"] = options["C"]
	result["D"] = options["D"]
	result["E"] = options["E"]
	result['answer'] = answer
	result['filename'] = filename
	result['url'] = url
	to_not_be_not_found = [question, options["A"], options["B"], options["C"], options["D"], options["E"]]
	if "NOT FOUND" in to_not_be_not_found:
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT no q 1 or 2: {0}; HERE THEY ARE: {1}".format(filename,to_not_be_not_found))
		return
	#pprint(result['question'])
	result['difficulty_percentage'] = difficulty_percentage
	result['question_percentage'] = question_percentage
	result['sessions'] = sessions
	return result

def scrape_critical_reading(soup, filename):
	global shitty_qs
	print_shit = False

	possible_A = ["A.", "(A)", "A)"]
	result = {}
	if soup.find("span", {"class": "font24margin2"}) is None:
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT OUT NO URL: {0}".format(filename))
		return
	url = soup.find("span", {"class": "font24margin2"}).find("a")['href']
	difficulty = soup.find("div", {"class": "difficulty"})
	if difficulty is not None and difficulty.find("b") is not None:
		difficulty_percentage = difficulty.find("b").text
	else:
		if difficulty is not None and difficulty.find("div") is not None and difficulty.find("div").contents[0].strip() == "(N/A)":
			difficulty_percentage = "N/A"
		else:
			difficulty_percentage = None
			shitty_qs.append(filename)
			if print_shit: print("CHECK THIS SHIT OUT NO DIFFICULTYT1: {0}".format(filename))
			return

	question_stats = soup.find("div", {"class": "question"})
	if question_stats is not None:
		bolded = question_stats.find_all("b")
		if bolded is not None:
			question_percentage = bolded[0].text
			sessions = bolded[2].text
		else:
			question_percentage = None
			sessions = None
			shitty_qs.append(filename)
			if print_shit: print("CHECK THIS SHIT OUT NO BOLD: {0}".format(filename))
			return
	else:
		question_percentage = None
		sessions = None
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT OUT NO questionstats: {0}".format(filename))
		return
	posts = soup.find("div", { "class" : "item text" }) #find returns the first 1 and the Q is the first post
	question="NOT FOUND"
	options = {"A": "NOT FOUND", "B": "NOT FOUND", "C": "NOT FOUND", "D": "NOT FOUND", "E": "NOT FOUND"}
	has_attachment = posts.find(text='Attachment:') is not None
	has_italics = len(posts.find_all("span", {"style": "font-style: italic"})) > 0
	answer = None
	possible_answers = ["A","B","C","D","E"]
	for p in possible_answers:
		test = "{0}'.toLowerCase".format(p)
		if str(soup).find(test) != -1:
			answer = p
			break
	if answer is None:
		try:
			answer = posts.find("div", {"class": "downRow"}).string.strip()
		except AttributeError:
			lukes_answer = soup.find("div", {"id": "lukes-answer"})
			if lukes_answer is not None:
				answer = lukes_answer.string
			else:
				shitty_qs.append(filename)
				if print_shit: print("CHECK THIS SHIT FOR NO ANSWER: {0}".format(filename))
				return
	if has_italics:
		found_italics = False
		last_c = ''
	try:
		poss_found = None
		for c in posts.contents:
			if options["A"] == "NOT FOUND":
				for poss in possible_A:
					if options["A"] == "NOT FOUND":
						if poss in str(c):
							if type(c) != Tag:
								q = ''
								first = True
								for sibs in c.previous_siblings:
									if str(sibs) != '<br/>':
										if not first:
											q = str(sibs).strip() + "\n" + str(q)
										else:
											q = str(sibs).strip()
											first = False
								question = q
								if question == "NOT FOUND":
									if str(c.previous_element) == '<br/>':
										prev_elem = c.previous_element
										while str(prev_elem) == '<br/>':
											prev_elem = prev_elem.previous_element
										to_strip = str(prev_elem)
										for character in replace_chars:
											if character in to_strip:
												to_strip = to_strip.replace(character, replace_chars[character])
										question = to_strip.replace('\t','').replace('\n','').strip()

							if type(c) == Tag:
								for z in c.contents:
									if options["A"] == "NOT FOUND":
										#print(re.split(r"(<br>|\t)", str(z)))
										#print('end reg')
										#splitted = str(z).split("<br>")
										splitted = re.split(r"(<br>|\t)", str(z))
										for strng in splitted:
											if poss in strng and options["A"] == "NOT FOUND":
												if question == "NOT FOUND":
													first = True
													q = None
													for sibs in z.previous_siblings:
														if str(sibs) != '<br/>':
															if not first:
																q = str(sibs).strip() + "\n" + str(q)
															else:
																q = str(sibs).strip()
																first = False
													if q is not None:
														question = q
													else:
														shitty_qs.append(filename)
														print("FUCK NO Q AGAIN: {0}".format(filename))
												options["A"] = strng.replace(poss, '').strip()
												next_letters = ["B","C","D","E"]
												possible_brs = ['<br/>', '<br>']
												if str(z.next_element) in possible_brs:
													temp_elem = z
													for letter in next_letters:
														while(str(temp_elem.next_element) in possible_brs):
															temp_elem = temp_elem.next_element
														this_opt = str(temp_elem.next_element)
														options[letter] = this_opt.replace(poss.replace("A", letter), '').strip()
														temp_elem = temp_elem.next_element

							else:
								options["A"] = c.string.replace(poss, '').strip()
								next_letters = ["B","C","D","E"]
								possible_brs = ['<br/>', '<br>']
								if str(c.next_element) in possible_brs:
									temp_elem = c

									for letter in next_letters:
										while(str(temp_elem.next_element) in possible_brs):
											temp_elem = temp_elem.next_element
										this_opt = str(temp_elem.next_element)
										options[letter] = this_opt.replace(poss.replace("A", letter), '').strip()
										temp_elem = temp_elem.next_element
	except TypeError:
		if print_shit: print("CHECK THIS SHIT type error: {0}".format(filename))
		shitty_qs.append(filename)
		return
	result["image"] = False
	if has_attachment:
		src = posts.find("div", { "class" : "attachcontent" })
		#grab attachment
		import os.path
		img_name = "{0}-IMG-1.png".format(filename.split(".html")[0])
		if "\DS" not in img_name:
			image_path = os.path.join("DS", img_name)
		else:
			image_path = img_name
		if not (os.path.isfile(image_path)):
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
	result['A'] = options["A"]
	result["B"] = options["B"]
	result["C"] = options["C"]
	result["D"] = options["D"]
	result["E"] = options["E"]
	result['answer'] = answer
	result['filename'] = filename
	result['url'] = url
	to_not_be_not_found = [question, options["A"], options["B"], options["C"], options["D"], options["E"]]
	if "NOT FOUND" in to_not_be_not_found:
		shitty_qs.append(filename)
		if print_shit: print("CHECK THIS SHIT no q 1 or 2: {0}; HERE THEY ARE: {1}".format(filename,to_not_be_not_found))
		return
	#pprint(result['question'])
	result['difficulty_percentage'] = difficulty_percentage
	result['question_percentage'] = question_percentage
	result['sessions'] = sessions
	return result

def scrape_file(filename, type):
	global questions_to_insert
	assert ".html" in filename
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
				if (this_question not in questions_already_in_db[type] and this_question not in other_questions and this_question != "NOT FOUND" and
					this_one not in ones_already_in_db and this_one not in other_ones and this_one != "NOT FOUND" and
					this_two not in twos_already_in_db and this_two not in other_twos and this_two != "NOT FOUND"):
					questions_to_insert[type].append(data_sufficiency_questions)
				else:
					pass
					#print('question {0} is already in the db!'.format(this_question))
			finally:
				questions_lock.release()
	elif type == "PS":
		problem_solving_questions = scrape_problem_solving(soup, filename)
		if problem_solving_questions is not None:
			questions_lock.acquire()
			try:
				other_questions = [d['question'] for d in questions_to_insert[type]]
				this_question = problem_solving_questions['question']
				if this_question not in questions_already_in_db[type] and this_question not in other_questions and this_question != "NOT FOUND":
					questions_to_insert[type].append(problem_solving_questions)
				else:
					pass
					#print('question {0} is already in the db!'.format(this_question))
			finally:
				questions_lock.release()
	elif type == "SC":
		sentence_correction_questions = scrape_sentence_correction(soup, filename)
		if sentence_correction_questions is not None:
			questions_lock.acquire()
			try:
				other_questions = [d['question'] for d in questions_to_insert[type]]
				this_question = sentence_correction_questions['question']
				if this_question not in questions_already_in_db[type] and this_question not in other_questions and this_question != "NOT FOUND":
					questions_to_insert[type].append(sentence_correction_questions)
				else:
					move_file_to(filename, type, "NotDownloaded/{0}".format(type))
			finally:
				questions_lock.release()

def get_files_in_db(type):
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		if type == "DS":
			c.execute("SELECT filename FROM DSQuestions")
		elif type == "PS":
			c.execute("SELECT filename FROM PSQuestions")
		elif type == "SC":
			c.execute("SELECT filename FROM SCQuestions")
		return c.fetchall()

def get_questions_in_db(type):
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		if type == "DS":
			c.execute("SELECT question FROM DSQuestions")
		elif type == "PS":
			c.execute("SELECT question FROM PSQuestions")
		elif type == "SC":
			c.execute("SELECT question FROM SCQuestions")
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
	downloaded_url_filenames_in_sql = [f[0] for f in get_downloaded_filenames()]
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
	test_limit = 10
	inserted = 0
	cur_thread = 0
	for t in files:
		if inserted == test_limit:
			break
		if t not in as_array and '.html' in t and t in downloaded_url_filenames_in_sql:
			for_each_thread[cur_thread].append((t,type))
			cur_thread += 1
			inserted += 1
			if cur_thread == thread_limit: cur_thread = 0
		elif t in as_array:
			move_file_to(t, type, "InsertedQs/{0}".format(type))
			#update with difficult
		elif t not in downloaded_url_filenames_in_sql and ".html" in t:
			move_file_to(t, type, "NotDownloaded/{0}".format(type))
		else:
			print("WHAT IS THIS {0}".format(t))
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
		with open (filepath, "r", encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				print("{0} fucked up decoding".format(filepath))
	else:
		print("OOPS")
	soup = BeautifulSoup(page)
	if type == "DS":
		return scrape_data_sufficiency(soup, file)
	elif type == "PS":
		return scrape_problem_solving(soup, file)
	elif type == "SC":
		return scrape_sentence_correction(soup, file)

def insert_into_sql_downloaded_links():
	print("updating sql with downloaded links")
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		to_tuple = [(dict["link"], dict["filename"]) for dict in new_downloaded_urls]
		c.executemany('INSERT INTO LinksDLed("link", "filename") VALUES (?,?)', to_tuple)


def download_forum_post(link, type):
	#print ("Downloading page {0}".format(link))
	import uuid
	import os.path
	filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	while os.path.isfile(filename_to_save):
		filename_to_save = "{0}_{1}.html".format(type,uuid.uuid4())
	full_filename = os.path.join(type, filename_to_save)
	import time
	time.sleep(sleep_delay) #because ban -> 5 seconds if sleeping, should be enough to not be a bot...
	try:
		urlretrieve(link, full_filename)
	except http.client.BadStatusLine:
		print("{0} raised an error downloading".format(link))
	return full_filename

def get_downloaded_urls():
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		c.execute("SELECT link FROM LinksDLed")
		return c.fetchall()

def get_downloaded_filenames():
	#filename, question, one, two, answer, tags, post, imagepath
	conn = sqlite3.connect('db.db')
	with conn:
		c = conn.cursor()
		c.execute("SELECT substr(filename,4) FROM LinksDLed")
		return c.fetchall()

def scrape_forum_index(link, type):
	global links_downloaded
	global already_downloaded_urls
	global new_downloaded_urls
	print ("Reading page...")
	req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})

	page = urlopen(req).read()
	#requests_result = requests.get(link)
	print(page)
	soup = BeautifulSoup(page)

	titles = soup.find_all("span", "topicTitle")
	threads = []
	#dont thread it lol because it banned last time...
	print("titles are {0}".format(titles))

	for t in titles:
		new_link = t.parent["href"]
		links_of_downloaded = [newly_downloaded["link"] for newly_downloaded in new_downloaded_urls]
		if new_link not in already_downloaded_urls and new_link not in links_of_downloaded:
			print("grabbing {0}".format(new_link))
			new_filename = download_forum_post(new_link,type)
			new_downloaded_urls.append({"link": new_link, "filename": new_filename} )
			links_downloaded += 1
			if links_downloaded == limit_to_insert_into_sql:
				links_downloaded = 0
				insert_into_sql_downloaded_links()
				already_downloaded_urls += links_of_downloaded
				new_downloaded_urls = []
	insert_into_sql_downloaded_links()

	print ("done downloading!!")

def move_file_to(filename, original_subdir, final_subdir):
	dir = os.path.dirname(__file__)
	file_path = os.path.join(os.path.join(dir, original_subdir), filename)
	new_path = os.path.join(os.path.join(dir, final_subdir), filename)
	shutil.move(file_path, new_path)

if __name__ == '__main__':
	skip = False
	from requests import get
	print("getting ip")
	ip = get('http://api.ipify.org').text
	print ('My public ip address is:', ip)
	files = get_files_in_db("DS")
	as_array = [filename[0] for filename in files]
	#print(as_array)
	#urlretrieve('https://magic.import.io/?site=http:%2F%2Fgmatclub.com%2Fforum%2Fviewtopic.php%3Ff%3D141%26t%3D106989%26view%3Dunread%26sid%3Dc9cdbc10207344ece642ae0c5bb6a189%23unread', 'blah.html')
	if not skip:
		if dlFromForum:
			already_downloaded_urls = [s[0] for s in get_downloaded_urls()]
			#for since 2006: for i in range(2500,2400,-50):
			for i in range(950,0,-50):
				'''
				###DS####
				link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=222&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				scrape_forum_index(link, "DS")
				import time
				print('finished {0} now waiting 1 seconds'.format(i))
				time.sleep(sleep_delay)


				######PS####
				link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=216&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				scrape_forum_index(link, "PS")
				import time
				print('finished {0} now waiting 5 seconds'.format(i))
				time.sleep(sleep_delay)


				######SC####
				#link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=172&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				#^ tghat is the hard one do these ones after you get home
				link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=172&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				scrape_forum_index(link, "SC")
				import time
				print('finished {0} now waiting 5 seconds'.format(i))
				time.sleep(sleep_delay)
				'''

				#####CR#####
				#link: http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=168&similar_to_id=0&search_tags=any&search_id=tag&start=2500
				#link = "http://gmatclub.com/forum/search.php?st=0&sk=t&sd=d&sr=topics&search_id=tag&tag_id=226&similar_to_id=0&search_tags=any&search_id=tag&start=" + str(i)
				#scrape_forum_index(link, "CR")
				#import time
				#print('finished {0} now waiting 5 seconds'.format(i))
				#time.sleep(sleep_delay)

				###RC Not many RC so just do it all
				link = "http://gmatclub.com/forum/gmat-reading-comprehension-rc-137/index-{0}.html".format(str(i))
				scrape_forum_index(link, "RC")
				import time
				print('finished {0} now waiting 5 seconds'.format(i))
				time.sleep(sleep_delay)
		else:
			if testFiles:
				if testOnly is not None:
					test = scrape_forum_post("SC", filepath = "bs{0}.html".format(testOnly))
					print("{0}: {1}".format(testOnly,test['question']))
					print("{0}: {1}".format(testOnly,test['A']))
					print("{0}: {1}".format(testOnly,test['B']))
					print("{0}: {1}".format(testOnly,test['C']))
					print("{0}: {1}".format(testOnly,test['D']))
					print("{0}: {1}".format(testOnly,test['E']))
					print("{0}: {1}".format(testOnly,test['answer']))
					print("{0}: {1}".format(testOnly,json.dumps(test["tags"])))
					print("{0}: {1}".format(testOnly,test['difficulty_percentage']))
					print("{0}: {1}".format(testOnly,test['question_percentage']))
					print("{0}: {1}".format(testOnly,test["sessions"]))
				else:
					from os import listdir
					files = listdir('.')
					for f in files:
						if "bs" in f:
							test= scrape_forum_post("SC", filepath = f)
							print("{0}: {1}".format(f,test['question']))
							print("{0}: {1}".format(f,test['A']))
							print("{0}: {1}".format(f,test['B']))
							print("{0}: {1}".format(f,test['C']))
							print("{0}: {1}".format(f,test['D']))
							print("{0}: {1}".format(f,test['E']))
							print("{0}: {1}".format(f,test['answer']))
			else:
				print('scraping dl')
				scrape_downloaded_posts("SC")
				for q in shitty_qs:
					move_file_to(q, "SC", "ShittyQs/SC")
					#print(q)
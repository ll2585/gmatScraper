from os import listdir, rename
import os
from bs4 import BeautifulSoup, NavigableString, Tag
import sqlite3
def scrape_image_ds():
	filenames = []
	q_type = "DS"
	rescrape_text = "ds_files_rescrape.txt"
	with open (rescrape_text, "r" , encoding="utf-8") as myfile:
		for f in myfile.readlines():
			filenames.append(f.replace('"','').strip())
	print(filenames)
	for f in filenames:
		with open ( os.path.join(q_type, f), "r" , encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				print("{0} fucked up decoding".format(f))
				return
		soup = BeautifulSoup(page)
		ones = "1)"
		temp = soup.find("div", {"class": "attachcontent"}).next_sibling
		q = ''
		while True:
			q += str(temp)
			temp = temp.next_sibling
			if ones in str(temp):
				break
		new_q = q.replace("<br/>","")
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute('UPDATE DSQuestions SET question = ? WHERE filename = ?', (new_q,f))

def fix_twos():
	filenames = []
	q_type = "DS"
	rescrape_text = "ds_fix_2s.txt"
	with open (rescrape_text, "r" , encoding="utf-8") as myfile:
		for f in myfile.readlines():
			filenames.append(f.replace('"','').strip())
	print(filenames)
	for f in filenames:
		with open ( os.path.join(q_type, f), "r" , encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				print("{0} fucked up decoding".format(f))
				return
		soup = BeautifulSoup(page)
		ones = "(1)"
		twos = "(2)"
		temp = soup.find("div", {"class": "item text"})
		found_1 = True
		found_2 = False
		for t in temp:
			if ones in t:
				found_1 = True
			if twos in t and found_1 and t[:3] == twos:
				found_2 = True
				new_2 = t[4:]
				conn = sqlite3.connect('db.db')
				with conn:
					c = conn.cursor()
					c.execute('UPDATE DSQuestions SET `2` = ? WHERE filename = ?', (new_2,f))
		if not found_2:
			print(f)
		if not found_1:
			print("NO 1", f)

def scrape_image_ps():
	filenames = []
	q_type = "PS"
	rescrape_text = "ps_remove_imgs.txt"
	with open (rescrape_text, "r" , encoding="utf-8") as myfile:
		for f in myfile.readlines():
			filenames.append(f.replace('"','').strip())
	print(filenames)
	for f in filenames:
		with open ( os.path.join(q_type, f), "r" , encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				print("{0} fucked up decoding".format(f))
				return
		soup = BeautifulSoup(page)
		all_as = ["A. ", "(A)", "A.", "A)"]
		temp = soup.find("div", {"class": "attachcontent"}).next_sibling
		q = ''
		found_a = False
		while True:
			q += str(temp)
			temp = temp.next_sibling
			for a in all_as:
				if a in str(temp)[:len(a)]:
					found_a = True
					break
			if temp is None:
				break
			elif found_a:
				break
		if not found_a:
			print(f)
		while q[:5] == "<br/>":
			q = q[5:]
		while q[-5:] == "<br/>":
			q = q[:-5]
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute('UPDATE PSQuestions SET question = ? WHERE filename = ?', (q,f))

def fix_sc_breaks():
	filenames = []
	q_type = "InsertedQs\SC"
	rescrape_text = "sc_2.txt"
	with open (rescrape_text, "r" , encoding="utf-8") as myfile:
		for f in myfile.readlines():
			filenames.append(f.replace('"','').strip())
	print(filenames)
	for f in filenames:
		with open ( os.path.join(q_type, f), "r" , encoding="utf-8") as myfile:
			try:
				page=myfile.read()
			except UnicodeDecodeError:
				print("{0} fucked up decoding".format(f))
				return
		soup = BeautifulSoup(page)
		letters = ["A", "B", "C", "D", "E"]
		all_as = ["(A).", "(A)", "A.)", "* (A)", "A.","a)","a. "]
		all_bs = []
		all_cs = []
		all_ds = []
		all_es = []
		for a in all_as:
			all_bs.append(a.replace("A","B").replace("a","b"))
			all_cs.append(a.replace("A","C").replace("a","c"))
			all_ds.append(a.replace("A","D").replace("a","d"))
			all_es.append(a.replace("A","E").replace("a","e"))
		all_arrs = [all_as, all_bs, all_cs, all_ds, all_es]
		temp = soup.find("div", {"class": "item text"})
		found_arr = [False] * len(letters)

		options = [''] * len(letters)
		cur_index = 0
		e_limit = 3
		e_cur_limit = 0
		for t in temp:
			if 'onclick="hide(' in str(t) or e_cur_limit == e_limit:
				break
			found_in_t = False
			if cur_index < len(all_arrs):
				for a in all_arrs[cur_index]:
					check_for = str(t).strip()
					if f == 'SC_277416db-2a51-4fd8-8c42-666fce0ffbbd.html':
						print(a,check_for[:len(a)],a==check_for[:len(a)])
					if a == check_for[:len(a)]:
						found_arr[cur_index] = True
						options[cur_index] += check_for[len(a):].replace("<br/>"," ").replace("\t","").replace("  ", " ").strip()
						cur_index += 1
						if cur_index == len(all_arrs):
							e_cur_limit += 1
						found_in_t = True
						break
			if cur_index > 0 and found_arr[cur_index-1] and not found_in_t:
				if cur_index == len(all_arrs):
					e_cur_limit += 1
				if options[cur_index-1] != '' and str(t).replace("\t", "").replace("<br/>"," ").replace("  ", " ").strip() != '' and options[cur_index-1][-1:] != ' ':
					options[cur_index-1] += ' '
				options[cur_index-1] += str(t).replace("\t", "").replace("<br/>"," ").replace("  ", " ").strip()
		if not found_arr[0]:
			print(f)
		print(f,options[4])
		'''
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			c.execute('UPDATE SCQuestions SET A = ? WHERE filename = ?', (options[0],f))
			c.execute('UPDATE SCQuestions SET B = ? WHERE filename = ?', (options[1],f))
			c.execute('UPDATE SCQuestions SET C = ? WHERE filename = ?', (options[2],f))
			c.execute('UPDATE SCQuestions SET D = ? WHERE filename = ?', (options[3],f))
			c.execute('UPDATE SCQuestions SET E = ? WHERE filename = ?', (options[4],f))
		'''

fix_sc_breaks()
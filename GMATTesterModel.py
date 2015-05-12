import sqlite3
import time

class GMATTesterModel():
	def __init__(self):
		self.reset()

	def get_question(self):
		import random
		possible_pool = []
		for type in self.settings["questions_to_get"]:
			if self.settings["questions_to_get"][type]:
				possible_pool += self.question_ids[type]
		self.cur_question = random.choice(possible_pool)
		return {"id": self.cur_question.id,
		        "question" : self.cur_question.question,
		        "a": self.cur_question.answers[0],
		        "b": self.cur_question.answers[1],
		        "c": self.cur_question.answers[2],
		        "d": self.cur_question.answers[3],
		        "e": self.cur_question.answers[4],
		        "difficulty": self.cur_question.difficulty_bin_1,
		        "number_correct": self.cur_question.difficulty_bin_2,
		        "has_image": self.cur_question.image != "",
		        "image_path": self.cur_question.image,
		        "flagged": self.cur_question.flagged}

	def get_answer(self):
		return self.cur_question.answer

	def load_questions_from_sql(self):
		conn = sqlite3.connect('db.db')
		ds_questions = []
		ps_questions = []
		with conn:
			c = conn.cursor()
			c.execute("SELECT * FROM DSQuestions") #do the others later too
			ds_qs = c.fetchall()
			c.execute("SELECT * FROM PSQuestions") #do the others later too
			ps_qs = c.fetchall()
		for d in ds_qs:
			this_question = Question(
				id = d[0],
				question = "{0}\n\n(1) {1}\n(2) {2}".format(d[2],d[3], d[4]),
				source = d[9],
				answers = ["Statement (1) ALONE is sufficient, but statement (2) alone is not sufficient",
				           "Statement (2) ALONE is sufficient, but statement (1) alone is not sufficient",
				           "BOTH statements TOGETHER are sufficient, but NEITHER statement ALONE is sufficient",
				           "EACH statement ALONE is sufficient",
				           "Statements (1) and (2) TOGETHER are NOT sufficient"], #default ds answers,
				answer = d[5],
				explanation = d[9],
				difficulty_bin_1 = "0%" if d[10] == "N/A" else d[10],
				difficulty_bin_2 = "0%" if d[11] == "N/A" else d[11],
				image = d[8],
				type = "DS",
				flagged= d[13] is not None
			)
			ds_questions.append(this_question)
			self.possible_questions["DS"][d[0]] = d
		ds_questions = sorted(ds_questions, key=lambda  q: (q.difficulty_bin_1,1-float(q.difficulty_bin_2.strip('%'))/100))
		self.question_ids["DS"] = ds_questions

		for d in ps_qs:
			this_question = Question(
				id = d[0],
				question = d[2],
				source = d[12],
				answers = [d[3],d[4],d[5],d[6],d[7]],
				answer = d[8],
				explanation = d[12],
				difficulty_bin_1 = d[13],
				difficulty_bin_2 = d[14],
				image = d[11],
				type = "PS",
				flagged= d[16] is not None
			)
			ps_questions.append(this_question)
			self.possible_questions["PS"][d[0]] = d
		self.question_ids["PS"] = ps_questions


	def answer_question(self, answer, time_taken):
		self.answered_questions.append({"date": self.date,
		                                "session_id": self.session_id,
		                                "id": self.cur_question.id,
		                                "type": self.cur_question.type,
		                                "my_answer": answer,
		                                "right_answer": self.cur_question.answer,
		                                "time_taken": time_taken})

	def end_study(self, see_results):
		self.update_flagged_questions()
		print(self.answered_questions)

	def get_results(self):
		return self.answered_questions

	def get_my_answer_for_row(self, row):
		question_type = self.answered_questions[row]["type"]
		question_id = self.answered_questions[row]["id"]
		question = self.question_ids[question_type][question_id]
		return {"id": question.id,
		        "question" : question.question,
		        "a": question.answers[0],
		        "b": question.answers[1],
		        "c": question.answers[2],
		        "d": question.answers[3],
		        "e": question.answers[4],
		        "difficulty": question.difficulty_bin_1,
		        "number_correct": question.difficulty_bin_2,
		        "has_image": question.image != "",
		        "image_path": question.image,
		        "flagged": question.flagged,
		        "answer_result": {"my_answer": self.answered_questions[row]["my_answer"],
		                          "time_taken": self.answered_questions[row]["time_taken"],
		                          "right_answer": self.answered_questions[row]["right_answer"]}
		        }

	def reset(self):
		self.possible_questions = {
			"DS": {},
		    "PS": {},
		    "SC": {},
		    "RC": {},
		    "CR": {}
		}
		self.question_ids = {
			"DS": [],
		    "PS": [],
		    "SC": [],
		    "RC": [],
		    "CR": []
		}
		self.load_questions_from_sql()
		self.cur_question = None
		self.answered_questions = []
		self.flagged_questions = {
			"DS": [],
		    "PS": [],
		    "SC": [],
		    "RC": [],
		    "CR": []
		}
		self.unflag_questions = {
			"DS": [],
		    "PS": [],
		    "SC": [],
		    "RC": [],
		    "CR": []
		}
		self.date = time.strftime("%Y.%m.%d")
		self.session_id = self.generate_session_id()

	def generate_session_id(self):
		conn = sqlite3.connect('db.db')
		session_ids = []
		import uuid
		with conn:
			c = conn.cursor()
			c.execute("select DISTINCT SessionID from AnsweredQs") #do the others later too
			session_ids = [res[0] for res in c.fetchall()]
		test = str(uuid.uuid4())
		while test in session_ids:
			test = str(uuid.uuid4())
		return test



	def start_study(self):
		self.reset()

	def update_flagged_questions(self):
		conn = sqlite3.connect('db.db')
		with conn:
			c = conn.cursor()
			arr = self.flagged_questions["PS"]
			question_mark_array = "({0})".format(",".join("?"*len(arr)))
			c.execute("UPDATE PSQuestions SET flagforedit = 1 WHERE id in " + question_mark_array, tuple(arr)) #do the others later too


	def set_settings(self, settings):
		self.settings = settings

	def toggle_flag(self, checked):
		type = self.cur_question.type
		question_id = self.cur_question.id
		if checked:
			self.flagged_questions[type].append(question_id)
			if question_id in self.unflag_questions[type]:
				self.unflag_questions[type].remove(question_id)
		elif question_id in self.flagged_questions[type]:
			self.flagged_questions[type].remove(question_id)
		else:
			self.unflag_questions[type].append(question_id)



class Question():
	def __init__(self, id = None, question = None, source = None, answers = None, answer = None, explanation = None, difficulty_bin_1 = None, difficulty_bin_2 = None, image = None, type = None, flagged = False):
		self.question = question
		self.id = id
		self.source = source
		self.answers = answers
		self.answer = answer
		self.explanation = explanation
		self.difficulty_bin_1 = difficulty_bin_1  #questions will be chosen by difficulty bin 1 and then difficulty bin 2
		self.difficulty_bin_2 = difficulty_bin_2
		self.image = image
		self.type = type
		self.flagged = flagged

	def __repr__(self):
		return str(self.image)
import sqlite3

class GMATTesterModel():
	def __init__(self):
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
		        "image_path": self.cur_question.image}

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
				type = "DS"
			)
			ds_questions.append(this_question)
			self.possible_questions["DS"][d[0]] = d
		print(ds_questions)
		ds_questions = sorted(ds_questions, key=lambda  q: (q.difficulty_bin_1,1-float(q.difficulty_bin_2.strip('%'))/100))
		print(ds_questions)
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
				type = "PS"
			)
			ps_questions.append(this_question)
			self.possible_questions["PS"][d[0]] = d
		self.question_ids["PS"] = ps_questions


	def answer_question(self, answer, time_taken):
		self.answered_questions.append({"id": self.cur_question.id, "type": self.cur_question.type, "my_answer": answer, "right_answer": self.cur_question.answer, "time_taken": time_taken})

	def end_study(self):
		print(self.answered_questions)

	def set_settings(self, settings):
		self.settings = settings



class Question():
	def __init__(self, id = None, question = None, source = None, answers = None, answer = None, explanation = None, difficulty_bin_1 = None, difficulty_bin_2 = None, image = None, type = None):
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

	def __repr__(self):
		return str(self.image)
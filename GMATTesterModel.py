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
		self.ds_questions_from_sql = self.get_ds_questions()
		self.cur_question = None
		self.answered_questions = []

	def get_question(self):
		self.cur_question = self.ds_questions_from_sql[0]
		return {"question" : self.cur_question.question,
		        "a": self.cur_question.answers[0],
		        "b": self.cur_question.answers[1],
		        "c": self.cur_question.answers[2],
		        "d": self.cur_question.answers[3],
		        "e": self.cur_question.answers[4]}

	def get_answer(self):
		return self.cur_question.answer

	def get_ds_questions(self):
		conn = sqlite3.connect('db.db')
		ds_questions = []
		with conn:
			c = conn.cursor()
			c.execute("SELECT * FROM DSQuestions")
			ds_qs = c.fetchall()
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
				difficulty_bin_1 = d[10],
				difficulty_bin_2 = d[11],
				image = d[8],
				type = "DS"
			)
			ds_questions.append(this_question)
			self.possible_questions["DS"][d[0]] = d
		return ds_questions

	def answer_question(self, answer):
		self.answered_questions.append({"id": self.cur_question.id, "type": self.cur_question.type, "answer": answer})


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
class GMATTesterPresenter():
	def __init__(self, view, model):
		self.model = model
		self.view = view

	def start_study(self, options):
		new_question = self.model.get_question()
		q = new_question["question"]
		answers = [new_question["a"], new_question["b"], new_question["c"], new_question["d"], new_question["e"]]
		self.view.update_main_question(q, answers)

	def submitted_answer(self, answer):
		self.model.answer_question(answer)
		self.view.show_right_answer(self.model.get_answer())
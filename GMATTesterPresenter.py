class GMATTesterPresenter():
	def __init__(self, view, model):
		self.model = model
		self.view = view

	def show_question(self):
		new_question = self.model.get_question()
		q = new_question["question"]
		answers = [new_question["a"], new_question["b"], new_question["c"], new_question["d"], new_question["e"]]
		difficulties = {"difficulty": new_question["difficulty"], "number_correct": new_question["number_correct"]}
		id = new_question["id"]
		image = {"has_image": new_question["has_image"], "image_path": new_question["image_path"]}
		self.view.update_main_question(q, answers, difficulties, id, image)

	def submitted_answer(self, answer, time_taken):
		self.model.answer_question(answer, time_taken)
		self.view.show_right_answer(self.model.get_answer())

	def end_study(self):
		self.model.end_study()

	def start_study(self, settings):
		self.model.set_settings(settings)
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
		self.view.toggle_question_flagged(new_question['flagged'])
		self.view.update_main_question(q, answers, difficulties, id, image, None)

	def submitted_answer(self, answer, time_taken):
		self.model.answer_question(answer, time_taken)
		self.view.show_right_answer(self.model.get_answer())

	def end_study(self, see_results):
		self.model.end_study(see_results)
		if see_results:
			study_results = self.model.get_results()
			self.view.show_results(study_results)

	def start_study(self, settings):
		self.model.start_study()
		self.model.set_settings(settings)

	def flag_question(self, checked):
		self.model.toggle_flag(checked)

	def show_question_results(self, row):
		new_question = self.model.get_my_answer_for_row(row)
		q = new_question["question"]
		answers = [new_question["a"], new_question["b"], new_question["c"], new_question["d"], new_question["e"]]
		difficulties = {"difficulty": new_question["difficulty"], "number_correct": new_question["number_correct"]}
		id = new_question["id"]
		image = {"has_image": new_question["has_image"], "image_path": new_question["image_path"]}
		answer_result = new_question["answer_result"]
		self.view.update_main_question(q, answers, difficulties, id, image, answer_result)
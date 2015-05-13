class GMATTesterPresenter():
	def __init__(self, view, model):
		self.model = model
		self.view = view

	def show_question(self):
		new_question = self.model.get_question()
		self.view.update_main_question(new_question, None)

	def submitted_answer(self, answer, time_taken):
		self.model.answer_question(answer, time_taken)
		self.view.show_right_answer(self.model.get_answer())

	def end_study(self, see_results):
		self.model.end_study(see_results)
		if see_results:
			study_results = self.model.get_results()
			self.view.show_results(study_results)

	def start_study(self, settings):
		self.model.set_settings(settings)
		self.model.start_study()


	def flag_question(self, checked):
		self.model.toggle_flag(checked)

	def show_question_results(self, row):
		new_question = self.model.get_my_answer_for_row(row)
		answer_result = new_question["answer_result"]
		self.view.update_main_question(new_question, answer_result)
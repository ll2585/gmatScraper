import sys
from PyQt4 import QtGui, QtCore
from GMATTesterPresenter import  GMATTesterPresenter
from GMATTesterModel import  GMATTesterModel
from time import strftime

class GMATTester(QtGui.QMainWindow):
	def __init__(self):
		super(GMATTester, self).__init__()
		self.setUp()

	def set_presenter(self, presenter):
		self.presenter = presenter

	def setUp(self):
		self.mainPanel = QtGui.QWidget()
		self.study_button = QtGui.QPushButton('Study', self)
		self.test_button = QtGui.QPushButton('Test', self)
		self.study_button.clicked.connect(self.study)
		self.test_button.clicked.connect(self.test)
		layout = QtGui.QVBoxLayout()
		layout.addWidget(self.study_button)
		layout.addWidget(self.test_button)
		self.mainPanel.setLayout(layout)
		self.setCentralWidget(self.mainPanel)

	def study(self):
		self.settings = {}
		settings_widget = QtGui.QWidget()
		layout = QtGui.QHBoxLayout()
		left_bar = QtGui.QVBoxLayout()
		self.question_group_box = QtGui.QGroupBox("Select Questions")

		self.question_group_layout = QtGui.QVBoxLayout()
		quantitative_label = QtGui.QLabel("<b>Quantitative</b>")
		self.PS_checkbox = QtGui.QCheckBox("Problem Solving")
		self.DS_checkbox = QtGui.QCheckBox("Data Sufficiency")
		verbal_label = QtGui.QLabel("<b>Verbal</b>")
		self.SC_checkbox = QtGui.QCheckBox("Sentence Correction")
		self.CR_checkbox = QtGui.QCheckBox("Critical Reading")
		self.RC_checkbox = QtGui.QCheckBox("Reading Comprehension")
		self.PS_checkbox.setChecked(False)
		self.DS_checkbox.setChecked(False)
		self.SC_checkbox.setChecked(True)
		self.CR_checkbox.setChecked(False)
		self.RC_checkbox.setChecked(False)
		self.question_group_layout.addWidget(quantitative_label)
		self.question_group_layout.addWidget(self.PS_checkbox)
		self.question_group_layout.addWidget(self.DS_checkbox)
		self.question_group_layout.addWidget(verbal_label)
		self.question_group_layout.addWidget(self.SC_checkbox)
		self.question_group_layout.addWidget(self.CR_checkbox)
		self.question_group_layout.addWidget(self.RC_checkbox)
		self.question_group_box.setLayout(self.question_group_layout)

		self.options_group_box = QtGui.QGroupBox("Options")
		self.options_group_layout = QtGui.QVBoxLayout()
		self.show_answer_immediately = QtGui.QCheckBox("Show Answer Immediately")
		self.store_answers = QtGui.QCheckBox("Store Answers")
		self.store_answers.setChecked(True)
		self.only_unanswered_questions = QtGui.QCheckBox("Only Unanswered Questions")
		self.only_answered_questions = QtGui.QCheckBox("Only Answered Questions")
		self.only_wrong_questions = QtGui.QCheckBox("Only Wrongly Questions")
		self.only_right_questions = QtGui.QCheckBox("Only Right Questions")
		self.show_answered_stats = QtGui.QCheckBox("Show Stats on Answered Questions")
		options_form = QtGui.QFormLayout()
		self.number_of_questions = QtGui.QLineEdit()
		self.number_of_questions.setValidator(QtGui.QIntValidator(1,99999))
		options_form.addRow("# Questions (blank for infinite): ", self.number_of_questions)
		self.minimum_difficulty = QtGui.QLineEdit()
		self.minimum_difficulty.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Min Difficulty (blank for None): ", self.minimum_difficulty)
		self.maximum_difficulty = QtGui.QLineEdit()
		self.maximum_difficulty.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Max Difficulty (blank for None): ", self.maximum_difficulty)
		self.minimum_percentage = QtGui.QLineEdit()
		self.minimum_percentage.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Min % Right (blank for None): ", self.minimum_percentage)
		self.maximum_percentage = QtGui.QLineEdit()
		self.maximum_percentage.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Max % Right (blank for None): ", self.maximum_percentage)
		self.minimum_sessions = QtGui.QLineEdit()
		self.minimum_sessions.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Min Sessions (blank for None): ", self.minimum_sessions)
		self.maximum_sessions = QtGui.QLineEdit()
		self.maximum_sessions.setValidator(QtGui.QIntValidator(1,100))
		options_form.addRow("Max Sessions (blank for None): ", self.maximum_sessions)
		self.options_group_layout.addLayout(options_form)
		self.options_group_layout.addWidget(self.show_answer_immediately)
		self.options_group_layout.addWidget(self.store_answers)
		self.options_group_layout.addWidget(self.only_unanswered_questions)
		self.options_group_layout.addWidget(self.only_answered_questions)
		self.options_group_layout.addWidget(self.only_wrong_questions)
		self.options_group_layout.addWidget(self.only_right_questions)
		self.options_group_layout.addWidget(self.show_answered_stats)

		self.options_group_box.setLayout(self.options_group_layout)

		self.start_study_button = QtGui.QPushButton('Start', self)
		self.start_study_button.clicked.connect(self.start_study)

		left_bar.setAlignment(QtCore.Qt.AlignTop)
		left_bar.addWidget(self.question_group_box)
		left_bar.addWidget(self.options_group_box)
		left_bar.addWidget(self.start_study_button)
		layout.addLayout(left_bar)

		settings_widget.setLayout(layout)
		self.setCentralWidget(settings_widget)

	def start_study(self):
		self.settings["show_answer_immediately"] = self.show_answer_immediately.isChecked()
		self.settings["num_questions"] = self.number_of_questions.text()
		self.settings["min_difficulty"] = self.minimum_difficulty.text()
		self.settings["max_difficulty"] = self.maximum_difficulty.text()
		self.settings["min_percentage"] = self.minimum_percentage.text()
		self.settings["max_percentage"] = self.maximum_percentage.text()
		self.settings["min_sessions"] = self.minimum_sessions.text()
		self.settings["max_sessions"] = self.maximum_sessions.text()
		self.settings["store_answers"] = self.store_answers.isChecked()
		self.settings["only_unanswered"] = self.only_unanswered_questions.isChecked()
		self.settings["only_answered"] = self.only_answered_questions.isChecked()
		self.settings["only_wrong"] = self.only_wrong_questions.isChecked()
		self.settings["only_right"] = self.only_right_questions.isChecked()
		self.settings["show_stats"] = self.show_answered_stats.isChecked()

		self.settings["questions_to_get"] = {
			"DS": self.DS_checkbox.isChecked(),
		    "PS": self.PS_checkbox.isChecked(),
		    "SC": self.SC_checkbox.isChecked(),
		}
		self.presenter.start_study(self.settings)
		questions_widget = QtGui.QWidget()
		layout = QtGui.QVBoxLayout()

		top_bar = QtGui.QHBoxLayout()
		self.id_label = QtGui.QLabel()
		self.question_number_label = QtGui.QLabel()
		self.time_taken = QtGui.QLabel()
		self.m = 0
		self.s = 0
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.update_time)

		self.difficulty_label = QtGui.QLabel()
		self.number_correct_label = QtGui.QLabel()
		self.new_question_button = QtGui.QPushButton("New Question")
		self.new_question_button.clicked.connect(self.show_question)
		self.back_to_main_button = QtGui.QPushButton("End")
		self.back_to_main_button.clicked.connect(self.end_study)
		self.end_button = QtGui.QPushButton("Finish and see results")
		self.end_button.clicked.connect(self.end_study_and_see_results)
		self.flagged_checkbox = QtGui.QCheckBox("Flag Question")

		self.flagged_checkbox.toggled.connect(self.flag_question)
		top_bar.addWidget(self.id_label)
		top_bar.addWidget(self.question_number_label)
		top_bar.addWidget(self.time_taken)
		top_bar.addWidget(self.difficulty_label)
		top_bar.addWidget(self.number_correct_label)
		top_bar.addWidget(self.new_question_button)
		top_bar.addWidget(self.back_to_main_button)
		top_bar.addWidget(self.end_button)
		top_bar.addWidget(self.flagged_checkbox)

		layout.addLayout(top_bar)
		middle_bar = QtGui.QVBoxLayout()
		self.question_image = QtGui.QLabel()
		self.question = QtGui.QLabel()
		self.question.setWordWrap(True)
		self.question.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.a = QtGui.QRadioButton()
		self.b = QtGui.QRadioButton()
		self.c = QtGui.QRadioButton()
		self.d = QtGui.QRadioButton()
		self.e = QtGui.QRadioButton()




		self.submit_answer_button = QtGui.QPushButton("Submit Answer")
		self.submit_answer_button.setVisible(False)
		self.submit_answer_button.clicked.connect(self.submit_answer)

		self.next_question_button = QtGui.QPushButton("Next")
		self.next_question_button.setVisible(False)
		self.next_question_button.clicked.connect(self.show_question)

		middle_bar.setAlignment(QtCore.Qt.AlignTop)
		middle_bar.addWidget(self.question_image)

		middle_bar.addWidget(self.question)

		self.answer_widget_group = QtGui.QButtonGroup()
		self.answer_widgets = [self.a, self.b, self.c, self.d, self.e]
		for widget in self.answer_widgets:
			widget.toggled.connect(self.checked_answer)
			widget.setVisible(False)
			middle_bar.addWidget(widget)
			self.answer_widget_group.addButton(widget)
		middle_bar.addWidget(self.submit_answer_button)
		middle_bar.addWidget(self.next_question_button)
		layout.addLayout(middle_bar)

		questions_widget.setLayout(layout)
		self.setCentralWidget(questions_widget)
		self.show_question()

	def flag_question(self):
		self.presenter.flag_question(self.flagged_checkbox.isChecked())

	def end_study(self):
		self.timer.stop()
		self.presenter.end_study(False)
		self.setUp()

	def display_question_panel(self):
		self.presenter.show_question_results(self.answered_questions.currentRow())

	def show_results(self, results):

		results_widget = QtGui.QWidget()
		layout = QtGui.QHBoxLayout()

		left_bar = QtGui.QVBoxLayout()
		self.right_answers = QtGui.QLabel()
		self.time_taken = QtGui.QLabel()
		self.answered_questions = QtGui.QListWidget()
		self.answered_questions.itemClicked.connect(self.display_question_panel)
		total_right = 0
		total_qs = 0
		total_m = 0
		total_s = 0
		for q in results:
			total_m += q["time_taken"][0]
			total_s += q["time_taken"][1]
			total_qs += 1
			right_answer = q['my_answer'] == q['right_answer']
			total_right += 1 if right_answer else 0
			item = QtGui.QListWidgetItem("{0} - {1} - {2} - {3:02d}:{4:02d}".format(q['type'],str(q['id']), "RIGHT" if right_answer else "WRONG", q["time_taken"][0],q["time_taken"][1]))
			item.setBackgroundColor(QtCore.Qt.green if right_answer else QtCore.Qt.red)
			self.answered_questions.addItem(item)
		import math
		total_m += math.floor(total_s / 60)
		total_s = total_s % 60
		self.time_taken.setText("Time Taken: {0} minutes {1} seconds".format(total_m,total_s))
		self.right_answers.setText("Total Score: {0}/{1}".format(str(total_right),str(total_qs)))
		left_bar.addWidget(self.time_taken)
		left_bar.addWidget(self.right_answers)
		left_bar.addWidget(self.answered_questions)

		layout.addLayout(left_bar)
		middle_layout = QtGui.QVBoxLayout()
		top_bar = QtGui.QHBoxLayout()
		self.id_label = QtGui.QLabel()
		self.question_number_label = QtGui.QLabel()
		self.time_taken = QtGui.QLabel()
		self.m = 0
		self.s = 0
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.update_time)

		self.difficulty_label = QtGui.QLabel()
		self.number_correct_label = QtGui.QLabel()
		self.back_to_main_button = QtGui.QPushButton("End")
		self.back_to_main_button.clicked.connect(self.end_study)

		self.flagged_checkbox = QtGui.QCheckBox("Flag Question")

		self.flagged_checkbox.toggled.connect(self.flag_question)
		top_bar.addWidget(self.id_label)
		top_bar.addWidget(self.question_number_label)
		top_bar.addWidget(self.time_taken)
		top_bar.addWidget(self.difficulty_label)
		top_bar.addWidget(self.number_correct_label)
		top_bar.addWidget(self.back_to_main_button)
		top_bar.addWidget(self.flagged_checkbox)

		middle_layout.addLayout(top_bar)

		question_layout = QtGui.QVBoxLayout()
		question_layout.addWidget(self.question_number_label)
		self.question_image = QtGui.QLabel()
		self.question = QtGui.QLabel()
		self.question.setWordWrap(True)
		self.question.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
		self.a = QtGui.QRadioButton()
		self.b = QtGui.QRadioButton()
		self.c = QtGui.QRadioButton()
		self.d = QtGui.QRadioButton()
		self.e = QtGui.QRadioButton()




		self.submit_answer_button = QtGui.QPushButton("Submit Answer")
		self.submit_answer_button.setVisible(False)
		self.submit_answer_button.clicked.connect(self.submit_answer)

		self.next_question_button = QtGui.QPushButton("Next")
		self.next_question_button.setVisible(False)
		self.next_question_button.clicked.connect(self.show_question)

		question_layout.setAlignment(QtCore.Qt.AlignTop)
		question_layout.addWidget(self.question_image)

		question_layout.addWidget(self.question)

		self.answer_widget_group = QtGui.QButtonGroup()
		self.answer_widgets = [self.a, self.b, self.c, self.d, self.e]
		for widget in self.answer_widgets:
			widget.toggled.connect(self.checked_answer)
			widget.setVisible(False)
			question_layout.addWidget(widget)
			self.answer_widget_group.addButton(widget)
		question_layout.addWidget(self.submit_answer_button)
		question_layout.addWidget(self.next_question_button)

		middle_layout.addLayout(question_layout)
		layout.addLayout(middle_layout)
		results_widget.setLayout(layout)
		self.setCentralWidget(results_widget)

	def end_study_and_see_results(self):
		self.timer.stop()
		self.presenter.end_study(True)

	def show_question(self):
		self.reset_question()
		if self.question_number_label.text() == "{0}/{0}".format(self.settings["num_questions"]):
			self.end_study_and_see_results()
		else:
			self.presenter.show_question()
			self.timer.start(1000)

	def update_time(self):
		if self.s < 59:
			self.s += 1
		else:
			if self.m < 59:
				self.s = 0
				self.m += 1
			else:
				self.timer.stop()

		time = "{0:02d}:{1:02d}".format(self.m,self.s)

		self.time_taken.setText(time)


	def reset_question(self):
		self.answer_widget_group.setExclusive(False)
		self.next_question_button.setVisible(False)
		self.question_image.setVisible(False)
		for widget in self.answer_widgets:
			widget.setEnabled(True)
			widget.setChecked(False)
			widget.setStyleSheet("")
		self.answer_widget_group.setExclusive(True)
		self.reset_timer()

	def toggle_question_flagged(self, flagged):
		self.flagged_checkbox.setChecked(flagged)

	def reset_timer(self):
		self.timer.stop()

		self.s = 0
		self.m = 0

		time = "{0:02d}:{1:02d}".format(self.m,self.s)

		self.time_taken.setText(time)


	def checked_answer(self):
		self.submit_answer_button.setVisible(False)
		for widget in self.answer_widgets:
			if widget.isChecked():
				self.submit_answer_button.setVisible(True)
				break

	def update_main_question(self, question, answer_result):
		if question['has_image']:
			import os
			question_image = QtGui.QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), question['image_path']))
			self.question_image.setVisible(True)
			self.question_image.setPixmap(question_image)
			self.question_image.show()
		self.question.setText(question["question"])
		self.settings["num_questions"] = question["max_questions"] if self.settings["num_questions"] == ""  or self.settings["num_questions"] > question["max_questions"] else self.settings["num_questions"]
		self.question_number_label.setText("{0}/{1}".format(question["question_number"], self.settings["num_questions"]))
		if self.question_number_label.text() == "{0}/{0}".format(self.settings["num_questions"]) and not answer_result:
			self.next_question_button.setDisabled(True)
			self.new_question_button.setDisabled(True)
		self.id_label.setText("ID: {0}".format(question["id"]))
		self.difficulty_label.setText("Difficulty: {0}".format(question["difficulty"]))
		self.number_correct_label.setText("Percentage Correct: {0}".format(question["number_correct"]))
		answer_labels = ["(A)", "(B)", "(C)", "(D)", "(E)"]
		letters = ["a", "b", "c", "d", "e"]
		for i in range(0, len(self.answer_widgets)):
			self.answer_widgets[i].setVisible(True)
			self.answer_widgets[i].setText("{0} {1}".format(answer_labels[i], question[letters[i]]))
		if answer_result is not None:
			self.reset_question()
			my_answer = answer_result["my_answer"]
			right_answer = answer_result["right_answer"]
			for i in range(0, len(self.answer_widgets)):
				if right_answer in answer_labels[i]:
					self.answer_widgets[i].setStyleSheet("* {background-color: rgb(0, 255, 0);}")
				if my_answer in answer_labels[i]:
					if my_answer != right_answer:
						self.answer_widgets[i].setStyleSheet("* {background-color: rgb(255, 0, 0);}")
					self.answer_widgets[i].setChecked(True)
					self.submit_answer_button.setVisible(False)
				self.answer_widgets[i].setDisabled(True)
			m = answer_result["time_taken"][0]
			s = answer_result["time_taken"][1]
			time = "{0:02d}:{1:02d}".format(m,s)
			self.time_taken.setText(time)


	def test(self):
		pass

	def get_start_study_options(self):
		return self.settings

	def submit_answer(self):
		self.timer.stop()
		answer_labels = ["A", "B", "C", "D", "E"]
		for i in range(0, len(self.answer_widgets)):
			if self.answer_widgets[i].isChecked():
				self.presenter.submitted_answer(answer_labels[i], [self.m, self.s])
				break

	def show_right_answer(self, right_answer):
		if not self.settings["show_answer_immediately"]:
			self.show_question()
			return
		answer_labels = ["A", "B", "C", "D", "E"]
		for i in range(0, len(self.answer_widgets)):
			if answer_labels[i] == right_answer:
				self.answer_widgets[i].setStyleSheet("* {background-color: rgb(0, 255, 0);}")
			elif self.answer_widgets[i].isChecked():
				self.answer_widgets[i].setStyleSheet("* {background-color: rgb(255, 0, 0);}")
			self.answer_widgets[i].setEnabled(False)
		self.next_question_button.setVisible(True)
		self.submit_answer_button.setVisible(False)




if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	myapp = GMATTester()
	myapp.set_presenter(GMATTesterPresenter(myapp, GMATTesterModel()))
	myapp.show()
	sys.exit(app.exec_())
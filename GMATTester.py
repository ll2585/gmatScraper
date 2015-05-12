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
		self.PS_checkbox = QtGui.QCheckBox("Problem Solving")
		self.DS_checkbox = QtGui.QCheckBox("Data Sufficiency")
		self.PS_checkbox.setChecked(True)
		self.question_group_layout.addWidget(self.PS_checkbox)
		self.question_group_layout.addWidget(self.DS_checkbox)
		self.question_group_box.setLayout(self.question_group_layout)

		self.options_group_box = QtGui.QGroupBox("Options")
		self.options_group_layout = QtGui.QVBoxLayout()
		self.show_answer_immediately = QtGui.QCheckBox("Show Answer Immediately")
		self.options_group_layout.addWidget(self.show_answer_immediately)
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
		self.settings["questions_to_get"] = {
			"DS": self.DS_checkbox.isChecked(),
		    "PS": self.PS_checkbox.isChecked(),
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
		top_bar.addWidget(self.id_label)
		top_bar.addWidget(self.question_number_label)
		top_bar.addWidget(self.time_taken)
		top_bar.addWidget(self.difficulty_label)
		top_bar.addWidget(self.number_correct_label)
		top_bar.addWidget(self.new_question_button)
		top_bar.addWidget(self.back_to_main_button)
		top_bar.addWidget(self.end_button)

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

	def end_study(self):
		self.timer.stop()
		self.setUp()

	def end_study_and_see_results(self):
		self.presenter.end_study()

	def show_question(self):
		self.reset_question()
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

	def update_main_question(self, question, answers, difficulties, id, image):
		if image['has_image']:
			import os
			question_image = QtGui.QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), image['image_path']))
			print(os.path.join(os.path.dirname(os.path.realpath(__file__)), image['image_path']))
			self.question_image.setVisible(True)
			self.question_image.setPixmap(question_image)
			self.question_image.show()
		self.question.setText(question)
		self.id_label.setText("ID: {0}".format(id))
		self.difficulty_label.setText("Difficulty: {0}".format(difficulties["difficulty"]))
		self.number_correct_label.setText("Percentage Correct: {0}".format(difficulties["number_correct"]))
		answer_labels = ["(A)", "(B)", "(C)", "(D)", "(E)"]
		for i in range(0, len(self.answer_widgets)):
			self.answer_widgets[i].setVisible(True)
			self.answer_widgets[i].setText("{0} {1}".format(answer_labels[i], answers[i]))

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
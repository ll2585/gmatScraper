import sys
from PyQt4 import QtGui, QtCore
from GMATTesterPresenter import  GMATTesterPresenter
from GMATTesterModel import  GMATTesterModel

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
		newPanel = QtGui.QWidget()
		layout = QtGui.QHBoxLayout()
		left_bar = QtGui.QVBoxLayout()
		self.question_group_box = QtGui.QGroupBox("Select Questions")

		self.question_group_layout = QtGui.QVBoxLayout()
		self.PS_checkbox = QtGui.QCheckBox("Problem Solving")
		self.DS_checkbox = QtGui.QCheckBox("Data Sufficiency")
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

		middle_bar = QtGui.QVBoxLayout()
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

		middle_bar.setAlignment(QtCore.Qt.AlignTop)
		middle_bar.addWidget(self.question)

		self.answer_widgets = [self.a, self.b, self.c, self.d, self.e]
		for widget in self.answer_widgets:
			widget.toggled.connect(self.checked_answer)
			widget.setVisible(False)
			middle_bar.addWidget(widget)
		middle_bar.addWidget(self.submit_answer_button)
		layout.addLayout(middle_bar)

		newPanel.setLayout(layout)
		self.setCentralWidget(newPanel)

	def start_study(self):
		self.presenter.start_study(self.get_start_study_options())

	def checked_answer(self):
		self.submit_answer_button.setVisible(False)
		for widget in self.answer_widgets:
			if widget.isChecked():
				self.submit_answer_button.setVisible(True)
				break

	def update_main_question(self, question, answers):
		self.question.setText(question)
		answer_labels = ["(A)", "(B)", "(C)", "(D)", "(E)"]
		for i in range(0, len(self.answer_widgets)):
			self.answer_widgets[i].setVisible(True)
			self.answer_widgets[i].setText("{0} {1}".format(answer_labels[i], answers[i]))

	def test(self):
		pass

	def get_start_study_options(self):
		return {"show_answer_immediately": self.show_answer_immediately.isChecked()}

	def submit_answer(self):
		answer_labels = ["A", "B", "C", "D", "E"]
		for i in range(0, len(self.answer_widgets)):
			if self.answer_widgets[i].isChecked():
				self.presenter.submitted_answer(answer_labels[i])
				break

	def show_right_answer(self, right_answer):
		if not self.show_answer_immediately.isChecked():
			return
		answer_labels = ["A", "B", "C", "D", "E"]
		answer_index = -1
		for i in range(0, len(self.answer_widgets)):
			if answer_labels[i] == right_answer:
				answer_index = i
				self.answer_widgets[i].setStyleSheet("* {background-color: rgb(0, 255, 0);}")
				break
		if not self.answer_widgets[answer_index].isChecked():
			for i in range(0, len(self.answer_widgets)):
				if self.answer_widgets[i].isChecked():
					self.answer_widgets[i].setStyleSheet("* {background-color: rgb(255, 0, 0);}")

	def wrong_answer(self):
		print("WRONG ANWER")



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	myapp = GMATTester()
	myapp.set_presenter(GMATTesterPresenter(myapp, GMATTesterModel()))
	myapp.show()
	sys.exit(app.exec_())
import sys
import unittest
from unittest.mock import MagicMock
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest
from PyQt4.QtCore import Qt
from GMATTester import GMATTester
from GMATTesterPresenter import GMATTesterPresenter
from GMATTesterModel import GMATTesterModel


class TesterTest(unittest.TestCase):
	def setUp(self):
		self.app = QApplication(sys.argv)
		self.tester = GMATTester()
		self.mock_model = GMATTesterModel()
		self.presenter = GMATTesterPresenter(self.tester, self.mock_model)
		self.tester.set_presenter(self.presenter)

	def test_defaults(self):
		self.assertEqual(self.tester.study_button.text(), "Study")
		self.assertEqual(self.tester.test_button.text(), "Test")

	def test_study(self):
		QTest.mouseClick(self.tester.study_button, Qt.LeftButton)
		self.assertEqual(self.tester.start_study_button.text(), "Start")
		self.assertTrue(self.tester.question.wordWrap())
		for widget in self.tester.answer_widgets:
			self.assertFalse(widget.isVisible())

	def test_mock_study(self):
		QTest.mouseClick(self.tester.study_button, Qt.LeftButton)

		self.mock_model.get_question = MagicMock(return_value={"question": "the answer is A", "a": "the answer", "b": "not the answer", "c": "not the answer", "d": "not the answer", "e": "not the answer"})
		QTest.mouseClick(self.tester.start_study_button, Qt.LeftButton)
		self.assertEqual(self.tester.question.text(), "the answer is A")
		QTest.mouseClick(self.tester.a, Qt.LeftButton)
		self.assertTrue(self.tester.submit_answer_button.isVisible())



if __name__ == "__main__":
	unittest.main()
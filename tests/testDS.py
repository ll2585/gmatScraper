import unittest
from scraper import scrapeForumPost

class TestDS(unittest.TestCase):
	def setUp(self):
		import os
		os.chdir(b'C:\Users\luke.li\Documents\Python\gmatScraper')
		import csv
		self.questions = {}
		with open('tests/ds.csv', encoding="utf-8") as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				self.questions[row['filename']] = (row)

	def testQuestions(self):
		for f in self.questions:
			this_q = self.questions[f]
			q = scrapeForumPost(None, "DS", filepath = "DS\{0}".format(f))
			question=q['question']
			with self.subTest(question=question):
				self.assertEqual(question.replace("  ", " "), this_q['question'])

	def testPromptOne(self):
		for f in self.questions:
			this_q = self.questions[f]
			q = scrapeForumPost(None, "DS", filepath = "DS\{0}".format(f))
			one=q['1']
			with self.subTest(one=one):
				self.assertEqual(one.replace("  ", " "), this_q['1'],f)

	def testPromptTwo(self):
		for f in self.questions:
			this_q = self.questions[f]
			q = scrapeForumPost(None, "DS", filepath = "DS\{0}".format(f))
			two=q['2']
			with self.subTest(two=two):
				self.assertEqual(two.replace("  ", " "), this_q['2'],f)

	def testAnswer(self):
		for f in self.questions:
			this_q = self.questions[f]
			q = scrapeForumPost(None, "DS", filepath = "DS\{0}".format(f))
			answer=q['answer']
			with self.subTest(answer=answer):
				self.assertEqual(answer.replace("  ", " "), this_q['answer'],f)

def suite():
	suite = unittest.TestSuite()
	suite.addTest (TestDS())
	return suite()

if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	test_suite = suite()
	runner.run (test_suite)
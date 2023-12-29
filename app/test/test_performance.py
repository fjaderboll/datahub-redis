import unittest
import random

import helper

class TestPerf(unittest.TestCase):

	def test(self):
		testId = str(random.randint(0, 1000))
		#for i in range(1, 10):
		#	(username, password) = helper.createUser(helper.getRandomName('perf-' + testId + '.'))

if __name__ == '__main__':
	unittest.main()

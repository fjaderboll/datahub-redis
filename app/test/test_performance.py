import unittest
import random

import util

class TestPerf(unittest.TestCase):

	def test(self):
		testId = str(random.randint(0, 1000))
		for i in range(1, 10):
			util.createUser('perf-' + testId + '.' + str(i))

if __name__ == '__main__':
	unittest.main()

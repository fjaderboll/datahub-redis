import unittest
import requests

import helper

class TestHeaders(unittest.TestCase):

	def assertNoFraming(self, response):
		self.assertEqual(response.headers.get('Content-Security-Policy'), "frame-ancestors 'none'")
		self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')

	def test_no_framing(self):
		# pages, the API and its errors may not be shown in a frame on another site
		self.assertNoFraming(requests.get(helper.BASE_URL + 'state/users'))
		self.assertNoFraming(requests.get(helper.BASE_URL + 'datasets/'))         # 401
		self.assertNoFraming(requests.get(helper.BASE_URL + 'no-such-endpoint'))  # 404
		self.assertNoFraming(requests.get(helper.BASE_URL))                       # Swagger

if __name__ == '__main__':
	unittest.main()

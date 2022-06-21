# import json
# from django.test import TestCase
# from urllib.parse import urlencode
#
#
# class ViewTestCase(TestCase):
#
#     def test_post_feedback(self):
#         # c = Client()
#         feedback = {
#             'name': 'Dupakoor',
#             'subject': 'Cry1Aa1',
#             'email': 'bpprc.database@gmail.com',
#             'message': 'It seems everything works smoothly'}
#         data = urlencode(feedback)
#         response = self.client.post(
#             '/feedback_home/', json.dumps(data), content_type="application/x-www-form-urlencoded")
#
#         self.assertEqual(response.status_code, 200)

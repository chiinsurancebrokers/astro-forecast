import unittest
from app import app


class HomeTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_is_a_landing_page_in_both_languages(self):
        for lang, word in (('en', 'Your sky, made clear'), ('el', 'Ο ουρανός σου')):
            r = self.client.get('/?lang=' + lang)
            self.assertEqual(r.status_code, 200)
            body = r.get_data(as_text=True)
            self.assertIn(word, body)
            for href in ('/horoscope', '/tarot', '/natal-reading', '/monitor', '/platform', '/methods'):
                self.assertIn('href="' + href, body)
            self.assertNotIn('Run forecast', body)

    def test_monitor_keeps_the_old_tool(self):
        r = self.client.get('/monitor')
        self.assertEqual(r.status_code, 200)
        self.assertIn('Run forecast', r.get_data(as_text=True))

    def test_every_sign_link_is_valid(self):
        body = self.client.get('/').get_data(as_text=True)
        self.assertEqual(body.count('href="/horoscope?sign='), 12)


if __name__ == '__main__':
    unittest.main()

import os
import re
import tempfile
import unittest

from app import db
from main import app
from models import User, Url


class FlaskrTestCase(unittest.TestCase):
    data = {
        "email": "test@test.ua",
        "password": "password",
        "password2": "password",
        "name": "test"
    }

    @classmethod
    def setUpClass(cls):
        cls.file_path = tempfile.NamedTemporaryFile(suffix=".db")
        cls.db = db
        cls.app = app
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.abspath(os.getcwd()) + cls.file_path.name
        print(cls.app.config['SQLALCHEMY_DATABASE_URI'])
        cls.app.config['DEBUG'] = False
        cls.app.config['TESTING'] = True
        cls.app.config['DEBUG'] = False
        cls.client = app.test_client()
        cls.db.init_app(cls.app)
        with cls.app.app_context():
            cls.db.create_all()

    @classmethod
    def tearDownClass(cls) -> None:
        with cls.app.app_context():
            cls.db.drop_all()
        os.remove(os.path.abspath(os.getcwd()) + cls.file_path.name)

    def test_empty_data_base(self):
        with self.app.app_context():
            self.assertTrue(User.query.count())

    def test_anonim_user(self):
        with self.app.app_context():
            response = self.client.get('/hello')
            self.assertEqual(response.status_code, 404)
            self.assertTrue(re.search('This page not found', response.get_data(as_text=True)))

    def test_create_user(self):
        with self.app.app_context():
            response = self.client.post("/register", data=self.data)
            count_user = User.query.count()
            self.assertEqual(response.status_code, 302, msg="Redirect to login")
            self.assertEqual(count_user, 1)

    def test_main_page(self):
        with self.app.app_context():
            # try login
            response = self.client.post("/login", data={"email": self.data["email"],
                                                        "password": self.data["password"]}, follow_redirects=True)
            self.assertEqual(response.status_code, 200, msg="Redirect to main")
            self.assertTrue(re.search(f"Hello, {self.data['name'].capitalize()}", response.get_data(as_text=True)))

            # try to create short url
            url = {"url": "https://flask.palletsprojects.com/en/2.2.x/quickstart/#"}
            self.client.post(f"/{self.data['name']}", data=url, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            # try to add not valid url
            response = self.client.post(f"/{self.data['name']}", data={"url": "/The/best/app"}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(re.search("Don&#39;t validate url", response.get_data(as_text=True)))

            # try to get list of short urls
            response = self.client.get(f"/{self.data['name']}", data=url, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(Url.query.filter_by(base_url=url["url"], user_id=1).first())
            self.assertEqual(Url.query.filter_by(base_url=url["url"], user_id=1).count(), 1)
            self.assertEqual(Url.query.count(), 2)

            # try to follow short url
            data = {"link": Url.query.filter_by(base_url=url["url"], user_id=1).first().key}
            response = self.client.get(f"/{data['link']}")
            self.assertEqual(response.status_code, 302)
            self.assertTrue(re.search(f'{url["url"]}', response.get_data(as_text=True)))

            # try to follow not exist short url
            response = self.client.get(f"/followshorturl")
            self.assertEqual(response.status_code, 302)

            # try to delete short url
            data = {"link": Url.query.filter_by(base_url=url["url"], user_id=1).first().key}
            response = self.client.get("/delete-link", data=data, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Url.query.filter_by(base_url=url["url"], user_id=1).first())
            self.assertEqual(Url.query.filter_by(base_url=url["url"], user_id=1).count(), 0)
            self.assertFalse(Url.query.filter_by(base_url=url["url"], user_id=1).first())
            self.assertTrue(re.search(f"This link {url['url']} was deleted", response.get_data(as_text=True)))

    def test_follow_short_url(self):
        url = {"url": "https://flask.palletsprojects.com/en/2.2.x/"}
        with self.app.app_context():
            self.client.post("/login", data={"email": self.data["email"], "password": self.data["password"]}, follow_redirects=True)
            self.client.post(f"/{self.data['name']}", data=url, follow_redirects=True)

            # try logout
            response = self.client.get('/logout')
            self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            # try to follow short url
            data = {"link": Url.query.filter_by(base_url=url["url"], user_id=1).first().key}
            response = self.client.get(f"/{data['link']}")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(Url.query.filter_by(base_url=url["url"], user_id=1).first().clicks, 1)

            # try to follow not exist short url
            response = self.client.get(f"/followshorturl", follow_redirects=True)
            self.assertEqual(response.status_code, 404)
            self.assertTrue(re.search(f'/login', response.get_data(as_text=True)))


if __name__ == '__main__':
    unittest.main()

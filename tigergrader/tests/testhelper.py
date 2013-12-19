import os
import shutil
import tigergrader as tg
import tigergrader.initdb as initdb
import tigergrader.grader as grader
from tigergrader.config import cfg
import unittest
import tempfile


class TestHelper(unittest.TestCase):

    TEST_HOME = os.path.dirname(os.path.realpath(__file__))

    def update_config(self, key, value):
        self.config[key] = value
        tg.app.config[key] = value

    def setUp(self):
        self.app = tg.app.test_client()
        self.config = cfg
        self.update_config('TESTING', True)
        self.update_config('UPLOAD_FOLDER', tempfile.mkdtemp())
        self.db_fd, db_name = tempfile.mkstemp()
        self.update_config('DATABASE', db_name)
        grader.celery.conf.ALWAYS_EAGER = True
        initdb.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.config['DATABASE'])
        shutil.rmtree(self.config['UPLOAD_FOLDER'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def submit(self, module, f):
        return self.app.post('/submit/' + module, data=dict(
                             file=(f, 'test.txt')),
                             follow_redirects=True)

    def register(self, user, password, emails):
        return self.app.post('/register', data=dict(
            username=user, password=password, emails=emails),
            follow_redirects=True)

    def activate_submission(self, module):
        self.login('admin', 'admintiger')
        return self.app.post('/admin', data={module: 1},
                             follow_redirects=True)
        self.logout()

    def activate_registration(self):
        self.login('admin', 'admintiger')
        return self.app.post('/admin', data={'_registration': 1},
                             follow_redirects=True)
        self.logout()

    def grade(self, file_name, test, user):
        submission = os.path.join(self.config["UPLOAD_FOLDER"], file_name)
        shutil.copyfile(os.path.join(self.TEST_HOME, file_name),
                        submission)

        return grader.grade(submission, test, user)

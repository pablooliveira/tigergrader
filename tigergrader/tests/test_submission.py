import unittest
import os
import tempfile
from tigergrader.initdb import create_user
from cStringIO import StringIO
from testhelper import TestHelper


class SubmissionTestCases(TestHelper):
    def setUp(self):
        TestHelper.setUp(self)

        create_user('admin', 'admin@example.com', 'admintiger')
        create_user('user', 'user@example.com', 'usertiger')

    def test_inactive_submission(self):
        self.login('user', 'usertiger')
        rv = self.submit('T1', StringIO('contents'))
        assert "Module does not seem to exist or is inactive." in rv.data

    def test_active_submission(self):
        self.activate_submission('T1')
        self.login('user', 'usertiger')
        rv = self.submit('T1', StringIO('contents'))
        assert "Module does not seem to exist or is inactive." not in rv.data
        assert "/waitfor/" in rv.data

    def test_grade(self):
        self.login('user', 'usertiger')
        submission = "jtiger-src.zip"
        result = self.grade(submission, "T1", user="user")
        assert result["grade"] == 3.0

        # grade is displayed for users
        rv = self.app.get('/', follow_redirects=True)
        assert "3.0 / 20" in rv.data

        # the report exists
        rv = self.app.get('/report/T1', follow_redirects=True)
        assert "T1 3.0 / 20" in rv.data

        # students cannot download the submissions ...
        rv = self.app.get('/archive/jtiger-src.zip', follow_redirects=True)
        assert "Administrative account required" in rv.data

        # ... but admin can
        self.logout()
        self.login('admin', 'admintiger')
        rv = self.app.get('/archive/jtiger-src.zip', follow_redirects=True)
        assert rv.headers['Content-Type'] == "application/zip"

    def test_grade_nozip(self):
        submission = "test_submission.py"
        result = self.grade(submission, "T1", user="user")
        assert result["grade"] == -1
        assert "Could not unzip file" in result["tests"][0]["error"]

    def test_grade_wrongzip(self):
        submission = "wrongzip.zip"
        result = self.grade(submission, "T1", user="user")
        assert result["grade"] == -1
        assert "Your zip file should contain only" \
            in result["tests"][0]["error"]

    def test_wrong_build(self):
        self.login('user', 'usertiger')
        submission = "jtiger-src.zip"
        result = self.grade(submission, "T2A", user="user")
        assert result["grade"] == -1
        assert "build failed" in result["tests"][0]["error"]

    def test_wrong_command(self):
        try:
            self.update_config("RUN_COMMAND", "wrong")
            submission = "jtiger-src.zip"
            result = self.grade(submission, "T1", user="user")
        finally:
            self.update_config("RUN_COMMAND", "java")
        assert result["grade"] == -1
        assert "Failed executing command" in result["tests"][0]["error"]


if __name__ == '__main__':
    unittest.main()

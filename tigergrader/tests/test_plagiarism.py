import unittest
import os
import shutil
from tigergrader.initdb import create_user
from testhelper import TestHelper


class PlagiarismTestCases(TestHelper):
    def setUp(self):
        TestHelper.setUp(self)
        create_user('admin', 'admin@example.com', 'admintiger')
        create_user('user1', 'user@example.com', 'usertiger')
        create_user('user2', 'user@example.com', 'usertiger')

        self.activate_submission("T1")
        self.grade("jtiger-src.zip", "T1", user="user1")
        self.grade("jtiger-src.zip", "T1", user="user2")

    def test_plagiarism(self):
        self.login('admin', 'admintiger')
        rv = self.app.get('/admin', follow_redirects=True)
        assert "3.0" in rv.data
        assert "user1" in rv.data
        assert "user2" in rv.data

        rv = self.app.get('/plagiarism/T1', follow_redirects=True)
        assert "user1" in rv.data
        assert "user2" in rv.data
        assert "/compare/T1/jtiger-src.zip/jtiger-src.zip/" in rv.data

        rv = self.app.get('/compare/T1/jtiger-src.zip/jtiger-src.zip/',
                          follow_redirects=True)
        assert "package jtiger.lexer" in rv.data

        rv = self.app.get('/plagiarism/TWRONG', follow_redirects=True)
        assert "Module does not seem to exist" in rv.data


if __name__ == '__main__':
    unittest.main()

from tigergrader.initdb import create_user
import unittest
from testhelper import TestHelper


class LoginTestCases(TestHelper):
    def test_invalid_login(self):
        rv = self.login('nobody', 'sesame')
        assert "Invalid Credentials" in rv.data

    def test_no_login(self):
        rv = self.app.get('/report/T1', follow_redirects=True)
        assert "You need to log in" in rv.data

    def test_admin_login(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        rv = self.login('admin', 'admintiger')
        assert "Invalid Credentials" not in rv.data
        assert "You were successfully logged in" in rv.data
        assert "Group admin" in rv.data
        assert "Registration and Modules" in rv.data

    def test_user_login(self):
        create_user('user', 'user@example.com', 'usertiger')
        rv = self.login('user', 'usertiger')
        assert "Invalid Credentials" not in rv.data
        assert "You were successfully logged in" in rv.data
        assert "Group user" in rv.data
        assert "(current grade : 0 / 20)" in rv.data

    def test_login_logout(self):
        create_user('user', 'user@example.com', 'usertiger')
        rv = self.login('user', 'usertiger')
        assert "Group user" in rv.data
        rv = self.logout()
        assert "Group user" not in rv.data

    def test_registration_inactive(self):
        rv = self.register("newuser", "secret", "newuser@example.com")
        assert "Registration is currently closed" in rv.data

    def test_no_admin_access(self):
        create_user('user', 'user@example.com', 'usertiger')
        self.login('user', 'usertiger')
        rv = self.activate_registration()
        assert "Administrative account required" in rv.data

    def test_registration_active(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("newuser", "secretsecret", "newuser@example.com")
        assert "Account successfully created" in rv.data

    def test_wrong_mail(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("newuser", "secretsecret", "wrongmail")
        assert "Emails addresses are not correct" in rv.data

    def test_wrong_username(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("newuser:)", "secretsecret", "newuser@example.com")
        assert "can only contain letters" in rv.data

    def test_no_mail(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("newuser", "secretsecret", "")
        assert "At least one email must be provided" in rv.data

    def test_pass_too_short(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("newuser", "secret", "newuser@example.com")
        assert "Password must be at least 8 characters long" in rv.data

    def test_user_too_short(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        rv = self.register("ne", "secret", "newuser@example.com")
        assert "Username must be at least 3 characters long" in rv.data

    def test_already_exists(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        self.register("newuser", "secretsecret", "newuser@example.com")
        rv = self.register("newuser", "secretsecret", "newuser@example.com")
        assert "Account already exists" in rv.data

    def test_already_exists(self):
        create_user('admin', 'admin@example.com', 'admintiger')
        self.activate_registration()
        self.register("newuser", "secretsecret", "newuser@example.com")
        rv = self.register("newuser", "secretsecret", "newuser@example.com")
        assert "Account already exists" in rv.data
        rv = self.register("admin", "secretsecret", "newuser@example.com")
        assert "Account already exists" in rv.data

if __name__ == '__main__':
    unittest.main()

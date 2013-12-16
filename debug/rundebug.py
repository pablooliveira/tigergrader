import os
import subprocess
from tigergrader import app
from tigergrader.initdb import create_user
from tigergrader.database import init_db

if __name__ == "__main__":
    DEBUG_HOME = os.path.dirname(os.path.realpath(__file__))
    os.environ["TIGERGRADER_SETTINGS"] = os.path.join(DEBUG_HOME, "configuration.py")
    init_db()
    create_user("admin", "admin@example.com", "admintiger")
    create_user("user", "user@example.com", "usertiger")
    subprocess.Popen(['celery', 'worker', '-A', 'tigergrader.grader'])  
    app.run(debug=True, port=8080, host="0.0.0.0")

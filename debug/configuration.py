import os
DEBUG_HOME = os.path.dirname(os.path.realpath(__file__))
SECRET_KEY = "SelectAVerySecretKeyToSignApplicationSessions"
ADMIN_USERNAME = "admin"
MODULE_FOLDER = os.path.join(DEBUG_HOME, "../example-lecture/modules")
SANDBOX_BLUEPRINT = os.path.join(DEBUG_HOME, "../example-lecture/sandbox/")
UPLOAD_FOLDER = os.path.join(DEBUG_HOME, "upload")
MODULES = ["T1", "T2A"]
SUBMISSION_TIMEOUT = 60*1000
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
EXPECTED_DIR = "src/"
POLICY_FILE = "test.policy"
JOPTS = ["-cp",
         "lib/*:dist/lib/JTiger.jar",
         "-Djava.security.manager",
         "-Djava.security.policy={0}".format(POLICY_FILE)]
CPU_LIMIT = 60
AS_LIMIT = 1024*1024*4096
CELERY_BACKEND = 'amqp'
CELERY_BROKER = 'amqp://guest@localhost//'
DATABASE = os.path.join(DEBUG_HOME, "database.db")

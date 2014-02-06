SECRET_KEY = "SelectAVerySecretKeyToSignApplicationSessions"
ADMIN_USERNAME = "admin"
MODULE_FOLDER = "/var/www/tigergrader/modules"
SANDBOX_BLUEPRINT="/var/www/tigergrader/sandbox/"
UPLOAD_FOLDER = "/var/www/tigergrader/upload"
MODULES = ["T1", "T2A"]
#MODULES = ["T1", "T2A", "T2B", "T3", "T4", "T5"]
SUBMISSION_TIMEOUT = 60*1000
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
EXPECTED_DIR = "src/"
POLICY_FILE = "test.policy"
POLICY='grant {{permission java.io.FilePermission "{input_file}", "read";}};'
BUILD_COMMAND="ant"
RUN_COMMAND="java"
RUN_OPTS = ["-cp",
         "lib/*:dist/lib/JTiger.jar",
         "-Djava.security.manager",
         "-Djava.security.policy={0}".format(POLICY_FILE)]
CPU_LIMIT = 60
AS_LIMIT = 1024*1024*4096
CELERY_BACKEND = 'amqp'
CELERY_BROKER = 'amqp://guest@localhost//'
DATABASE="/var/www/tigergrader/database.db"

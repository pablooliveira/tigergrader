SECRET_KEY = "SelectAVerySecretKeyToSignApplicationSessions"
ADMIN_USERNAME = "admin"
MODULE_FOLDER = "/var/www/tigergrader/modules"
UPLOAD_FOLDER = "/var/www/tigergrader/upload"
SANDBOX_BLUEPRINT="/var/www/tigergrader/sandbox/"
MODULES = ["T1", "T2A"]
SUBMISSION_TIMEOUT = 60*1000
MAX_CONTENT_LENGTH = 5 * 1024 * 1024
EXPECTED_DIR="src/"
POLICY_FILE="test.policy"
JOPTS=["-cp",
        "lib/*:dist/lib/JTiger.jar",
        "-Djava.security.manager",
        "-Djava.security.policy={0}".format(POLICY_FILE)
        ]
CPU_LIMIT=60
AS_LIMIT=1024*1024*2048
CELERY_BACKEND='amqp'
CELERY_BROKER='amqp://guest@localhost//'
DATABASE="/var/www/tigergrader/database.db"

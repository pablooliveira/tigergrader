#!/bin/bash
VERSION="0.1.0"
ADMIN_MAIL="tigergrader@example.com"
ADMIN_PASS="admintiger"
SERVER_NAME="tigergrader.local"
TIGERGRADER_HOME="/var/www/tigergrader"
TIGERGRADER_SETTINGS="${TIGERGRADER_HOME}/configuration.py"
LECTURE="example-lecture/"
#LECTURE="2013-lecture/"
export TIGERGRADER_SETTINGS 

# Install required packages
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install -y git apache2 libapache2-mod-wsgi python-virtualenv \
    dwdiff rabbitmq-server ant openjdk-6-jdk sqlite3 

# Create tigergrader deploy directory
mkdir -p ${TIGERGRADER_HOME}
cd ${TIGERGRADER_HOME}

# Create virtualenv 
virtualenv -q --distribute pythonenv
source pythonenv/bin/activate

pip install /vagrant/dist/tigergrader-${VERSION}.tar.gz

# Install wsgi configuration
mkdir -p wsgi

cat <<EOF > wsgi/tigergrader.wsgi
import sys
import os
activate_this = '${TIGERGRADER_HOME}/pythonenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
os.environ["TIGERGRADER_SETTINGS"] = "${TIGERGRADER_SETTINGS}" 
sys.path.insert(0, '${TIGERGRADER_HOME}')
from tigergrader import app as application
EOF
touch wsgi/index.html

# Configure Celery
wget https://raw.github.com/celery/celery/3.2-devel/extra/generic-init.d/celeryd \
    -O /etc/init.d/celeryd
chmod +x /etc/init.d/celeryd

cat <<EOF > /etc/default/celeryd
CELERYD_NODES="w1"
CELERYD_CHDIR="${TIGERGRADER_HOME}"
CELERYD_USER="tigergrader"
CELERYD_GROUP="tigergrader"
CELERYD_LOG_FILE="${TIGERGRADER_HOME}/celery/%N.log"
CELERYD_PID_FILE="${TIGERGRADER_HOME}/celery/%N.pid"
CELERY_BIN="${TIGERGRADER_HOME}/pythonenv/bin/celery"
CELERY_CONFIG_MODULE="celeryconfig"
CELERY_CREATE_DIRS=1
CELERY_APP="tigergrader.grader"
CELERYD_OPTS="--time-limit=300 --concurrency=4"
EOF

# Copy default configuration
cp /vagrant/vagrant/configuration.py ${TIGERGRADER_HOME}
cp -r /vagrant/${LECTURE}/modules ${TIGERGRADER_HOME}
cp -r /vagrant/${LECTURE}/sandbox ${TIGERGRADER_HOME}
mkdir -p ${TIGERGRADER_HOME}/upload/
cp -rf /vagrant/${LECTURE}/upload/*  ${TIGERGRADER_HOME}/upload/

cp -n /vagrant/${LECTURE}/database.db ${TIGERGRADER_HOME}

# Add user tigergrader
useradd -s /bin/false -b /var/www/ tigergrader

python -m tigergrader.initdb ${ADMIN_MAIL} ${ADMIN_PASS}

# Make everything owned by tigergrader user
chown -R tigergrader:tigergrader ${TIGERGRADER_HOME}


/etc/init.d/celeryd start

# Configure apache
cat <<EOF > /etc/apache2/sites-enabled/001-tigergrader 
<VirtualHost *:80>
    ServerName ${SERVER_NAME}
    ServerAdmin ${ADMIN_MAIL}
    LogLevel info
    DocumentRoot ${TIGERGRADER_HOME}/wsgi

    WSGIDaemonProcess tigergrader user=tigergrader group=tigergrader threads=5
    WSGIScriptAlias /tigergrader ${TIGERGRADER_HOME}/wsgi/tigergrader.wsgi

    <Directory ${TIGERGRADER_HOME}/wsgi>
        WSGIProcessGroup tigergrader
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
EOF

rm -f /etc/apache2/sites-enabled/000-default

/etc/init.d/apache2 reload
/etc/init.d/apache2 restart

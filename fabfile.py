from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
from os import path
env.hosts = [<>]
BASE_DIR='<>'
APP_NAME='<>'
USER_NAME='<>'
DEPLOY_DIR=BASE_DIR+APP_NAME
GIT_CLONE_URL='<>'
GIT_PUSH_URL='<>'
FCGI_PORT='<>'
CUR_DIR= path.abspath(path.dirname(__file__).decode('utf-8'))

def setup():
    """Sets up the remote Ubuntu server with pip, virtualenv , clones the repo"""
    with cd(BASE_DIR):
        run('sudo apt-get install python-setuptools python-dev build-essential')
        run('sudo easy_install -U pip')
        run('sudo pip install -U virtualenv')
        run('virtualenv --no-site-packages '+ DEPLOY_DIR)
    with cd(DEPLOY_DIR):
        run('git clone %s' % GIT_CLONE_URL)
        run('source bin/activate && pip -E . install -r %s/requirements.txt' % APP_NAME)

def upgrade():
    with cd(DEPLOY_DIR):
        run('source bin/activate && pip -E . install -r %s/requirements.txt' % APP_NAME)
        
def init():
    with cd(DEPLOY_DIR):
        run('source bin/activate')

def commit_deploy(rev='HEAD',comment='Commit'):
    """ Add, commit, push changes to git repo, and deploy"""
    local('git add . && git commit -m %s' % comment)
    deploy(rev)
    
def deploy(rev='HEAD'):
    """Push changes to remote git and deploy the app. Takes an argument 'rev' which can be used to deploy a particular revision."""
    local('git push %s master' % GIT_PUSH_URL)
    with cd(DEPLOY_DIR+'/'+APP_NAME):
        run('git pull')
    stop_fcgi()
    migrate_and_start()

def restart():
    """Restart the FCGI processes on deployment machine"""
    stop_fcgi()
    with cd("%s/%s/config" % (DEPLOY_DIR,APP_NAME)):
        run("source ../../bin/activate && ./manage.py runfcgi pidfile=%(base_dir)s/process.file outlog=%(base_dir)s/out.log errlog=%(base_dir)s/err.log host=127.0.0.1 port=%(port)s " % {'port':FCGI_PORT,'base_dir':DEPLOY_DIR},shell=True)

def stop_fcgi():
    """Stop the FCGI processes on deployment machine"""
    with cd(DEPLOY_DIR):
        print("Stopping FCGI....")
        with settings(warn_only=True):
            result=run("cat process.file |xargs kill -9")
            if result.failed: print "No FCGI running"
        #if exists(APP_NAME):run("unlink %s" % APP_NAME)

def migrate_and_start():
    """Run syncdb, migrate(south) and start the FCGI processes on deployment machine"""
    with cd("%s/%s/config" % (DEPLOY_DIR,APP_NAME)):
        print("Migrating database...")
        run('source ../../bin/activate && ./manage.py syncdb')
        run('source ../../bin/activate && ./manage.py migrate')
        print("Restarting server....")
        run("source ../../bin/activate && ./manage.py runfcgi pidfile=%(base_dir)s/process.file outlog=%(base_dir)s/out.log errlog=%(base_dir)s/err.log host=127.0.0.1 port=%(port)s " % {'port':FCGI_PORT,'base_dir':DEPLOY_DIR},shell=True)
        print("...Done!'")


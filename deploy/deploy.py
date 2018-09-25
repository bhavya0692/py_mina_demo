"""
py_mina deployfile
"""


from py_mina import *
from deploy import *
from git import Repo
from py_mina.subtasks.deploy import *
from py_mina.subtasks import (
    git_clone,
    create_shared_paths,
    link_shared_paths,
    rollback_release,
    force_unlock
)


# Settings - global


set('verbose', True)
set('keep_releases', 1)
#set('sudo_on_chown', True)
#set('sudo_on_chmod', True)
set('ask_unlock_if_locked', True)


# Settings - remote server connection


set('user', 'rails')
set('hosts', ['indopus.in'])


# Settings - application

set('deploy_to', '/home/rails/apps/vidvaan_deploy')
set('repository', 'git@github.com:Bizongo/vidvaan.git')
set('branch', 'master')


# Settings - shared [PUBLIC] files/dirs (application configs, assets, storage, etc.)


set('shared_dirs', ['logs'])
set('shared_files', ['config/config.py','config/google_credentials.json','startup.sh'])


# Settings - explicit owner of [PUBLIC] shared files/dirs


#set('owner_user', 'www-data')
#set('owner_group', 'www-data')


# Settings - protected shared files/dirs (db configs, certificates, keys, etc.)
#          * [PROTECTED] owner config settings are required to be set


#set('protected_shared_dirs', [])
#set('protected_shared_files', [])


# Settings - owner of [PROTECTED] shared files/dirs

#set('protected_owner_user', 'root')
#set('protected_owner_group', 'root')


# Tasks


@task
def restart():
    """
    Restarts application on remote server
    """

    with cd(fetch('current_path')):
        run('sudo supervisorctl restart vidvaan')


@deploy_task(on_success=restart)
def deploy():
    """
    Runs deploy process on remote staging server
    """
    
    repo = Repo('.')
    branch = repo.active_branch
    set('branch', branch.name)

    git_clone()
    link_shared_paths()

    #Activating the virtualenv
    run('source /home/rails/.virtualenvs/vidvaan-staging-python3/bin/activate')

    #Install dependencies
    run('sudo pip3 install -r requirements.txt')

    #Remove pycache from releases
    run('find ../.. | grep -E "(__pycache__|\.pyc|\.pyo$)" | sudo xargs rm -rf')


@setup_task
def setup():
    """
    Runs setup process on remote server
    """

    create_shared_paths()


@task(on_success=restart)
def rollback():
    """
    Rollbacks to previous release
    """

    rollback_release()


@task
def unlock():
    """
    Forces lockfile removal when previous deploy failed
    """

    force_unlock()


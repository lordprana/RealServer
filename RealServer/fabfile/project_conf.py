'''
--------------------------------------------------------------------------------------
project_conf.py
--------------------------------------------------------------------------------------
Configuration settings that detail your EC2 instances and other info about your Django
servers

author : Ashok Fernandez (github.com/ashokfernandez/)
credit : Derived from files in https://github.com/gcollazo/Fabulous
date   : 11 / 3 / 2014

Make sure you fill everything out that looks like it needs to be filled out, there are links
in the comments to help.
'''

import os.path

fabconf = {}

#  Do not edit
fabconf['FAB_CONFIG_PATH'] = os.path.dirname(__file__)

# Project name
fabconf['PROJECT_NAME'] = "RealServer"

# Username for connecting to EC2 instaces - Do not edit unless you have a
# reason to
fabconf['SERVER_USERNAME'] = "ubuntu"

# Full local path for .ssh
fabconf['SSH_PATH'] = "~/.ssh"

# Name of the private key file you use to connect to EC2 instances
fabconf['EC2_KEY_NAME'] = "realec2key.pem"

# Don't edit. Full path of the ssh key you use to connect to EC2 instances
fabconf[
    'SSH_PRIVATE_KEY_PATH'] = '%s/%s' % (fabconf['SSH_PATH'], fabconf['EC2_KEY_NAME'])

# Where to install apps
fabconf['APPS_DIR'] = "/home/%s/webapps" % fabconf['SERVER_USERNAME']

# Where you want your project installed: /APPS_DIR/PROJECT_NAME
fabconf[
    'PROJECT_PATH'] = "%s/%s" % (fabconf['APPS_DIR'], fabconf['PROJECT_NAME'])

# Your Django's version "run migrations" command
fabconf['RUN_MIGRATIONS_CMD'] = "python %s/manage.py syncdb" % fabconf['PROJECT_PATH']

# App domains
fabconf['DOMAINS'] = "getrealdating.com www.getrealdating.com"

# Path for virtualenvs
fabconf['VIRTUALENV_DIR'] = "/home/%s/.virtualenvs" % fabconf['SERVER_USERNAME']

# Email for the server admin
fabconf['ADMIN_EMAIL'] = "admin@getrealdating.com"

# Git username for the server
fabconf['GIT_USERNAME'] = "EC2"

# Name of the private key file used for git deployments
fabconf['GIT_DEPLOY_KEY_NAME'] = "id_rsa"

# Don't edit. Local path for deployment key you use for git
fabconf['GIT_DEPLOY_KEY_PATH'] = "%s/%s" % (
    fabconf['SSH_PATH'], fabconf['GIT_DEPLOY_KEY_NAME'])

# The top-level domain name for your remote git service
fabconf['GIT_HOST_DOMAIN'] = "github.com"

# Path to the repo of the application you want to install. The
# REPO_USERNAME could be same as the GIT_USERNAME if the repo is under the
# same account else, it is the org username (for orgs) or the username of
# the projects owner. The REPO_NAME can contain slashes (eg
# <project_name>/<repo_name> if you are using Bitbucket and the project is
# within a project)
fabconf['REPO_USERNAME'] = 'lordprana'
fabconf['REPO_NAME'] = 'RealServer'

# Creates the ssh location of your remote repo from the above details
fabconf['REPO_URL'] = "ssh://git@%s/%s/%s.git" % (
    fabconf['GIT_HOST_DOMAIN'], fabconf['REPO_USERNAME'], fabconf['REPO_NAME'])

# Virtualenv activate command
fabconf['ACTIVATE'] = "source /home/%s/.virtualenvs/%s/bin/activate" % (
    fabconf['SERVER_USERNAME'], fabconf['PROJECT_NAME'])

# Name tag for your server instance on EC2
fabconf['INSTANCE_NAME_TAG'] = "realserver"

# EC2 key. http://bit.ly/j5ImEZ
#fabconf['AWS_ACCESS_KEY'] = 'AKIAI4755USWAQYAFTUA'
fabconf['AWS_ACCESS_KEY'] = 'AKIAJ3TL7CI5VKSUMCYQ'

# EC2 secret. http://bit.ly/j5ImEZ
#fabconf['AWS_SECRET_KEY'] = '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'
fabconf['AWS_SECRET_KEY'] = 'hfh0rpAoQIFb4ofC9QdxjmD29osX9dqb7qwNjHTU'
# EC2 region. http://amzn.to/12jBkm7
ec2_region = 'us-west-2'

# AMI name. http://bit.ly/liLKxj
ec2_amis = ['ami-b7a114d7']

# Name of the keypair you use in EC2. http://bit.ly/ldw0HZ
ec2_keypair = 'realec2key'

# Name of the security group. http://bit.ly/kl0Jyn
ec2_secgroups = ['RealSecurityGroup']

# API Name of instance type. http://bit.ly/mkWvpn
ec2_instancetype = 't2.micro'

# Existing instances - add the public dns of your instances here when you have spawned them
fabconf['EC2_INSTANCES'] = [""]

# Fabric

[Fabric](https://www.fabfile.org) is a Python library for performing devops tasks. You can thing of it a bit like a
makefile on steroids for Python. Its api abstracts away the clunky way you would run shell commands in Python, check
return values and manage stdio. Tasks may be targetted at particular hosts or group of hosts.

# Using Fabric

    $ cd PyBitmessage
    $ fab <task_name>

For a list of available commands:

    $ fab -l

General fabric commandline help

    $ fab -h

Arguments can be given:

    $ fab task1:arg1=arg1value,arg2=arg2value task2:option1

Tasks target hosts. Hosts can be specified with -H, or roles can be defined and you can target groups of hosts with -R.
Furthermore, you can use -- to run arbitrary shell commands rather than tasks:

    $ fab -H localhost task1
    $ fab -R webservers -- sudo /etc/httpd restart

# Getting started

 * Install Fabric, fabric-virtualenv, virtualenvwrapper system-wide (log in to a new terminal afterwards if you're installing
   virtualenvwrappers for the first time)
    $ sudo apt install Fabric virtualenvwrapper; sudo pip install fabric-virtualenv
 * Create a virtualenv called pybitmessage and install fabfile/requirements.txt
    $ mkvirtualenv --system-site-packages pybitmessage-devops
    $ pip install -r fabfile/requirements.txt
 * Ensure you can ssh localhost with no intervention, which may include:
   * settings in ~/.ssh/config
   * authorized_keys file
   * load ssh key
   * check(!) and accept the host key
 * From the PyBitmessage directory you can now run fab commands!

# Rationale

There are a number of advantages that should benefit us:

 * Common tasks can be writen in Python and executed consistently
 * Common tasks are now under source control
 * All developers can run the same commands, if the underlying command sequence for a task changes (after review, obv)
   the user does not have to care
 * Tasks can be combined either programmatically or on the commandline and run in series or parallel
 * Whoee environemnts can be managed very effectively in conjunction with a configuration management system


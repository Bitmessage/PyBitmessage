# Fabric

[Fabric](https://www.fabfile.org) is a Python library for performing devops tasks. You can think of it a bit like a
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

 * Install [Fabric](http://docs.fabfile.org/en/1.14/usage/fab.html), 
   [fabric-virtualenv](https://pypi.org/project/fabric-virtualenv/) and
   [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) 
   system-wide using your preferred method.
 * Create a virtualenv called pybitmessage and install fabfile/requirements.txt
    $ mkvirtualenv -r fabfile/requirements.txt --system-site-packages pybitmessage-devops
 * Ensure you can ssh localhost with no intervention, which may include:
   * ssh [sshd_config server] and [ssh_config client] configuration
   * authorized_keys file
   * load ssh key
   * check(!) and accept the host key
 * From the PyBitmessage directory you can now run fab commands!

# Rationale

There are a number of advantages that should benefit us:

 * Common tasks can be written in Python and executed consistently
 * Common tasks are now under source control
 * All developers can run the same commands, if the underlying command sequence for a task changes (after review, obv)
   the user does not have to care
 * Tasks can be combined either programmatically or on the commandline and run in series or parallel
 * Whole environments can be managed very effectively in conjunction with a configuration management system

<a name="sshd_config"></a>
# /etc/ssh/sshd_config

If you're going to be using ssh to connect to localhost you want to avoid weakening your security. The best way of
doing this is blocking port 22 with a firewall. As a belt and braces approach you can also edit the
/etc/ssh/sshd_config file to restrict login further:

```
PubkeyAuthentication no

...

Match ::1
    PubkeyAuthentication yes
```
Adapted from [stackexchange](https://unix.stackexchange.com/questions/406245/limit-ssh-access-to-specific-clients-by-ip-address)

<a name="ssh_config"></a>
# ~/.ssh/config

Fabric will honour your ~/.ssh/config file for your convenience. Since you will spend more time with this key unlocked
than others you should use a different key:

```
Host localhost
    HostName localhost
    IdentityFile ~/.ssh/id_rsa_localhost

Host github
    HostName github.com
    IdentityFile ~/.ssh/id_rsa_github
```

# Ideas for further development

## Smaller 

 * Decorators and context managers are useful for accepting common params like verbosity, force or doing command-level help
 * if `git status` or `git status --staged` produce results, prefer that to generate the file list


## Larger

 * Support documentation translations, aim for current transifex'ed languages
 * Fabric 2 is finally out, go @bitprophet! Invoke/Fabric2 is a rewrite of Fabric supporting Python3. Probably makes
 sense for us to stick to the battle-hardened 1.x branch, at least until we support Python3.

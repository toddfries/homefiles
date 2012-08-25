#!/usr/bin/env python

"""
Fabric fabfile for .homefiles.
"""

import fabric.api
import paramiko
import socket

# Run in a non-interactive mode, calling abort anytime it would
# normally prompt the user for input.
fabric.api.env.abort_on_prompts = True

# We must run the shell as a login shell (-l) so that install.py can
# find files in ~/bin/
fabric.api.env.shell = "/bin/sh -l -c"

DEPLOY_HOSTS = [
#    "crookshanks",
    "deadeye",
    "missy",
    "molly",
    "penguin",
    "pepsi",
    "shadow",
    "tschutter@shadow:2222"
]


def _is_host_up(host, port):
    """Determine if we can connect to host."""
    # Set the timeout
    original_timeout = socket.getdefaulttimeout()
    new_timeout = 3
    socket.setdefaulttimeout(new_timeout)
    host_status = False
    try:
        paramiko.Transport((host, port))
        host_status = True
    except Exception:
        print "[%s] WARNING: Cannot connect to port %s." % (host, port)
    socket.setdefaulttimeout(original_timeout)
    return host_status


#@fabric.api.parallel # broken?
@fabric.api.hosts(DEPLOY_HOSTS)
def deploy():
    """Deploy .homefiles updates to known hosts."""
    if _is_host_up(fabric.api.env.host, int(fabric.api.env.port)):
        with fabric.api.cd("~/.homefiles"):
            fabric.api.run("git pull")
            fabric.api.run("python install.py")

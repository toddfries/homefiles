#!/usr/bin/env python
#
# Copyright (c) 2012-2012 Tom Schutter
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    - Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    - Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

"""
Installs files in tschutter/homefiles using symbolic links.
"""

from optparse import OptionParser
import os
import shutil
import sys


def file_in_path(filename):
    """Returns True if filename is in PATH."""
    path = os.getenv("PATH", os.defpath)
    for pathdir in path.split(os.pathsep):
        pathname = os.path.join(pathdir, filename)
        if os.path.exists(pathname):
            return True
    return False


def clean_link(options, linkname):
    """Delete link or backup files and dirs."""
    link_pathname = os.path.join(options.home, linkname)

    if os.path.islink(link_pathname):
        # The destination exists as a symbolic link.
        print "Deleting symbolic link '%s'." % link_pathname
        if not options.dryrun:
            os.unlink(link_pathname)

    elif os.path.exists(link_pathname):
        # The destination exists as a file or dir.  Back it up.
        print "Moving '%s' to '%s'." % (link_pathname, options.homefiles)
        if not options.dryrun:
            shutil.move(link_pathname, options.homefiles)


def make_link(options, enabled, filename, linkname=None):
    """If enabled is True, create a symbolic link from home/linkname to
    homefiles/filename.

    If linkname is not specified, it is the same as filename.
    """

    if linkname == None:
        linkname = filename

    # Determine the source and destination pathnames.
    file_pathname = os.path.join(options.homefiles, filename)
    link_pathname = os.path.join(options.home, linkname)

    # The target filename should always exist.
    if not os.path.exists(file_pathname):
        print "ERROR: File '%s' does not exist." % file_pathname
        sys.exit(1)

    if enabled and not options.force and os.path.islink(link_pathname):
        # The destination already exists as a symbolic link.  Delete it if
        # it points to the wrong place.
        try:
            samefile = os.path.samefile(file_pathname, link_pathname)
        except OSError:
            samefile = False
        if not samefile:
            clean_link(options, linkname)
        else:
            if options.verbose:
                print "Link already exists from '%s' to '%s'." % (
                    link_pathname,
                    file_pathname
                )
            return
    else:
        clean_link(options, linkname)

    if not enabled:
        return

    # Make the link target relative.  This usually makes the link
    # shorter in ls output.
    filedir = os.path.dirname(filename)
    link_target = os.path.relpath(
        file_pathname,
        os.path.join(options.home, filedir)
    )

    # Make the symbolic link from link_pathname to link_target.
    print "Creating symbolic link from '%s' to '%s'." % (
        link_pathname,
        link_target
    )
    if not options.dryrun:
        os.symlink(link_target, link_pathname)


def make_dot_link(options, enabled, filename):
    """Create a symbolic link from home/.filename to homefiles/filename.
    """
    return make_link(options, enabled, filename, "." + filename)


def link_dotfiles(options):
    """Create links in ${HOME} to dotfiles."""

    # Determine what platform we are on.
    uname = os.uname()
    is_ubuntu = uname[3].find("Ubuntu") >= 0
    is_cygwin = uname[0].startswith("CYGWIN")

    make_dot_link(options, True, "bournerc")
    clean_link(options, ".bash_profile")
    make_dot_link(options, os.path.exists("/bin/bash"), "bashrc")
    clean_link(options, ".emacs")
    if is_cygwin:
        make_dot_link(options, True, "emacs.d")  # WinEmacs
    else:
        make_dot_link(options, file_in_path("emacs"), "emacs.d")
    make_dot_link(options, file_in_path("vi"), "exrc")
    make_dot_link(options, file_in_path("git"), "gitconfig")
    make_dot_link(options, os.path.exists("/bin/ksh"), "kshrc")
    make_dot_link(options, file_in_path("mail"), "mailcap")
    make_dot_link(options, file_in_path("mg"), "mg")
    make_dot_link(options, True, "profile")
    make_dot_link(options, file_in_path("pylint"), "pylintrc")
    make_dot_link(options, file_in_path("screen"), "screenrc")
    make_dot_link(options, file_in_path("tmux"), "tmux.conf")
    make_dot_link(options, file_in_path("vi"), "vimrc")
    make_dot_link(options, file_in_path("xzgv"), "xzgvrc")
    make_dot_link(options, file_in_path("mintty"), "minttyrc")
    make_link(options, is_ubuntu, "Xdefaults", ".Xresources")
    make_link(options, not is_ubuntu, "Xdefaults", ".Xdefaults")


def link_binfiles(options):
    """Create links in ${HOME}/bin."""
    bindir = os.path.join(options.home, "bin")
    if not os.path.isdir(bindir):
        print "Creating dir '%s'." % bindir
        if not options.dryrun:
            os.mkdir(bindir)
    make_link(options, True, "bin/findfile")
    make_link(options, True, "bin/install-essentials")
    make_link(options, True, "bin/tgrep")
    make_link(options, True, "bin/tm")


def main():
    """main"""
    option_parser = OptionParser(
        usage="usage: %prog [options]\n" +
            "  Installs files in tschutter/homefiles using symbolic links."
    )
    option_parser.add_option(
        "--home",
        action="store",
        dest="home",
        metavar="DIR",
        default=os.path.expanduser("~"),
        help="specify directory to install to (default=%default)"
    )
    option_parser.add_option(
        "--force",
        action="store_true",
        dest="force",
        default=False,
        help="replace existing symbolic links"
    )
    option_parser.add_option(
        "-n",
        "--dry-run",
        action="store_true",
        dest="dryrun",
        default=False,
        help="print commands that would be executed, but do not execute them"
    )
    option_parser.add_option(
        "--verbose",
        action="store_true",
        dest="verbose",
        default=False,
        help="produce more verbose output"
    )

    (options, args) = option_parser.parse_args()
    if len(args) != 0:
        option_parser.error("invalid argument")

    options.homefiles = os.path.dirname(os.path.abspath(__file__))

    link_dotfiles(options)

    link_binfiles(options)

    return 0

if __name__ == "__main__":
    sys.exit(main())

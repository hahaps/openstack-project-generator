#!/usr/bin/env python
# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Interactive shell based on Django:
#
# Copyright (c) 2005, the Lawrence Journal-World
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be
#        used to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
  CLI interface for <project_name> management.
"""

from __future__ import print_function


import os
import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import migration
from oslo_log import log as logging

from <project_name> import i18n
i18n.enable_lazy()

# Need to register global_opts
from <project_name>.common import config  # noqa
from <project_name> import context
from <project_name> import db
from <project_name>.db import migration as db_migration
from <project_name>.db.sqlalchemy import api as db_api
from <project_name>.i18n import _
from <project_name> import objects
from <project_name> import version


CONF = cfg.CONF


# Decorators for actions
def args(*args, **kwargs):
    def _decorator(func):
        func.__dict__.setdefault('args', []).insert(0, (args, kwargs))
        return func
    return _decorator


class ShellCommands(object):
    def bpython(self):
        """Runs a bpython shell.

        Falls back to Ipython/python shell if unavailable
        """
        self.run('bpython')

    def ipython(self):
        """Runs an Ipython shell.

        Falls back to Python shell if unavailable
        """
        self.run('ipython')

    def python(self):
        """Runs a python shell.

        Falls back to Python shell if unavailable
        """
        self.run('python')

    @args('--shell', dest="shell",
          metavar='<bpython|ipython|python>',
          help='Python shell')
    def run(self, shell=None):
        """Runs a Python interactive interpreter."""
        if not shell:
            shell = 'bpython'

        if shell == 'bpython':
            try:
                import bpython
                bpython.embed()
            except ImportError:
                shell = 'ipython'
        if shell == 'ipython':
            try:
                from IPython import embed
                embed()
            except ImportError:
                try:
                    # Ipython < 0.11
                    # Explicitly pass an empty list as arguments, because
                    # otherwise IPython would use sys.argv from this script.
                    import IPython

                    shell = IPython.Shell.IPShell(argv=[])
                    shell.mainloop()
                except ImportError:
                    # no IPython module
                    shell = 'python'

        if shell == 'python':
            import code
            try:
                # Try activating rlcompleter, because it's handy.
                import readline
            except ImportError:
                pass
            else:
                # We don't have to wrap the following import in a 'try',
                # because we already know 'readline' was imported successfully.
                import rlcompleter    # noqa
                readline.parse_and_bind("tab:complete")
            code.interact()

    @args('--path', required=True, help='Script path')
    def script(self, path):
        """Runs the script from the specified path with flags set properly."""
        exec(compile(open(path).read(), path, 'exec'), locals(), globals())


def _db_error(caught_exception):
    print('%s' % caught_exception)
    print(_("The above error may show that the database has not "
            "been created.\nPlease create a database using "
            "'<project_name>-manage db sync' before running this command."))
    exit(1)


class DbCommands(object):
    """Class for managing the database."""

    def __init__(self):
        pass

    @args('version', nargs='?', default=None,
          help='Database version')
    def sync(self, version=None):
        """Sync the database up to the most recent version."""
        return db_migration.db_sync(version)

    def version(self):
        """Print the current database version."""
        print(migration.db_version(db_api.get_engine(),
                                   db_migration.MIGRATE_REPO_PATH,
                                   db_migration.INIT_VERSION))

    @args('age_in_days', type=int,
          help='Purge deleted rows older than age in days')
    def purge(self, age_in_days):
        """Purge deleted rows older than a given age from <project_name> tables."""
        age_in_days = int(age_in_days)
        if age_in_days <= 0:
            print(_("Must supply a positive, non-zero value for age"))
            exit(1)
        ctxt = context.get_admin_context()
        db.purge_deleted_rows(ctxt, age_in_days)


class VersionCommands(object):
    """Class for exposing the codebase version."""

    def __init__(self):
        pass

    def list(self):
        print(version.version_string())

    def __call__(self):
        self.list()


class ConfigCommands(object):
    """Class for exposing the flags defined by flag_file(s)."""

    def __init__(self):
        pass

    @args('param', nargs='?', default=None,
          help='Configuration parameter to display (default: %(default)s)')
    def list(self, param=None):
        """List parameters configured for <project_name>.

        Lists all parameters configured for <project_name> unless an optional argument
        is specified.  If the parameter is specified we only print the
        requested parameter.  If the parameter is not found an appropriate
        error is produced by .get*().
        """
        param = param and param.strip()
        if param:
            print('%s = %s' % (param, CONF.get(param)))
        else:
            for key, value in CONF.items():
                print('%s = %s' % (key, value))


class GetLogCommands(object):
    """Get logging information."""

    def errors(self):
        """Get all of the errors from the log files."""
        error_found = 0
        if CONF.log_dir:
            logs = [x for x in os.listdir(CONF.log_dir) if x.endswith('.log')]
            for file in logs:
                log_file = os.path.join(CONF.log_dir, file)
                lines = [line.strip() for line in open(log_file, "r")]
                lines.reverse()
                print_name = 0
                for index, line in enumerate(lines):
                    if line.find(" ERROR ") > 0:
                        error_found += 1
                        if print_name == 0:
                            print(log_file + ":-")
                            print_name = 1
                        print(_("Line %(dis)d : %(line)s") %
                              {'dis': len(lines) - index, 'line': line})
        if error_found == 0:
            print(_("No errors in logfiles!"))

    @args('num_entries', nargs='?', type=int, default=10,
          help='Number of entries to list (default: %(default)d)')
    def syslog(self, num_entries=10):
        """Get <num_entries> of the <project_name> syslog events."""
        entries = int(num_entries)
        count = 0
        log_file = ''
        if os.path.exists('/var/log/syslog'):
            log_file = '/var/log/syslog'
        elif os.path.exists('/var/log/messages'):
            log_file = '/var/log/messages'
        else:
            print(_("Unable to find system log file!"))
            sys.exit(1)
        lines = [line.strip() for line in open(log_file, "r")]
        lines.reverse()
        print(_("Last %s <project_name> syslog entries:-") % (entries))
        for line in lines:
            if line.find("<project_name>") > 0:
                count += 1
                print(_("%s") % (line))
            if count == entries:
                break

        if count == 0:
            print(_("No <project_name> entries in syslog!"))


CATEGORIES = {
    'config': ConfigCommands,
    'db': DbCommands,
    'logs': GetLogCommands,
    'shell': ShellCommands,
    'version': VersionCommands
}


def methods_of(obj):
    """Return non-private methods from an object.

    Get all callable methods of an object that don't start with underscore
    :return: a list of tuples of the form (method_name, method)
    """
    result = []
    for i in dir(obj):
        if callable(getattr(obj, i)) and not i.startswith('_'):
            result.append((i, getattr(obj, i)))
    return result


def add_command_parsers(subparsers):
    for category in CATEGORIES:
        command_object = CATEGORIES[category]()

        parser = subparsers.add_parser(category)
        parser.set_defaults(command_object=command_object)

        category_subparsers = parser.add_subparsers(dest='action')

        for (action, action_fn) in methods_of(command_object):
            parser = category_subparsers.add_parser(action)

            action_kwargs = []
            for args, kwargs in getattr(action_fn, 'args', []):
                parser.add_argument(*args, **kwargs)

            parser.set_defaults(action_fn=action_fn)
            parser.set_defaults(action_kwargs=action_kwargs)


category_opt = cfg.SubCommandOpt('category',
                                 title='Command categories',
                                 handler=add_command_parsers)


def get_arg_string(args):
    arg = None
    if args[0] == '-':
        # (Note)zhiteng: args starts with FLAGS.oparser.prefix_chars
        # is optional args. Notice that cfg module takes care of
        # actual ArgParser so prefix_chars is always '-'.
        if args[1] == '-':
            # This is long optional arg
            arg = args[2:]
        else:
            arg = args[1:]
    else:
        arg = args

    return arg


def fetch_func_args(func):
    fn_args = []
    for args, kwargs in getattr(func, 'args', []):
        arg = get_arg_string(args[0])
        fn_args.append(getattr(CONF.category, arg))

    return fn_args


def main():
    objects.register_all()
    """Parse options and call the appropriate class/method."""
    CONF.register_cli_opt(category_opt)
    script_name = sys.argv[0]
    if len(sys.argv) < 2:
        print(_("\nOpenStack <Project_name> version: %(version)s\n") %
              {'version': version.version_string()})
        print(script_name + " category action [<args>]")
        print(_("Available categories:"))
        for category in CATEGORIES:
            print(_("\t%s") % category)
        sys.exit(2)

    try:
        CONF(sys.argv[1:], project='<project_name>',
             version=version.version_string())
        logging.setup(CONF, "<project_name>")
    except cfg.ConfigDirNotFoundError as details:
        print(_("Invalid directory: %s") % details)
        sys.exit(2)
    except cfg.ConfigFilesNotFoundError:
        cfgfile = CONF.config_file[-1] if CONF.config_file else None
        if cfgfile and not os.access(cfgfile, os.R_OK):
            st = os.stat(cfgfile)
            print(_("Could not read %s. Re-running with sudo") % cfgfile)
            try:
                os.execvp('sudo', ['sudo', '-u', '#%s' % st.st_uid] + sys.argv)
            except Exception:
                print(_('sudo failed, continuing as if nothing happened'))

        print(_('Please re-run <project_name>-manage as root.'))
        sys.exit(2)

    fn = CONF.category.action_fn
    fn_args = fetch_func_args(fn)
    fn(*fn_args)

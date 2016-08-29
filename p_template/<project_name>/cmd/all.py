#!/usr/bin/env python
# Copyright 2011 OpenStack, LLC
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Starter script for All <project_name> services.

This script attempts to start all the <project_name> services in one process.  Each
service is started in its own greenthread.  Please note that exceptions and
sys.exit() on the starting of a service are logged and the script will
continue attempting to launch the rest of the services.

"""

import eventlet
eventlet.monkey_patch()

import sys

from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from <project_name> import i18n
i18n.enable_lazy()

# Need to register global_opts
from <project_name>.common import config  # noqa
from <project_name>.i18n import _LE
from <project_name> import objects
from <project_name> import rpc
from <project_name> import service
from <project_name> import utils
from <project_name> import version


CONF = cfg.CONF


# TODO(e0ne): get a rid of code duplication in <project_name>.cmd module in Mitaka
def main():
    objects.register_all()
    CONF(sys.argv[1:], project='<project_name>',
         version=version.version_string())
    logging.setup(CONF, "<project_name>")
    LOG = logging.getLogger('<project_name>.all')

    utils.monkey_patch()

    gmr.TextGuruMeditation.setup_autorun(version)

    rpc.init(CONF)

    launcher = service.process_launcher()
    # <project_name>-api
    try:
        server = service.WSGIService('osapi_<project_name>')
        launcher.launch_service(server, workers=server.workers or 1)
    except (Exception, SystemExit):
        LOG.exception(_LE('Failed to load osapi_<project_name>'))

    # <project_name>-<manager_service_name>
    try:
        launcher.launch_service(service.Service.create(binary="<project_name>-<manager_service_name>"))
    except (Exception, SystemExit):
        LOG.exception(_LE('Failed to load <project_name>-<manager_service_name>'))

    launcher.wait()

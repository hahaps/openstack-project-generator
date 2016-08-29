# Copyright (c) 2010 OpenStack Foundation
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

"""
Scheduler Service
"""

import eventlet
from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging as messaging

from <project_name> import manager


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class <Manager_service_name>Manager(manager.Manager):
    """<Manager_service_name> manager."""

    RPC_API_VERSION = '1.8'

    target = messaging.Target(version=RPC_API_VERSION)

    def __init__(self, service_name=None, *args, **kwargs):
        super(<Manager_service_name>Manager, self).__init__(*args, **kwargs)
        self._startup_delay = True

    def init_host_with_rpc(self):
        eventlet.sleep(CONF.periodic_interval)
        self._startup_delay = False

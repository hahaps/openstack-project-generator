# Copyright 2012, Red Hat, Inc.
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
Client side of the <manager_service_name> manager RPC API.
"""

from oslo_config import cfg
import oslo_messaging as messaging

from <project_name>.objects import base as objects_base
from <project_name> import rpc


CONF = cfg.CONF


class <Manager_service_name>API(object):
    """Client side of the <manager_service_name> rpc API.

    API version history:

        1.8 - Add sending object over RPC in create_consistencygroup method
    """

    RPC_API_VERSION = '1.0'

    def __init__(self):
        super(<Manager_service_name>API, self).__init__()
        target = messaging.Target(topic=CONF.<manager_service_name>_topic,
                                  version=self.RPC_API_VERSION)
        serializer = objects_base.<Project_name>ObjectSerializer()
        self.client = rpc.get_client(target, version_cap='1.8',
                                     serializer=serializer)

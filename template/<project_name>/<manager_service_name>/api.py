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

"""Handles all requests relating to <manager_service_name>."""

import functools

from oslo_config import cfg
from oslo_log import log as logging

from <project_name>.db import base
from <project_name>.objects import base as objects_base
import <project_name>.policy
from <project_name>.<manager_service_name> import rpcapi as <manager_service_name>_rpcapi


CONF = cfg.CONF

LOG = logging.getLogger(__name__)


def wrap_check_policy(func):
    """Check policy corresponding to the wrapped methods prior to execution

    This decorator requires the first 3 args of the wrapped function
    to be (self, context, <project_name>)
    """
    @functools.wraps(func)
    def wrapped(self, context, target_obj, *args, **kwargs):
        check_policy(context, func.__name__, target_obj)
        return func(self, context, target_obj, *args, **kwargs)

    return wrapped


def check_policy(context, action, target_obj=None):
    target = {
        'project_id': context.project_id,
        'user_id': context.user_id,
    }

    if isinstance(target_obj, objects_base.<Project_name>Object):
        # Turn object into dict so target.update can work
        target.update(target_obj.obj_to_primitive() or {})
    else:
        target.update(target_obj or {})

    _action = '<project_name>:%s' % action
    <project_name>.policy.enforce(context, _action, target)


class API(base.Base):
    """API for interacting with the <manager_service_name> manager."""

    def __init__(self, db_driver=None, image_service=None):
        self.<manager_service_name>_rpcapi = <manager_service_name>_rpcapi.<Manager_service_name>API()
        super(API, self).__init__(db_driver)

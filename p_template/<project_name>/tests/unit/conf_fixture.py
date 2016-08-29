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

import os

from oslo_config import cfg


CONF = cfg.CONF

CONF.import_opt('policy_file', '<project_name>.policy', group='oslo_policy')

def_vol_type = 'fake_vol_type'


def set_defaults(conf):
    conf.set_default('rpc_backend', '<project_name>.openstack.common.rpc.impl_fake')
    conf.set_default('connection', 'sqlite://', group='database')
    conf.set_default('sqlite_synchronous', False, group='database')
    conf.set_default('policy_file', '<project_name>.tests.unit/policy.json',
                     group='oslo_policy')
    conf.set_default('state_path', os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..')))
    conf.set_default('policy_dirs', [], group='oslo_policy')
    conf.set_default('auth_strategy', 'noauth')

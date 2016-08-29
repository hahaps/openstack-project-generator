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

"""Defines interface for DB access.

Functions in this module are imported into the <project_name>.db namespace. Call these
functions from <project_name>.db namespace, not the <project_name>.db.api namespace.

All functions in this module return objects that implement a dictionary-like
interface. Currently, many of these objects are sqlalchemy objects that
implement a dictionary interface. However, a future goal is to have all of
these objects be simple dictionaries.


"""

from oslo_config import cfg
from oslo_db import concurrency as db_concurrency
from oslo_db import options as db_options

db_opts = []


CONF = cfg.CONF
CONF.register_opts(db_opts)
db_options.set_defaults(CONF)
CONF.set_default('sqlite_db', '<project_name>.sqlite', group='database')

_BACKEND_MAPPING = {'sqlalchemy': '<project_name>.db.sqlalchemy.api'}


IMPL = db_concurrency.TpoolDbapiWrapper(CONF, _BACKEND_MAPPING)

# The maximum value a signed INT type may have
MAX_INT = 0x7FFFFFFF


###################

def dispose_engine():
    """Force the engine to establish new connections."""

    # FIXME(jdg): When using sqlite if we do the dispose
    # we seem to lose our DB here.  Adding this check
    # means we don't do the dispose, but we keep our sqlite DB
    # This likely isn't the best way to handle this

    if 'sqlite' not in IMPL.get_engine().name:
        return IMPL.dispose_engine()
    else:
        return

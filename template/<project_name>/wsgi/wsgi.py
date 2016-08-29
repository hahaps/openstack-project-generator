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

"""<Project_name> OS API WSGI application."""


import sys
import warnings

from <project_name> import objects

warnings.simplefilter('once', DeprecationWarning)

from oslo_config import cfg
from oslo_log import log as logging

from <project_name> import i18n
i18n.enable_lazy()

# Need to register global_opts
from <project_name>.common import config  # noqa
from <project_name> import rpc
from <project_name> import version
from <project_name>.wsgi import common as wsgi_common

CONF = cfg.CONF


def _application():
    objects.register_all()
    CONF(sys.argv[1:], project='<project_name>',
         version=version.version_string())
    logging.setup(CONF, "<project_name>")

    rpc.init(CONF)
    return wsgi_common.Loader().load_app(name='osapi_<project_name>')


application = _application()

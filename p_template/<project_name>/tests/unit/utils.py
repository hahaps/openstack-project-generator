#    Copyright 2011 OpenStack Foundation
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
#

import sys
import uuid

from oslo_service import loopingcall
import oslo_versionedobjects

from <project_name> import context


def get_test_admin_context():
    return context.get_admin_context()


class ZeroIntervalLoopingCall(loopingcall.FixedIntervalLoopingCall):
    def start(self, interval, **kwargs):
        kwargs['initial_delay'] = 0
        return super(ZeroIntervalLoopingCall, self).start(0, **kwargs)


def replace_obj_loader(testcase, obj):
    def fake_obj_load_attr(self, name):
        # This will raise KeyError for non existing fields as expected
        field = self.fields[name]

        if field.default != oslo_versionedobjects.fields.UnspecifiedDefault:
            value = field.default
        elif field.nullable:
            value = None
        elif isinstance(field, oslo_versionedobjects.fields.StringField):
            value = ''
        elif isinstance(field, oslo_versionedobjects.fields.IntegerField):
            value = 1
        elif isinstance(field, oslo_versionedobjects.fields.UUIDField):
            value = uuid.uuid4()
        setattr(self, name, value)

    testcase.addCleanup(setattr, obj, 'obj_load_attr', obj.obj_load_attr)
    obj.obj_load_attr = fake_obj_load_attr


file_spec = None


def get_file_spec():
    """Return a Python 2 and 3 compatible version of a 'file' spec.

    This is to be used anywhere that you need to do something such as
    mock.MagicMock(spec=file) to mock out something with the file attributes.

    Due to the 'file' built-in method being removed in Python 3 we need to do
    some special handling for it.
    """
    global file_spec
    # set on first use
    if file_spec is None:
        if sys.version_info[0] == 3:
            import _io
            file_spec = list(set(dir(_io.TextIOWrapper)).union(
                set(dir(_io.BytesIO))))
        else:
            file_spec = file

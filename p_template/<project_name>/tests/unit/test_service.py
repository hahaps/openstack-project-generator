
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
Unit Tests for remote procedure calls using queue
"""

import mock
from oslo_concurrency import processutils
from oslo_config import cfg

from <project_name> import exception
from <project_name> import manager
from <project_name> import rpc
from <project_name> import service
from <project_name> import test
from <project_name>.wsgi import common as wsgi


test_service_opts = [
    cfg.StrOpt("fake_manager",
               default="<project_name>.tests.unit.test_service.FakeManager",
               help="Manager for testing"),
    cfg.StrOpt("test_service_listen",
               default=None,
               help="Host to bind test service to"),
    cfg.IntOpt("test_service_listen_port",
               default=0,
               help="Port number to bind test service to"), ]

CONF = cfg.CONF
CONF.register_opts(test_service_opts)


class FakeManager(manager.Manager):
    """Fake manager for tests."""
    def __init__(self, host=None,
                 db_driver=None, service_name=None):
        super(FakeManager, self).__init__(host=host,
                                          db_driver=db_driver)

    def test_method(self):
        return 'manager'


class ExtendedService(service.Service):
    def test_method(self):
        return 'service'


class ServiceManagerTestCase(test.TestCase):
    """Test cases for Services."""

    def test_message_gets_to_manager(self):
        serv = service.Service('test',
                               'test',
                               'test',
                               '<project_name>.tests.unit.test_service.FakeManager')
        serv.start()
        self.assertEqual('manager', serv.test_method())

    def test_override_manager_method(self):
        serv = ExtendedService('test',
                               'test',
                               'test',
                               '<project_name>.tests.unit.test_service.FakeManager')
        serv.start()
        self.assertEqual('service', serv.test_method())


class ServiceTestCase(test.TestCase):
    """Test cases for Services."""

    def setUp(self):
        super(ServiceTestCase, self).setUp()
        self.host = 'foo'
        self.binary = '<project_name>-fake'
        self.topic = 'fake'

    def test_create(self):
        # NOTE(vish): Create was moved out of mock replay to make sure that
        #             the looping calls are created in StartService.
        app = service.Service.create(host=self.host,
                                     binary=self.binary,
                                     topic=self.topic)

        self.assertTrue(app)

    @mock.patch.object(rpc, 'get_server')
    @mock.patch('<project_name>.db')
    def test_service_stop_waits_for_rpcserver(self, mock_db, mock_rpc):
        serv = service.Service(
            self.host,
            self.binary,
            self.topic,
            '<project_name>.tests.unit.test_service.FakeManager'
        )
        serv.start()
        serv.stop()
        serv.wait()
        serv.rpcserver.start.assert_called_once_with()
        serv.rpcserver.stop.assert_called_once_with()
        serv.rpcserver.wait.assert_called_once_with()


class TestWSGIService(test.TestCase):

    def setUp(self):
        super(TestWSGIService, self).setUp()

    def test_service_random_port(self):
        with mock.patch.object(wsgi.Loader, 'load_app') as mock_load_app:
            test_service = service.WSGIService("test_service")
            self.assertEqual(0, test_service.port)
            test_service.start()
            self.assertNotEqual(0, test_service.port)
            test_service.stop()
            self.assertTrue(mock_load_app.called)

    def test_reset_pool_size_to_default(self):
        with mock.patch.object(wsgi.Loader, 'load_app') as mock_load_app:
            test_service = service.WSGIService("test_service")
            test_service.start()

            # Stopping the service, which in turn sets pool size to 0
            test_service.stop()
            self.assertEqual(0, test_service.server._pool.size)

            # Resetting pool size to default
            test_service.reset()
            test_service.start()
            self.assertEqual(1000, test_service.server._pool.size)
            self.assertTrue(mock_load_app.called)

    @mock.patch('<project_name>.wsgi.eventlet_server.Server')
    def test_workers_set_default(self, wsgi_server):
        test_service = service.WSGIService("osapi_<project_name>")
        self.assertEqual(processutils.get_worker_count(), test_service.workers)

    @mock.patch('<project_name>.wsgi.eventlet_server.Server')
    def test_workers_set_good_user_setting(self, wsgi_server):
        self.override_config('osapi_<project_name>_workers', 8)
        test_service = service.WSGIService("osapi_<project_name>")
        self.assertEqual(8, test_service.workers)

    @mock.patch('<project_name>.wsgi.eventlet_server.Server')
    def test_workers_set_zero_user_setting(self, wsgi_server):
        self.override_config('osapi_<project_name>_workers', 0)
        test_service = service.WSGIService("osapi_<project_name>")
        # If a value less than 1 is used, defaults to number of procs available
        self.assertEqual(processutils.get_worker_count(), test_service.workers)

    @mock.patch('<project_name>.wsgi.eventlet_server.Server')
    def test_workers_set_negative_user_setting(self, wsgi_server):
        self.override_config('osapi_<project_name>_workers', -1)
        self.assertRaises(exception.InvalidInput,
                          service.WSGIService,
                          "osapi_<project_name>")
        self.assertFalse(wsgi_server.called)


class OSCompatibilityTestCase(test.TestCase):
    def _test_service_launcher(self, fake_os):
        # Note(lpetrut): The <project_name>-<manager_service_name> service needs to be spawned
        # differently on Windows due to an eventlet bug. For this reason,
        # we must check the process launcher used.
        fake_process_launcher = mock.MagicMock()
        with mock.patch('os.name', fake_os):
            with mock.patch('<project_name>.service.process_launcher',
                            fake_process_launcher):
                launcher = service.get_launcher()
                if fake_os == 'nt':
                    self.assertEqual(service.Launcher, type(launcher))
                else:
                    self.assertEqual(fake_process_launcher(), launcher)

    def test_process_launcher_on_windows(self):
        self._test_service_launcher('nt')

    def test_process_launcher_on_linux(self):
        self._test_service_launcher('posix')

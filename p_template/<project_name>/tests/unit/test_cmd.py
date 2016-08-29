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
import six
import sys

try:
    from unittest import mock
except ImportError:
    import mock
from oslo_config import cfg


from <project_name>.cmd import all as <project_name>_all
from <project_name>.cmd import api as <project_name>_api
from <project_name>.cmd import manage as <project_name>_manage
from <project_name>.cmd import <manager_service_name> as <project_name>_<manager_service_name>
from <project_name> import test
from <project_name> import version

CONF = cfg.CONF


class Test<Project_name>ApiCmd(test.TestCase):
    """Unit test cases for python modules under <project_name>/cmd."""

    def setUp(self):
        super(Test<Project_name>ApiCmd, self).setUp()
        sys.argv = ['<project_name>-api']
        CONF(sys.argv[1:], project='<project_name>', version=version.version_string())

    def tearDown(self):
        super(Test<Project_name>ApiCmd, self).tearDown()

    @mock.patch('<project_name>.service.WSGIService')
    @mock.patch('<project_name>.service.process_launcher')
    @mock.patch('<project_name>.rpc.init')
    @mock.patch('<project_name>.utils.monkey_patch')
    @mock.patch('oslo_log.log.setup')
    def test_main(self, log_setup, monkey_patch, rpc_init, process_launcher,
                  wsgi_service):
        launcher = process_launcher.return_value
        server = wsgi_service.return_value
        server.workers = mock.sentinel.worker_count

        <project_name>_api.main()

        self.assertEqual('<project_name>', CONF.project)
        self.assertEqual(CONF.version, version.version_string())
        log_setup.assert_called_once_with(CONF, "<project_name>")
        monkey_patch.assert_called_once_with()
        rpc_init.assert_called_once_with(CONF)
        process_launcher.assert_called_once_with()
        wsgi_service.assert_called_once_with('osapi_<project_name>')
        launcher.launch_service.assert_called_once_with(server,
                                                        workers=server.workers)
        launcher.wait.assert_called_once_with()


class Test<Project_name>AllCmd(test.TestCase):

    def setUp(self):
        super(Test<Project_name>AllCmd, self).setUp()
        sys.argv = ['<project_name>-all']
        CONF(sys.argv[1:], project='<project_name>', version=version.version_string())

    def tearDown(self):
        super(Test<Project_name>AllCmd, self).tearDown()

    @mock.patch('<project_name>.rpc.init')
    @mock.patch('<project_name>.service.Service.create')
    @mock.patch('<project_name>.service.WSGIService')
    @mock.patch('<project_name>.service.process_launcher')
    @mock.patch('<project_name>.utils.monkey_patch')
    @mock.patch('oslo_log.log.getLogger')
    @mock.patch('oslo_log.log.setup')
    def test_main(self, log_setup, get_logger, monkey_patch, process_launcher,
                  wsgi_service, service_create, rpc_init):
        launcher = process_launcher.return_value
        server = wsgi_service.return_value
        server.workers = mock.sentinel.worker_count
        service = service_create.return_value

        <project_name>_all.main()

        self.assertEqual('<project_name>', CONF.project)
        self.assertEqual(CONF.version, version.version_string())
        log_setup.assert_called_once_with(CONF, "<project_name>")
        get_logger.assert_called_once_with('<project_name>.all')
        monkey_patch.assert_called_once_with()
        rpc_init.assert_called_once_with(CONF)
        process_launcher.assert_called_once_with()

        service_create.assert_has_calls([mock.call(binary='<project_name>-<manager_service_name>')])
        self.assertEqual(1, service_create.call_count)
        launcher.launch_service.assert_has_calls([mock.call(service)])
        self.assertEqual(2, launcher.launch_service.call_count)

        launcher.wait.assert_called_once_with()


class Test<Project_name><Manager_service_name>Cmd(test.TestCase):

    def setUp(self):
        super(Test<Project_name><Manager_service_name>Cmd, self).setUp()
        sys.argv = ['<project_name>-<manager_service_name>']
        CONF(sys.argv[1:], project='<project_name>', version=version.version_string())

    def tearDown(self):
        super(Test<Project_name><Manager_service_name>Cmd, self).tearDown()

    @mock.patch('<project_name>.service.wait')
    @mock.patch('<project_name>.service.serve')
    @mock.patch('<project_name>.service.Service.create')
    @mock.patch('<project_name>.utils.monkey_patch')
    @mock.patch('oslo_log.log.setup')
    def test_main(self, log_setup, monkey_patch, service_create,
                  service_serve, service_wait):
        server = service_create.return_value

        <project_name>_<manager_service_name>.main()

        self.assertEqual('<project_name>', CONF.project)
        self.assertEqual(CONF.version, version.version_string())
        log_setup.assert_called_once_with(CONF, "<project_name>")
        monkey_patch.assert_called_once_with()
        service_create.assert_called_once_with(binary='<project_name>-<manager_service_name>')
        service_serve.assert_called_once_with(server)
        service_wait.assert_called_once_with()


class Test<Project_name>ManageCmd(test.TestCase):

    def setUp(self):
        super(Test<Project_name>ManageCmd, self).setUp()
        sys.argv = ['<project_name>-manage']
        CONF(sys.argv[1:], project='<project_name>', version=version.version_string())

    def tearDown(self):
        super(Test<Project_name>ManageCmd, self).tearDown()

    @mock.patch('<project_name>.db.migration.db_sync')
    def test_db_commands_sync(self, db_sync):
        version = mock.MagicMock()
        db_cmds = <project_name>_manage.DbCommands()
        db_cmds.sync(version=version)
        db_sync.assert_called_once_with(version)

    @mock.patch('oslo_db.sqlalchemy.migration.db_version')
    def test_db_commands_version(self, db_version):
        db_cmds = <project_name>_manage.DbCommands()
        with mock.patch('sys.stdout', new=six.StringIO()):
            db_cmds.version()
            self.assertEqual(1, db_version.call_count)

    def test_config_commands_list(self):
        with mock.patch('sys.stdout', new=six.StringIO()) as fake_out:
            expected_out = ''
            for key, value in CONF.items():
                expected_out += '%s = %s' % (key, value) + '\n'

            config_cmds = <project_name>_manage.ConfigCommands()
            config_cmds.list()

            self.assertEqual(expected_out, fake_out.getvalue())

    def test_config_commands_list_param(self):
        with mock.patch('sys.stdout', new=six.StringIO()) as fake_out:
            CONF.set_override('host', 'fake')
            expected_out = 'host = fake\n'

            config_cmds = <project_name>_manage.ConfigCommands()
            config_cmds.list(param='host')

            self.assertEqual(expected_out, fake_out.getvalue())

    def test_get_log_commands_no_errors(self):
        with mock.patch('sys.stdout', new=six.StringIO()) as fake_out:
            CONF.set_override('log_dir', None)
            expected_out = 'No errors in logfiles!\n'

            get_log_cmds = <project_name>_manage.GetLogCommands()
            get_log_cmds.errors()

            self.assertEqual(expected_out, fake_out.getvalue())

    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.listdir')
    def test_get_log_commands_errors(self, listdir, open):
        CONF.set_override('log_dir', 'fake-dir')
        listdir.return_value = ['fake-error.log']

        with mock.patch('sys.stdout', new=six.StringIO()) as fake_out:
            open.return_value = six.StringIO(
                '[ ERROR ] fake-error-message')
            expected_out = ('fake-dir/fake-error.log:-\n'
                            'Line 1 : [ ERROR ] fake-error-message\n')

            get_log_cmds = <project_name>_manage.GetLogCommands()
            get_log_cmds.errors()

            self.assertEqual(expected_out, fake_out.getvalue())
            open.assert_called_once_with('fake-dir/fake-error.log', 'r')
            listdir.assert_called_once_with(CONF.log_dir)

    @mock.patch('six.moves.builtins.open')
    @mock.patch('os.path.exists')
    def test_get_log_commands_syslog_no_log_file(self, path_exists, open):
        path_exists.return_value = False

        get_log_cmds = <project_name>_manage.GetLogCommands()
        with mock.patch('sys.stdout', new=six.StringIO()):
            exit = self.assertRaises(SystemExit, get_log_cmds.syslog)
            self.assertEqual(1, exit.code)

            path_exists.assert_any_call('/var/log/syslog')
            path_exists.assert_any_call('/var/log/messages')

    def test_get_arg_string(self):
        args1 = "foobar"
        args2 = "-foo bar"
        args3 = "--foo bar"

        self.assertEqual("foobar", <project_name>_manage.get_arg_string(args1))
        self.assertEqual("foo bar", <project_name>_manage.get_arg_string(args2))
        self.assertEqual("foo bar", <project_name>_manage.get_arg_string(args3))

    @mock.patch('oslo_config.cfg.ConfigOpts.register_cli_opt')
    def test_main_argv_lt_2(self, register_cli_opt):
        script_name = '<project_name>-manage'
        sys.argv = [script_name]
        CONF(sys.argv[1:], project='<project_name>', version=version.version_string())

        with mock.patch('sys.stdout', new=six.StringIO()):
            exit = self.assertRaises(SystemExit, <project_name>_manage.main)
            self.assertTrue(register_cli_opt.called)
            self.assertEqual(2, exit.code)

    @mock.patch('oslo_config.cfg.ConfigOpts.__call__')
    @mock.patch('oslo_log.log.setup')
    @mock.patch('oslo_config.cfg.ConfigOpts.register_cli_opt')
    def test_main_sudo_failed(self, register_cli_opt, log_setup,
                              config_opts_call):
        script_name = '<project_name>-manage'
        sys.argv = [script_name, 'fake_category', 'fake_action']
        config_opts_call.side_effect = cfg.ConfigFilesNotFoundError(
            mock.sentinel._namespace)

        with mock.patch('sys.stdout', new=six.StringIO()):
            exit = self.assertRaises(SystemExit, <project_name>_manage.main)

            self.assertTrue(register_cli_opt.called)
            config_opts_call.assert_called_once_with(
                sys.argv[1:], project='<project_name>',
                version=version.version_string())
            self.assertFalse(log_setup.called)
            self.assertEqual(2, exit.code)

    @mock.patch('oslo_config.cfg.ConfigOpts.__call__')
    @mock.patch('oslo_config.cfg.ConfigOpts.register_cli_opt')
    def test_main(self, register_cli_opt, config_opts_call):
        script_name = '<project_name>-manage'
        sys.argv = [script_name, 'config', 'list']
        action_fn = mock.MagicMock()
        CONF.category = mock.MagicMock(action_fn=action_fn)

        <project_name>_manage.main()

        self.assertTrue(register_cli_opt.called)
        config_opts_call.assert_called_once_with(
            sys.argv[1:], project='<project_name>', version=version.version_string())
        self.assertTrue(action_fn.called)

    @mock.patch('oslo_config.cfg.ConfigOpts.__call__')
    @mock.patch('oslo_log.log.setup')
    @mock.patch('oslo_config.cfg.ConfigOpts.register_cli_opt')
    def test_main_invalid_dir(self, register_cli_opt, log_setup,
                              config_opts_call):
        script_name = '<project_name>-manage'
        fake_dir = 'fake-dir'
        invalid_dir = 'Invalid directory:'
        sys.argv = [script_name, '--config-dir', fake_dir]
        config_opts_call.side_effect = cfg.ConfigDirNotFoundError(fake_dir)

        with mock.patch('sys.stdout', new=six.StringIO()) as fake_out:
            exit = self.assertRaises(SystemExit, <project_name>_manage.main)
            self.assertTrue(register_cli_opt.called)
            config_opts_call.assert_called_once_with(
                sys.argv[1:], project='<project_name>',
                version=version.version_string())
            self.assertIn(invalid_dir, fake_out.getvalue())
            self.assertIn(fake_dir, fake_out.getvalue())
            self.assertFalse(log_setup.called)
            self.assertEqual(2, exit.code)

#    Copyright 2011 Justin Santa Barbara
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


import functools
import hashlib
import time

import mock
from oslo_config import cfg
import six

import <project_name>
from <project_name> import exception
from <project_name> import test
from <project_name> import utils


CONF = cfg.CONF


class ExecuteTestCase(test.TestCase):
    @mock.patch('<project_name>.utils.processutils.execute')
    def test_execute(self, mock_putils_exe):
        output = utils.execute('a', 1, foo='bar')
        self.assertEqual(mock_putils_exe.return_value, output)
        mock_putils_exe.assert_called_once_with('a', 1, foo='bar')

    @mock.patch('<project_name>.utils.get_root_helper')
    @mock.patch('<project_name>.utils.processutils.execute')
    def test_execute_root(self, mock_putils_exe, mock_get_helper):
        output = utils.execute('a', 1, foo='bar', run_as_root=True)
        self.assertEqual(mock_putils_exe.return_value, output)
        mock_helper = mock_get_helper.return_value
        mock_putils_exe.assert_called_once_with('a', 1, foo='bar',
                                                run_as_root=True,
                                                root_helper=mock_helper)

    @mock.patch('<project_name>.utils.get_root_helper')
    @mock.patch('<project_name>.utils.processutils.execute')
    def test_execute_root_and_helper(self, mock_putils_exe, mock_get_helper):
        mock_helper = mock.Mock()
        output = utils.execute('a', 1, foo='bar', run_as_root=True,
                               root_helper=mock_helper)
        self.assertEqual(mock_putils_exe.return_value, output)
        self.assertFalse(mock_get_helper.called)
        mock_putils_exe.assert_called_once_with('a', 1, foo='bar',
                                                run_as_root=True,
                                                root_helper=mock_helper)


class GetFromPathTestCase(test.TestCase):
    def test_tolerates_nones(self):
        f = utils.get_from_path

        input = []
        self.assertEqual([], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [None]
        self.assertEqual([], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': None}]
        self.assertEqual([], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': None}}]
        self.assertEqual([{'b': None}], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': None}}}]
        self.assertEqual([{'b': {'c': None}}], f(input, "a"))
        self.assertEqual([{'c': None}], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': None}}}, {'a': None}]
        self.assertEqual([{'b': {'c': None}}], f(input, "a"))
        self.assertEqual([{'c': None}], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': None}}}, {'a': {'b': None}}]
        self.assertEqual([{'b': {'c': None}}, {'b': None}], f(input, "a"))
        self.assertEqual([{'c': None}], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

    def test_does_select(self):
        f = utils.get_from_path

        input = [{'a': 'a_1'}]
        self.assertEqual(['a_1'], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': 'b_1'}}]
        self.assertEqual([{'b': 'b_1'}], f(input, "a"))
        self.assertEqual(['b_1'], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': 'c_1'}}}]
        self.assertEqual([{'b': {'c': 'c_1'}}], f(input, "a"))
        self.assertEqual([{'c': 'c_1'}], f(input, "a/b"))
        self.assertEqual(['c_1'], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': 'c_1'}}}, {'a': None}]
        self.assertEqual([{'b': {'c': 'c_1'}}], f(input, "a"))
        self.assertEqual([{'c': 'c_1'}], f(input, "a/b"))
        self.assertEqual(['c_1'], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': 'c_1'}}},
                 {'a': {'b': None}}]
        self.assertEqual([{'b': {'c': 'c_1'}}, {'b': None}], f(input, "a"))
        self.assertEqual([{'c': 'c_1'}], f(input, "a/b"))
        self.assertEqual(['c_1'], f(input, "a/b/c"))

        input = [{'a': {'b': {'c': 'c_1'}}},
                 {'a': {'b': {'c': 'c_2'}}}]
        self.assertEqual([{'b': {'c': 'c_1'}}, {'b': {'c': 'c_2'}}],
                         f(input, "a"))
        self.assertEqual([{'c': 'c_1'}, {'c': 'c_2'}], f(input, "a/b"))
        self.assertEqual(['c_1', 'c_2'], f(input, "a/b/c"))

        self.assertEqual([], f(input, "a/b/c/d"))
        self.assertEqual([], f(input, "c/a/b/d"))
        self.assertEqual([], f(input, "i/r/t"))

    def test_flattens_lists(self):
        f = utils.get_from_path

        input = [{'a': [1, 2, 3]}]
        self.assertEqual([1, 2, 3], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': [1, 2, 3]}}]
        self.assertEqual([{'b': [1, 2, 3]}], f(input, "a"))
        self.assertEqual([1, 2, 3], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': {'b': [1, 2, 3]}}, {'a': {'b': [4, 5, 6]}}]
        self.assertEqual([1, 2, 3, 4, 5, 6], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': [{'b': [1, 2, 3]}, {'b': [4, 5, 6]}]}]
        self.assertEqual([1, 2, 3, 4, 5, 6], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = [{'a': [1, 2, {'b': 'b_1'}]}]
        self.assertEqual([1, 2, {'b': 'b_1'}], f(input, "a"))
        self.assertEqual(['b_1'], f(input, "a/b"))

    def test_bad_xpath(self):
        f = utils.get_from_path

        self.assertRaises(exception.Error, f, [], None)
        self.assertRaises(exception.Error, f, [], "")
        self.assertRaises(exception.Error, f, [], "/")
        self.assertRaises(exception.Error, f, [], "/a")
        self.assertRaises(exception.Error, f, [], "/a/")
        self.assertRaises(exception.Error, f, [], "//")
        self.assertRaises(exception.Error, f, [], "//a")
        self.assertRaises(exception.Error, f, [], "a//a")
        self.assertRaises(exception.Error, f, [], "a//a/")
        self.assertRaises(exception.Error, f, [], "a/a/")

    def test_real_failure1(self):
        # Real world failure case...
        #  We weren't coping when the input was a Dictionary instead of a List
        # This led to test_accepts_dictionaries
        f = utils.get_from_path

        inst = {'fixed_ip': {'floating_ips': [{'address': '1.2.3.4'}],
                             'address': '192.168.0.3'},
                'hostname': ''}

        private_ips = f(inst, 'fixed_ip/address')
        public_ips = f(inst, 'fixed_ip/floating_ips/address')
        self.assertEqual(['192.168.0.3'], private_ips)
        self.assertEqual(['1.2.3.4'], public_ips)

    def test_accepts_dictionaries(self):
        f = utils.get_from_path

        input = {'a': [1, 2, 3]}
        self.assertEqual([1, 2, 3], f(input, "a"))
        self.assertEqual([], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = {'a': {'b': [1, 2, 3]}}
        self.assertEqual([{'b': [1, 2, 3]}], f(input, "a"))
        self.assertEqual([1, 2, 3], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = {'a': [{'b': [1, 2, 3]}, {'b': [4, 5, 6]}]}
        self.assertEqual([1, 2, 3, 4, 5, 6], f(input, "a/b"))
        self.assertEqual([], f(input, "a/b/c"))

        input = {'a': [1, 2, {'b': 'b_1'}]}
        self.assertEqual([1, 2, {'b': 'b_1'}], f(input, "a"))
        self.assertEqual(['b_1'], f(input, "a/b"))


class GenericUtilsTestCase(test.TestCase):

    @mock.patch('os.path.exists', return_value=True)
    def test_find_config(self, mock_exists):
        path = '/etc/<project_name>/<project_name>.conf'
        cfgpath = utils.find_config(path)
        self.assertEqual(path, cfgpath)

        mock_exists.return_value = False
        self.assertRaises(exception.ConfigNotFound,
                          utils.find_config,
                          path)

    def test_as_int(self):
        test_obj_int = '2'
        test_obj_float = '2.2'
        for obj in [test_obj_int, test_obj_float]:
            self.assertEqual(2, utils.as_int(obj))

        obj = 'not_a_number'
        self.assertEqual(obj, utils.as_int(obj))
        self.assertRaises(TypeError,
                          utils.as_int,
                          obj,
                          quiet=False)

    def test_is_int_like(self):
        self.assertTrue(utils.is_int_like(1))
        self.assertTrue(utils.is_int_like(-1))
        self.assertTrue(utils.is_int_like(0b1))
        self.assertTrue(utils.is_int_like(0o1))
        self.assertTrue(utils.is_int_like(0x1))
        self.assertTrue(utils.is_int_like('1'))
        self.assertFalse(utils.is_int_like(1.0))
        self.assertFalse(utils.is_int_like('abc'))

    def test_check_exclusive_options(self):
        utils.check_exclusive_options()
        utils.check_exclusive_options(something=None,
                                      pretty_keys=True,
                                      unit_test=True)

        self.assertRaises(exception.InvalidInput,
                          utils.check_exclusive_options,
                          test=True,
                          unit=False,
                          pretty_keys=True)

        self.assertRaises(exception.InvalidInput,
                          utils.check_exclusive_options,
                          test=True,
                          unit=False,
                          pretty_keys=False)

    def test_hostname_unicode_sanitization(self):
        hostname = u"\u7684.test.example.com"
        self.assertEqual("test.example.com",
                         utils.sanitize_hostname(hostname))

    def test_hostname_sanitize_periods(self):
        hostname = "....test.example.com..."
        self.assertEqual("test.example.com",
                         utils.sanitize_hostname(hostname))

    def test_hostname_sanitize_dashes(self):
        hostname = "----test.example.com---"
        self.assertEqual("test.example.com",
                         utils.sanitize_hostname(hostname))

    def test_hostname_sanitize_characters(self):
        hostname = "(#@&$!(@*--#&91)(__=+--test-host.example!!.com-0+"
        self.assertEqual("91----test-host.example.com-0",
                         utils.sanitize_hostname(hostname))

    def test_hostname_translate(self):
        hostname = "<}\x1fh\x10e\x08l\x02l\x05o\x12!{>"
        self.assertEqual("hello", utils.sanitize_hostname(hostname))

    def test_is_valid_boolstr(self):
        self.assertTrue(utils.is_valid_boolstr(True))
        self.assertTrue(utils.is_valid_boolstr('trUe'))
        self.assertTrue(utils.is_valid_boolstr(False))
        self.assertTrue(utils.is_valid_boolstr('faLse'))
        self.assertTrue(utils.is_valid_boolstr('yeS'))
        self.assertTrue(utils.is_valid_boolstr('nO'))
        self.assertTrue(utils.is_valid_boolstr('y'))
        self.assertTrue(utils.is_valid_boolstr('N'))
        self.assertTrue(utils.is_valid_boolstr(1))
        self.assertTrue(utils.is_valid_boolstr('1'))
        self.assertTrue(utils.is_valid_boolstr(0))
        self.assertTrue(utils.is_valid_boolstr('0'))

    @mock.patch('os.path.join', side_effect=lambda x, y: '/'.join((x, y)))
    def test_make_dev_path(self, mock_join):
        self.assertEqual('/dev/xvda', utils.make_dev_path('xvda'))
        self.assertEqual('/dev/xvdb1', utils.make_dev_path('xvdb', 1))
        self.assertEqual('/foo/xvdc1', utils.make_dev_path('xvdc', 1, '/foo'))

    @mock.patch('<project_name>.utils.execute')
    def test_read_file_as_root(self, mock_exec):
        out = mock.Mock()
        err = mock.Mock()
        mock_exec.return_value = (out, err)
        test_filepath = '/some/random/path'
        output = utils.read_file_as_root(test_filepath)
        mock_exec.assert_called_once_with('cat', test_filepath,
                                          run_as_root=True)
        self.assertEqual(out, output)

    def test_safe_parse_xml(self):

        normal_body = ('<?xml version="1.0" ?>'
                       '<foo><bar><v1>hey</v1><v2>there</v2></bar></foo>')

        def killer_body():
            return (("""<!DOCTYPE x [
                    <!ENTITY a "%(a)s">
                    <!ENTITY b "%(b)s">
                    <!ENTITY c "%(c)s">]>
                <foo>
                    <bar>
                        <v1>%(d)s</v1>
                    </bar>
                </foo>""") % {
                'a': 'A' * 10,
                'b': '&a;' * 10,
                'c': '&b;' * 10,
                'd': '&c;' * 9999,
            }).strip()

        dom = utils.safe_minidom_parse_string(normal_body)
        # Some versions of minidom inject extra newlines so we ignore them
        result = str(dom.toxml()).replace('\n', '')
        self.assertEqual(normal_body, result)

        self.assertRaises(ValueError,
                          utils.safe_minidom_parse_string,
                          killer_body())

    def test_xhtml_escape(self):
        self.assertEqual('&quot;foo&quot;', utils.xhtml_escape('"foo"'))
        self.assertEqual('&apos;foo&apos;', utils.xhtml_escape("'foo'"))

    def test_hash_file(self):
        data = b'Mary had a little lamb, its fleece as white as snow'
        flo = six.BytesIO(data)
        h1 = utils.hash_file(flo)
        h2 = hashlib.sha1(data).hexdigest()
        self.assertEqual(h1, h2)

    @mock.patch('paramiko.SSHClient')
    def test_create_channel(self, mock_client):
        test_width = 600
        test_height = 800
        mock_channel = mock.Mock()
        mock_client.invoke_shell.return_value = mock_channel
        utils.create_channel(mock_client, test_width, test_height)
        mock_client.invoke_shell.assert_called_once_with()
        mock_channel.resize_pty.assert_called_once_with(test_width,
                                                        test_height)

    @mock.patch('os.stat')
    def test_get_file_mode(self, mock_stat):
        class stat_result(object):
            st_mode = 0o777
            st_gid = 33333

        test_file = '/var/tmp/made_up_file'
        mock_stat.return_value = stat_result
        mode = utils.get_file_mode(test_file)
        self.assertEqual(0o777, mode)
        mock_stat.assert_called_once_with(test_file)

    @mock.patch('os.stat')
    def test_get_file_gid(self, mock_stat):

        class stat_result(object):
            st_mode = 0o777
            st_gid = 33333

        test_file = '/var/tmp/made_up_file'
        mock_stat.return_value = stat_result
        gid = utils.get_file_gid(test_file)
        self.assertEqual(33333, gid)
        mock_stat.assert_called_once_with(test_file)

    @mock.patch('<project_name>.utils.CONF')
    def test_get_root_helper(self, mock_conf):
        mock_conf.rootwrap_config = '/path/to/conf'
        self.assertEqual('sudo <project_name>-rootwrap /path/to/conf',
                         utils.get_root_helper())

    def test_list_of_dicts_to_dict(self):
        a = {'id': '1', 'color': 'orange'}
        b = {'id': '2', 'color': 'blue'}
        c = {'id': '3', 'color': 'green'}
        lst = [a, b, c]

        resp = utils.list_of_dicts_to_dict(lst, 'id')
        self.assertEqual(c['id'], resp['3']['id'])


class TemporaryChownTestCase(test.TestCase):
    @mock.patch('os.stat')
    @mock.patch('os.getuid', return_value=1234)
    @mock.patch('<project_name>.utils.execute')
    def test_get_uid(self, mock_exec, mock_getuid, mock_stat):
        mock_stat.return_value.st_uid = 5678
        test_filename = 'a_file'
        with utils.temporary_chown(test_filename):
            mock_exec.assert_called_once_with('chown', 1234, test_filename,
                                              run_as_root=True)
        mock_getuid.asset_called_once_with()
        mock_stat.assert_called_once_with(test_filename)
        calls = [mock.call('chown', 1234, test_filename, run_as_root=True),
                 mock.call('chown', 5678, test_filename, run_as_root=True)]
        mock_exec.assert_has_calls(calls)

    @mock.patch('os.stat')
    @mock.patch('os.getuid', return_value=1234)
    @mock.patch('<project_name>.utils.execute')
    def test_supplied_owner_uid(self, mock_exec, mock_getuid, mock_stat):
        mock_stat.return_value.st_uid = 5678
        test_filename = 'a_file'
        with utils.temporary_chown(test_filename, owner_uid=9101):
            mock_exec.assert_called_once_with('chown', 9101, test_filename,
                                              run_as_root=True)
        self.assertFalse(mock_getuid.called)
        mock_stat.assert_called_once_with(test_filename)
        calls = [mock.call('chown', 9101, test_filename, run_as_root=True),
                 mock.call('chown', 5678, test_filename, run_as_root=True)]
        mock_exec.assert_has_calls(calls)

    @mock.patch('os.stat')
    @mock.patch('os.getuid', return_value=5678)
    @mock.patch('<project_name>.utils.execute')
    def test_matching_uid(self, mock_exec, mock_getuid, mock_stat):
        mock_stat.return_value.st_uid = 5678
        test_filename = 'a_file'
        with utils.temporary_chown(test_filename):
            pass
        mock_getuid.asset_called_once_with()
        mock_stat.assert_called_once_with(test_filename)
        self.assertFalse(mock_exec.called)


class TempdirTestCase(test.TestCase):
    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.rmtree')
    def test_tempdir(self, mock_rmtree, mock_mkdtemp):
        with utils.tempdir(a='1', b=2) as td:
            self.assertEqual(mock_mkdtemp.return_value, td)
            self.assertFalse(mock_rmtree.called)
        mock_mkdtemp.assert_called_once_with(a='1', b=2)
        mock_rmtree.assert_called_once_with(mock_mkdtemp.return_value)

    @mock.patch('tempfile.mkdtemp')
    @mock.patch('shutil.rmtree', side_effect=OSError)
    def test_tempdir_error(self, mock_rmtree, mock_mkdtemp):
        with utils.tempdir(a='1', b=2) as td:
            self.assertEqual(mock_mkdtemp.return_value, td)
            self.assertFalse(mock_rmtree.called)
        mock_mkdtemp.assert_called_once_with(a='1', b=2)
        mock_rmtree.assert_called_once_with(mock_mkdtemp.return_value)


class WalkClassHierarchyTestCase(test.TestCase):
    def test_walk_class_hierarchy(self):
        class A(object):
            pass

        class B(A):
            pass

        class C(A):
            pass

        class D(B):
            pass

        class E(A):
            pass

        class_pairs = zip((D, B, E),
                          utils.walk_class_hierarchy(A, encountered=[C]))
        for actual, expected in class_pairs:
            self.assertEqual(expected, actual)

        class_pairs = zip((D, B, C, E), utils.walk_class_hierarchy(A))
        for actual, expected in class_pairs:
            self.assertEqual(expected, actual)


class MonkeyPatchTestCase(test.TestCase):
    """Unit test for utils.monkey_patch()."""
    def setUp(self):
        super(MonkeyPatchTestCase, self).setUp()
        self.example_package = '<project_name>.tests.unit.monkey_patch_example.'
        self.flags(
            monkey_patch=True,
            monkey_patch_modules=[self.example_package + 'example_a' + ':'
                                  + self.example_package
                                  + 'example_decorator'])

    def test_monkey_patch(self):
        utils.monkey_patch()
        <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION = []
        from <project_name>.tests.unit.monkey_patch_example import example_a
        from <project_name>.tests.unit.monkey_patch_example import example_b

        self.assertEqual('Example function', example_a.example_function_a())
        exampleA = example_a.ExampleClassA()
        exampleA.example_method()
        ret_a = exampleA.example_method_add(3, 5)
        self.assertEqual(8, ret_a)

        self.assertEqual('Example function', example_b.example_function_b())
        exampleB = example_b.ExampleClassB()
        exampleB.example_method()
        ret_b = exampleB.example_method_add(3, 5)

        self.assertEqual(8, ret_b)
        package_a = self.example_package + 'example_a.'
        self.assertTrue(
            package_a + 'example_function_a'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)

        self.assertTrue(
            package_a + 'ExampleClassA.example_method'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)
        self.assertTrue(
            package_a + 'ExampleClassA.example_method_add'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)
        package_b = self.example_package + 'example_b.'
        self.assertFalse(
            package_b + 'example_function_b'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)
        self.assertFalse(
            package_b + 'ExampleClassB.example_method'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)
        self.assertFalse(
            package_b + 'ExampleClassB.example_method_add'
            in <project_name>.tests.unit.monkey_patch_example.CALLED_FUNCTION)


class StringLengthTestCase(test.TestCase):
    def test_check_string_length(self):
        self.assertIsNone(utils.check_string_length(
                          'test', 'name', max_length=255))
        self.assertRaises(exception.InvalidInput,
                          utils.check_string_length,
                          11, 'name', max_length=255)
        self.assertRaises(exception.InvalidInput,
                          utils.check_string_length,
                          '', 'name', min_length=1)
        self.assertRaises(exception.InvalidInput,
                          utils.check_string_length,
                          'a' * 256, 'name', max_length=255)


class InvalidFilterTestCase(test.TestCase):
    def test_admin_allows_all_options(self):
        ctxt = mock.Mock(name='context')
        ctxt.is_admin = True

        filters = {'allowed1': None, 'allowed2': None, 'not_allowed1': None}
        fltrs_orig = {'allowed1': None, 'allowed2': None, 'not_allowed1': None}
        allowed_search_options = ('allowed1', 'allowed2')
        allowed_orig = ('allowed1', 'allowed2')

        utils.remove_invalid_filter_options(ctxt, filters,
                                            allowed_search_options)

        self.assertEqual(allowed_orig, allowed_search_options)
        self.assertEqual(fltrs_orig, filters)

    def test_admin_allows_some_options(self):
        ctxt = mock.Mock(name='context')
        ctxt.is_admin = False

        filters = {'allowed1': None, 'allowed2': None, 'not_allowed1': None}
        fltrs_orig = {'allowed1': None, 'allowed2': None, 'not_allowed1': None}
        allowed_search_options = ('allowed1', 'allowed2')
        allowed_orig = ('allowed1', 'allowed2')

        utils.remove_invalid_filter_options(ctxt, filters,
                                            allowed_search_options)

        self.assertEqual(allowed_orig, allowed_search_options)
        self.assertNotEqual(fltrs_orig, filters)
        self.assertEqual(allowed_search_options, tuple(sorted(filters.keys())))


class LogTracingTestCase(test.TestCase):

    def test_utils_setup_tracing(self):
        self.mock_object(utils, 'LOG')

        utils.setup_tracing(None)
        self.assertFalse(utils.TRACE_API)
        self.assertFalse(utils.TRACE_METHOD)
        self.assertEqual(0, utils.LOG.warning.call_count)

        utils.setup_tracing(['method'])
        self.assertFalse(utils.TRACE_API)
        self.assertTrue(utils.TRACE_METHOD)
        self.assertEqual(0, utils.LOG.warning.call_count)

        utils.setup_tracing(['method', 'api'])
        self.assertTrue(utils.TRACE_API)
        self.assertTrue(utils.TRACE_METHOD)
        self.assertEqual(0, utils.LOG.warning.call_count)

    def test_utils_setup_tracing_invalid_key(self):
        self.mock_object(utils, 'LOG')

        utils.setup_tracing(['fake'])

        self.assertFalse(utils.TRACE_API)
        self.assertFalse(utils.TRACE_METHOD)
        self.assertEqual(1, utils.LOG.warning.call_count)

    def test_utils_setup_tracing_valid_and_invalid_key(self):
        self.mock_object(utils, 'LOG')

        utils.setup_tracing(['method', 'fake'])

        self.assertFalse(utils.TRACE_API)
        self.assertTrue(utils.TRACE_METHOD)
        self.assertEqual(1, utils.LOG.warning.call_count)

    def test_trace_no_tracing(self):
        self.mock_object(utils, 'LOG')

        @utils.trace_method
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(None)

        result = _trace_test_method()

        self.assertEqual('OK', result)
        self.assertEqual(0, utils.LOG.debug.call_count)

    def test_utils_trace_method(self):
        self.mock_object(utils, 'LOG')

        @utils.trace_method
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['method'])

        result = _trace_test_method()
        self.assertEqual('OK', result)
        self.assertEqual(2, utils.LOG.debug.call_count)

    def test_utils_trace_api(self):
        self.mock_object(utils, 'LOG')

        @utils.trace_api
        def _trace_test_api(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['api'])

        result = _trace_test_api()
        self.assertEqual('OK', result)
        self.assertEqual(2, utils.LOG.debug.call_count)

    def test_utils_trace_method_default_logger(self):
        mock_log = self.mock_object(utils, 'LOG')

        @utils.trace_method
        def _trace_test_method_custom_logger(*args, **kwargs):
            return 'OK'
        utils.setup_tracing(['method'])

        result = _trace_test_method_custom_logger()

        self.assertEqual('OK', result)
        self.assertEqual(2, mock_log.debug.call_count)

    def test_utils_trace_method_inner_decorator(self):
        mock_logging = self.mock_object(utils, 'logging')
        mock_log = mock.Mock()
        mock_log.isEnabledFor = lambda x: True
        mock_logging.getLogger = mock.Mock(return_value=mock_log)

        def _test_decorator(f):
            def blah(*args, **kwargs):
                return f(*args, **kwargs)
            return blah

        @_test_decorator
        @utils.trace_method
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['method'])

        result = _trace_test_method(self)

        self.assertEqual('OK', result)
        self.assertEqual(2, mock_log.debug.call_count)
        # Ensure the correct function name was logged
        for call in mock_log.debug.call_args_list:
            self.assertTrue('_trace_test_method' in str(call))
            self.assertFalse('blah' in str(call))

    def test_utils_trace_method_outer_decorator(self):
        mock_logging = self.mock_object(utils, 'logging')
        mock_log = mock.Mock()
        mock_log.isEnabledFor = lambda x: True
        mock_logging.getLogger = mock.Mock(return_value=mock_log)

        def _test_decorator(f):
            def blah(*args, **kwargs):
                return f(*args, **kwargs)
            return blah

        @utils.trace_method
        @_test_decorator
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['method'])

        result = _trace_test_method(self)

        self.assertEqual('OK', result)
        self.assertEqual(2, mock_log.debug.call_count)
        # Ensure the incorrect function name was logged
        for call in mock_log.debug.call_args_list:
            self.assertFalse('_trace_test_method' in str(call))
            self.assertTrue('blah' in str(call))

    def test_utils_trace_method_outer_decorator_with_functools(self):
        mock_log = mock.Mock()
        mock_log.isEnabledFor = lambda x: True
        self.mock_object(utils.logging, 'getLogger', mock_log)
        mock_log = self.mock_object(utils, 'LOG')

        def _test_decorator(f):
            @functools.wraps(f)
            def wraps(*args, **kwargs):
                return f(*args, **kwargs)
            return wraps

        @utils.trace_method
        @_test_decorator
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['method'])

        result = _trace_test_method()

        self.assertEqual('OK', result)
        self.assertEqual(2, mock_log.debug.call_count)
        # Ensure the incorrect function name was logged
        for call in mock_log.debug.call_args_list:
            self.assertTrue('_trace_test_method' in str(call))
            self.assertFalse('wraps' in str(call))

    def test_utils_trace_method_with_exception(self):
        self.LOG = self.mock_object(utils, 'LOG')

        @utils.trace_method
        def _trace_test_method(*args, **kwargs):
            raise exception.APITimeout('test message')

        utils.setup_tracing(['method'])

        self.assertRaises(exception.APITimeout, _trace_test_method)

        exception_log = self.LOG.debug.call_args_list[1]
        self.assertTrue('exception' in str(exception_log))
        self.assertTrue('test message' in str(exception_log))

    def test_utils_trace_method_with_time(self):
        mock_logging = self.mock_object(utils, 'logging')
        mock_log = mock.Mock()
        mock_log.isEnabledFor = lambda x: True
        mock_logging.getLogger = mock.Mock(return_value=mock_log)

        mock_time = mock.Mock(side_effect=[3.1, 6])
        self.mock_object(time, 'time', mock_time)

        @utils.trace_method
        def _trace_test_method(*args, **kwargs):
            return 'OK'

        utils.setup_tracing(['method'])

        result = _trace_test_method(self)

        self.assertEqual('OK', result)
        return_log = mock_log.debug.call_args_list[1]
        self.assertTrue('2900' in str(return_log))

    def test_utils_trace_wrapper_class(self):
        mock_logging = self.mock_object(utils, 'logging')
        mock_log = mock.Mock()
        mock_log.isEnabledFor = lambda x: True
        mock_logging.getLogger = mock.Mock(return_value=mock_log)

        utils.setup_tracing(['method'])

        @six.add_metaclass(utils.TraceWrapperMetaclass)
        class MyClass(object):
            def trace_test_method(self):
                return 'OK'

        test_class = MyClass()
        result = test_class.trace_test_method()

        self.assertEqual('OK', result)
        self.assertEqual(2, mock_log.debug.call_count)

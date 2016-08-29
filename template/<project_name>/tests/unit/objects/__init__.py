from oslo_versionedobjects.tests import test_objects

from <project_name> import objects


class BaseObjectsTestCase(test_objects._LocalTest):
    def setUp(self):
        super(BaseObjectsTestCase, self).setUp()
        # Import <project_name> objects for test cases
        objects.register_all()

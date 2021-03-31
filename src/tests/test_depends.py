from pybitmessage import depends
from unittest import mock, TestCase


class TestDependencies(TestCase):

	# @mock.patch('src.depends.check_dependencies')
	def test_check_dependencies(self):
		'''Method is checking for dependencies are passing or not'''
		self.assertIsNone(depends.check_dependencies())

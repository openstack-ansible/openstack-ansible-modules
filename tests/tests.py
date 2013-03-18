import keystone_user
import mock
from nose.tools import assert_equal


def setup_foo_tenant():
    keystone = mock.MagicMock()
    tenant = mock.Mock()
    tenant.id = "21b505b9cbf84bdfba60dc08cc2a4b8d"
    tenant.name = "foo"
    tenant.description = "The foo tenant"
    keystone.tenants.list = mock.Mock(return_value=[tenant])
    return keystone


def test_tenant_exists_when_present():
    """ tenant_exists when tenant does exist"""
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    assert keystone_user.tenant_exists(keystone, "foo")


def test_tenant_exists_when_absent():
    """ tenant_exists when tenant does not exist"""
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    assert not keystone_user.tenant_exists(keystone, "bar")


def test_ensure_tenant_exists_when_present():
    """ ensure_tenant_exists when tenant does exists """

    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "foo",
                    "The foo tenant", False)

    # Assertions
    assert not changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")


def test_change_tenant_description():
    """ ensure_tenant_exists with a change in description """
    # Setup
    keystone = setup_foo_tenant()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "foo",
                    "The foo tenant with a description change", False)

    # Assertions
    assert changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")




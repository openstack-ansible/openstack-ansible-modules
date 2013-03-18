import keystone_user
import mock


def test_tenant_exists_tenant_present():
    # Setup
    keystone = mock.MagicMock()
    tenant = mock.Mock()
    tenant.name = "foo"
    keystone.tenants.list = mock.Mock(return_value=[tenant])

    # Code under test
    assert keystone_user.tenant_exists(keystone, "foo")


def test_tenant_exists_tenant_absent():
    # Setup
    keystone = mock.MagicMock()
    tenant = mock.Mock()
    tenant.name = "foo"
    keystone.tenants.list = mock.Mock(return_value=[tenant])

    # Code under test
    assert not keystone_user.tenant_exists(keystone, "bar")


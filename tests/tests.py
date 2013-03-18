import keystone_user
import mock
from nose.tools import assert_equal
from nose.plugins.skip import SkipTest


def setup_tenant_user_role():
    """Create a tenant, user, and role"""
    keystone = mock.MagicMock()

    tenant = mock.Mock()
    tenant.id = "21b505b9cbf84bdfba60dc08cc2a4b8d"
    tenant.name = "acme"
    tenant.description = "The acme tenant"
    keystone.tenants.list = mock.Mock(return_value=[tenant])

    user = mock.Mock()
    user.id = "24073d9426ab4bc59527955d7c486179"
    user.name = "johndoe"
    keystone.users.list = mock.Mock(return_value=[user])

    role = mock.Mock()
    role.id = "34a699ab89d04c38894bbf3d998e5229"
    role.name = "admin"
    keystone.roles.list = mock.Mock(return_value=[role])

    return keystone


def test_tenant_exists_when_present():
    """ tenant_exists when tenant does exist"""
    # Setup
    keystone = setup_tenant_user_role()

    # Code under test
    assert keystone_user.tenant_exists(keystone, "acme")


def test_tenant_exists_when_absent():
    """ tenant_exists when tenant does not exist"""
    # Setup
    keystone = setup_tenant_user_role()

    # Code under test
    assert not keystone_user.tenant_exists(keystone, "bar")


def test_ensure_tenant_exists_when_present():
    """ ensure_tenant_exists when tenant does exists """

    # Setup
    keystone = setup_tenant_user_role()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "acme",
                    "The acme tenant", False)

    # Assertions
    assert not changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")


def test_ensure_tenant_exists_when_absent():
    """ ensure_tenant_exists when tenant does not exist """
    # Setup
    keystone = setup_tenant_user_role()
    keystone.tenants.create = mock.Mock(return_value=mock.Mock(
        id="7c310f797aa045898e2884a975ab32ab"))

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "bar",
                    "The bar tenant", False)

    # Assertions
    assert changed
    assert_equal(id, "7c310f797aa045898e2884a975ab32ab")
    keystone.tenants.create.assert_called_with(tenant_name="bar",
                                               description="The bar tenant",
                                               enabled=True)


def test_ensure_user_exists_when_present():
    # Setup
    keystone = setup_tenant_user_role()

    # Code under test
    (changed, id) = keystone_user.ensure_user_exists(keystone,
                                 user_name="johndoe",
                                 password="12345",
                                 email="johndoe@example.com",
                                 tenant_name="acme",
                                 check_mode=False)

    # Assertions
    assert not changed
    assert_equal(id, "24073d9426ab4bc59527955d7c486179")


@mock.patch('keystone_user.ensure_user_exists')
def test_ensure_user_exists_when_absent(mock_ensure_user_exists):
    # Setup
    keystone = setup_tenant_user_role()
    mock_ensure_user_exists.return_value = (True,
                                       "1e31370740a14668a2d3267c39c7af07")

    # Code under test
    (changed, id) = keystone_user.ensure_user_exists(keystone,
                                 user_name="skippyjonjones",
                                 password="1234567",
                                 email="sjj@example.com",
                                 tenant_name="acme",
                                 check_mode=False)

    # Assertions
    assert changed
    assert_equal(id, "1e31370740a14668a2d3267c39c7af07")


def test_ensure_role_exists_when_present():
    # Setup
    keystone = setup_tenant_user_role()
    role = mock.Mock()
    role.id = "34a699ab89d04c38894bbf3d998e5229"
    role.name = "admin"
    keystone.roles.roles_for_user = mock.Mock(return_value=[role])

    # Code under test
    user = "johndoe"
    tenant = "acme"
    role = "admin"
    check_mode = False
    (changed, id) = keystone_user.ensure_role_exists(keystone, user, tenant,
                                                     role, check_mode)

    # Assertions
    assert not changed
    assert_equal(id, "34a699ab89d04c38894bbf3d998e5229")

def test_ensure_role_exists_when_absent():
    raise SkipTest("Not yet implemented")


@mock.patch('keystone_user.ensure_tenant_exists')
def test_dispatch_tenant_when_present(mock_ensure_tenant_exists):
    """ dispatch with tenant only"""
    # Setup
    keystone = setup_tenant_user_role()
    mock_ensure_tenant_exists.return_value = (True,
                                       "34469137412242129cd908e384717794")

    # Code under test
    res = keystone_user.dispatch(keystone, tenant="bar",
                           tenant_description="This is a bar")

    # Assertions
    mock_ensure_tenant_exists.assert_called_with(keystone, "bar",
                                                "This is a bar", False)
    assert_equal(res,
        dict(changed=True, id="34469137412242129cd908e384717794"))


def test_change_tenant_description():
    """ ensure_tenant_exists with a change in description """
    # Setup
    keystone = setup_tenant_user_role()

    # Code under test
    (changed, id) = keystone_user.ensure_tenant_exists(keystone, "acme",
                    "The foo tenant with a description change", False)

    # Assertions
    assert changed
    assert_equal(id, "21b505b9cbf84bdfba60dc08cc2a4b8d")


@mock.patch('keystone_user.ensure_user_exists')
def test_dispatch_user_when_present(mock_ensure_user_exists):
    """ dispatch with tenant and user"""
    # Setup
    keystone = setup_tenant_user_role()
    mock_ensure_user_exists.return_value = (True,
                                       "0a6f3697fc314279b1a22c61d40c0919")

    # Code under test
    res = keystone_user.dispatch(keystone, tenant="acme", user="root",
                                 email="admin@example.com",
                                 password="12345")

    # Assertions
    mock_ensure_user_exists.assert_called_with(keystone, "root",
                                               "12345", "admin@example.com",
                                               "acme", False)

    assert_equal(res,
        dict(changed=True, id="0a6f3697fc314279b1a22c61d40c0919"))


@mock.patch('keystone_user.ensure_role_exists')
def test_dispatch_role_present(mock_ensure_role_exists):
    """ dispatch with tenant, user and role"""
    keystone = setup_tenant_user_role()
    mock_ensure_role_exists.return_value = (True,
                                       "7df22b53d9c4405f92032c802178a31e")

    # Code under test
    res = keystone_user.dispatch(keystone, tenant="acme", user="root",
                                 role="admin")

    # Assertions
    mock_ensure_role_exists.assert_called_with(keystone, "root",
                                               "acme", "admin", False)
    assert_equal(res,
        dict(changed=True, id="7df22b53d9c4405f92032c802178a31e"))

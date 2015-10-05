import keystone_service
import mock
from nose.tools import assert_equal, assert_list_equal, assert_is_none
from nose import SkipTest


def setup():
    keystone = mock.MagicMock()
    service = mock.Mock(id="b6a7ff03f2574cd9b5c7c61186e0d781",
                        type="identity",
                        description="Keystone Identity Service")
    # Can't set <name> field in mock in initializer
    service.name = "keystone"
    keystone.services.list = mock.Mock(return_value=[service])
    endpoint = mock.Mock(id="600759628a214eb7b3acde39b1e85180",
                         service_id="b6a7ff03f2574cd9b5c7c61186e0d781",
                         publicurl="http://192.168.206.130:5000/v2.0",
                         internalurl="http://192.168.206.130:5000/v2.0",
                         adminurl="http://192.168.206.130:35357/v2.0",
                         region="RegionOne")
    keystone.endpoints.list = mock.Mock(return_value=[endpoint])
    return keystone


def setup_multi_region():
    keystone = mock.MagicMock()

    services = [
        mock.Mock(id="b6a7ff03f2574cd9b5c7c61186e0d781",
                  type="identity",
                  description="Keystone Identity Service"),
        mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346",
                  type="compute",
                  description="Compute Service")
    ]

    # Can't set <name> field in mock in initializer
    services[0].name = "keystone"
    services[1].name = "nova"

    keystone.services.list = mock.Mock(return_value=services)

    endpoints = [
        mock.Mock(id="600759628a214eb7b3acde39b1e85180",
                  service_id="b6a7ff03f2574cd9b5c7c61186e0d781",
                  publicurl="http://192.168.206.130:5000/v2.0",
                  internalurl="http://192.168.206.130:5000/v2.0",
                  adminurl="http://192.168.206.130:35357/v2.0",
                  region="RegionOne"),
        mock.Mock(id="6bdf5ed5e0a54df8b9a049bd263bba0c",
                  service_id="b6a7ff03f2574cd9b5c7c61186e0d781",
                  publicurl="http://192.168.206.130:5000/v2.0",
                  internalurl="http://192.168.206.130:5000/v2.0",
                  adminurl="http://192.168.206.130:35357/v2.0",
                  region="RegionTwo"),
        mock.Mock(id="cf65cfdc5b5a4fa39bfbe3d7e27f8526",
                  service_id="a7ebed35051147d4abbe2ee049eeb346",
                  publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
                  internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
                  adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
                  region="RegionTwo")
    ]

    keystone.endpoints.list = mock.Mock(return_value=endpoints)

    return keystone


@mock.patch('keystone_service.ensure_endpoint_absent')
@mock.patch('keystone_service.ensure_service_absent')
@mock.patch('keystone_service.ensure_present')
def test_dispatch_service_present(mock_ensure_present,
                                  mock_ensure_service_absent,
                                  mock_ensure_endpoint_absent):
    """ Dispatch: service present """
    # Setup
    mock_ensure_present.return_value = (True, None, None)
    manager = mock.MagicMock()
    manager.attach_mock(mock_ensure_present, 'ensure_present')
    manager.attach_mock(mock_ensure_service_absent, 'ensure_service_absent')
    manager.attach_mock(mock_ensure_endpoint_absent,
                        'ensure_endpoint_absent')

    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    state = "present"
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    region = "RegionOne"
    ignore_other_regions = False
    check_mode = False

    # Code under test
    keystone_service.dispatch(keystone, name, service_type, description,
                              public_url, internal_url, admin_url, region,
                              ignore_other_regions, state, check_mode)

    expected_calls = [mock.call.ensure_present(keystone, name, service_type,
                                               description, public_url,
                                               internal_url, admin_url, region,
                                               ignore_other_regions,
                                               check_mode)]

    assert_equal(manager.mock_calls, expected_calls)


@mock.patch('keystone_service.ensure_endpoint_absent')
@mock.patch('keystone_service.ensure_service_absent')
@mock.patch('keystone_service.ensure_present')
def test_dispatch_service_absent(mock_ensure_present,
                                 mock_ensure_service_absent,
                                 mock_ensure_endpoint_absent):
    """ Dispatch: service absent """
    # Setup
    mock_ensure_service_absent.return_value = True
    mock_ensure_endpoint_absent.return_value = True
    manager = mock.MagicMock()
    manager.attach_mock(mock_ensure_present, 'ensure_present')
    manager.attach_mock(mock_ensure_service_absent, 'ensure_service_absent')
    manager.attach_mock(mock_ensure_endpoint_absent,
                        'ensure_endpoint_absent')

    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    ignore_other_regions = False
    state = "absent"
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = False

    # Code under test
    keystone_service.dispatch(keystone, name, service_type, description,
                              public_url, internal_url, admin_url, region,
                              ignore_other_regions, state, check_mode)

    expected_calls = [
        mock.call.ensure_endpoint_absent(keystone, name, check_mode, region,
                                         ignore_other_regions),
        mock.call.ensure_service_absent(keystone, name, check_mode)
    ]

    assert_list_equal(manager.mock_calls, expected_calls)


def test_ensure_present_when_present():
    """ ensure_present when the service and endpoint are present """
    # Setup
    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    ignore_other_regions = False
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = False

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert not changed
    assert_equal(service_id, "b6a7ff03f2574cd9b5c7c61186e0d781")
    assert_equal(endpoint_id, "600759628a214eb7b3acde39b1e85180")


def test_ensure_present_when_present_multi_region():
    """ ensure_present when the service and endpoint are present in region """
    # Setup
    keystone = setup_multi_region()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    ignore_other_regions = True
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = False

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert not changed
    assert_equal(service_id, "b6a7ff03f2574cd9b5c7c61186e0d781")
    assert_equal(endpoint_id, "600759628a214eb7b3acde39b1e85180")


def test_ensure_present_when_present_check():
    """ ensure_present when the service and endpoint are present, check mode"""
    # Setup
    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    ignore_other_regions = False
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = True

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert not changed
    assert_equal(service_id, None)
    assert_equal(endpoint_id, None)


def test_ensure_present_when_absent():
    """ ensure_present when the service and endpoint are absent """
    # Setup
    keystone = setup()

    # Mock out the service and endpoint creates
    endpoint = mock.Mock(
            id="622386d836b14fd986d9cec7504d208a",
            publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            region="RegionOne")
    keystone.endpoints.create = mock.Mock(return_value=endpoint)
    service = mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create = mock.Mock(return_value=service)

    name = "nova"
    service_type = "compute"
    description = "Compute Service"
    public_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    internal_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    admin_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    region = "RegionOne"
    ignore_other_regions = False
    check_mode = False

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert changed
    assert_equal(service_id, "a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create.assert_called_with(name=name,
                                                service_type=service_type,
                                                description=description)
    assert_equal(endpoint_id, "622386d836b14fd986d9cec7504d208a")
    keystone.endpoints.create.assert_called_with(
        service_id="a7ebed35051147d4abbe2ee049eeb346",
        publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        region="RegionOne")


def test_ensure_present_when_absent_multi_region():
    """ ensure_present when the endpoint is absent in this region """
    # Setup
    keystone = setup_multi_region()

    # Mock out the service and endpoint creates
    endpoint = mock.Mock(
            id="622386d836b14fd986d9cec7504d208a",
            publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            region="RegionOne")
    keystone.endpoints.create = mock.Mock(return_value=endpoint)
    service = mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create = mock.Mock(return_value=service)
    keystone.endpoints.delete = mock.Mock()

    name = "nova"
    service_type = "compute"
    description = "Compute Service"
    public_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    internal_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    admin_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    region = "RegionOne"
    ignore_other_regions = True
    check_mode = False

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert changed
    assert_equal(service_id, "a7ebed35051147d4abbe2ee049eeb346")
    assert not keystone.services.create.called
    assert_equal(endpoint_id, "622386d836b14fd986d9cec7504d208a")
    keystone.endpoints.create.assert_called_with(
        service_id="a7ebed35051147d4abbe2ee049eeb346",
        publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
        region="RegionOne")
    assert not keystone.endpoints.delete.called


def test_ensure_present_when_absent_check():
    """ ensure_present when the service and endpoint are absent, check mode """
    # Setup
    keystone = setup()

    # Mock out the service and endpoint creates
    endpoint = mock.Mock(
            id="622386d836b14fd986d9cec7504d208a",
            publicurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            internalurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            adminurl="http://192.168.206.130:8774/v2/%(tenant_id)s",
            region="RegionOne")
    keystone.endpoints.create = mock.Mock(return_value=endpoint)
    service = mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create = mock.Mock(return_value=service)

    name = "nova"
    service_type = "compute"
    description = "Compute Service"
    public_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    internal_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    admin_url = "http://192.168.206.130:8774/v2/%(tenant_id)s"
    region = "RegionOne"
    ignore_other_regions = False
    check_mode = True

    # Code under test
    (changed, service_id, endpoint_id) = keystone_service.ensure_present(
            keystone, name, service_type, description, public_url,
            internal_url, admin_url, region, ignore_other_regions, check_mode)

    # Assertions
    assert changed
    assert_equal(service_id, None)
    assert not keystone.services.create.called
    assert_equal(endpoint_id, None)
    assert not keystone.endpoints.create.called


def test_get_endpoint_present():
    """ get_endpoint when endpoint is present """
    keystone = setup()

    endpoint = keystone_service.get_endpoint(keystone, "keystone", "RegionOne",
                                             False)

    assert_equal(endpoint.id, "600759628a214eb7b3acde39b1e85180")

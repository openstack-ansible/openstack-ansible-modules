import keystone_service
import mock
from nose.tools import assert_equal, assert_is_none
from nose.plugins.skip import SkipTest


def setup():
    keystone = mock.MagicMock()
    service = mock.Mock()
    service.id = "b6a7ff03f2574cd9b5c7c61186e0d781"
    service.name = "keystone"
    service.type = "identity"
    service.description = "Keystone Identity Service"
    keystone.services.list = mock.Mock(return_value=[service])
    return keystone


@mock.patch('keystone_service.ensure_endpoints_absent')
@mock.patch('keystone_service.ensure_service_absent')
@mock.patch('keystone_service.ensure_endpoints_present')
@mock.patch('keystone_service.ensure_service_present')
def test_dispatch_service_present(mock_ensure_service_present,
                                  mock_ensure_endpoints_present,
                                  mock_ensure_service_absent,
                                  mock_ensure_endpoints_absent):
    """ Dispatch: service present """
    # Setup
    manager = mock.MagicMock()
    manager.attach_mock(mock_ensure_service_present, 'ensure_service_present')
    manager.attach_mock(mock_ensure_service_absent, 'ensure_service_absent')
    manager.attach_mock(mock_ensure_endpoints_present,
                        'ensure_endpoints_present')
    manager.attach_mock(mock_ensure_endpoints_absent,
                        'ensure_endpoints_absent')

    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    state = "present"
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = False

    # Code under test
    keystone_service.dispatch(keystone, name, service_type, description,
            public_url, internal_url, admin_url, region, state, check_mode)

    expected_calls = [mock.call.ensure_service_present(keystone, name,
                                                       service_type,
                                                       description,
                                                       check_mode),
                      mock.call.ensure_endpoints_present(keystone, name,
                                                         public_url,
                                                         internal_url,
                                                         admin_url,
                                                         check_mode)]

    assert_equal(manager.mock_calls, expected_calls)


@mock.patch('keystone_service.ensure_endpoints_absent')
@mock.patch('keystone_service.ensure_service_absent')
@mock.patch('keystone_service.ensure_endpoints_present')
@mock.patch('keystone_service.ensure_service_present')
def test_dispatch_service_absent(mock_ensure_service_present,
                                  mock_ensure_endpoints_present,
                                  mock_ensure_service_absent,
                                  mock_ensure_endpoints_absent):
    """ Dispatch: service absent """
    # Setup
    manager = mock.MagicMock()
    manager.attach_mock(mock_ensure_service_present, 'ensure_service_present')
    manager.attach_mock(mock_ensure_service_absent, 'ensure_service_absent')
    manager.attach_mock(mock_ensure_endpoints_present,
                        'ensure_endpoints_present')
    manager.attach_mock(mock_ensure_endpoints_absent,
                        'ensure_endpoints_absent')

    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    region = "RegionOne"
    state = "absent"
    public_url = "http://192.168.206.130:5000/v2.0"
    internal_url = "http://192.168.206.130:5000/v2.0"
    admin_url = "http://192.168.206.130:35357/v2.0"
    check_mode = False

    # Code under test
    keystone_service.dispatch(keystone, name, service_type, description,
            public_url, internal_url, admin_url, region, state, check_mode)

    expected_calls = [
        mock.call.ensure_endpoints_absent(keystone, name, check_mode),
        mock.call.ensure_service_absent(keystone, name, check_mode)
    ]

    assert_equal(manager.mock_calls, expected_calls)


def test_ensure_service_present_when_present():
    """ ensure_services_present when the service is present"""
    # Setup
    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    check_mode = False

    # Code under test
    (changed, id) = keystone_service.ensure_service_present(keystone, name,
                        service_type, description, check_mode)

    # Assertions
    assert not changed
    assert_equal(id, "b6a7ff03f2574cd9b5c7c61186e0d781")

def test_ensure_service_present_when_present_check():
    """ ensure_services_present when the service is present, check mode"""
    # Setup
    keystone = setup()
    name = "keystone"
    service_type = "identity"
    description = "Keystone Identity Service"
    check_mode = True

    # Code under test
    (changed, id) = keystone_service.ensure_service_present(keystone, name,
                        service_type, description, check_mode)

    # Assertions
    assert not changed
    assert_equal(id, "b6a7ff03f2574cd9b5c7c61186e0d781")


def test_ensure_service_present_when_absent():
    """ ensure_services_present when the service is absent"""
    # Setup
    keystone = setup()
    service = mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create = mock.Mock(return_value=service)
    name = "nova"
    service_type = "compute"
    description = "Compute Service"
    check_mode = False

    # Code under test
    (changed, id) = keystone_service.ensure_service_present(keystone, name,
                        service_type, description, check_mode)

    # Assertions
    assert changed
    assert_equal(id, "a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create.assert_called_with(name=name,
                                                service_type=service_type,
                                                description=description)


def test_ensure_service_present_when_absent_check():
    """ ensure_services_present when the service is absent, check mode"""
    # Setup
    keystone = setup()
    service = mock.Mock(id="a7ebed35051147d4abbe2ee049eeb346")
    keystone.services.create = mock.Mock(return_value=service)
    name = "nova"
    service_type = "compute"
    description = "Compute Service"
    check_mode = True

    # Code under test
    (changed, id) = keystone_service.ensure_service_present(keystone, name,
                        service_type, description, check_mode)

    # Assertions
    assert changed
    assert_equal(id, None)
    assert not keystone.services.create.called


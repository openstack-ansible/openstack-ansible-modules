# Ansible modules for managing OpenStack

These are unofficial Ansible modules for managing OpenStack, which you may find useful until the official Ansible modules are implemented.

These will eventually be a dependency of the [openstack-ansible][1] repo for doing a test deployment of OpenStack into virtual machines managed by vagrant.

[1]: http://github.com/lorin/openstack-ansible

## keystone_manage

Initialize the keystone database:

    keystone_manage: action=db_sync

## keystone_user

Manage users, tenants, and roles

Create a tenant

    keystone_user: token=$admin_token tenant=demo tenant_description="Default Tenant"

Create a user

    keystone_user: token=$admin_token user=admin tenant=demo password=secrete

Create and apply a role:

    keystone_user: token=$admin_token role=admin user=admin tenant=demo

## keystone_service

Manage services and endpoints

    keystone_service: token=$admin_token name=keystone type=identity desecription="Identity Service" public_url="http://192.168.206.130:5000/v2.0" internal_url="http://192.168.206.130:5000/v2.0" admin_url="http://192.168.206.130:35357/v2.0"

You can use `url` as an alias for `public_url`. If you don't specify internal and admin urls, they will default to the same value of public url. For example:

    keystone_service: token=$admin_token name=nova type=compute description="Compute Service" url=http://192.168.206.130:8774/v2/%(tenant_id)s


## Not yet supported
- Disabled tenants
- Deleting users
- Deleting roles
- Deleting services
- Deleting endpoints
- Updating tenants
- Updating users
- Updating services
- Updating endpoints
- Multiple endpoints per service


## Will probably never be supported
- Non-unique names for tenants, users, roles, and services


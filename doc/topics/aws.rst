========================
Getting Started With AWS
========================

Amazon AWS is a very widely used public cloud platform and one of the core
platforms Salt Cloud has been built to support.

Set up the cloud config at ``/etc/salt/cloud``:

.. code-block:: yaml

    # Set up the location of the salt master
    minion:
      master: saltmaster.example.com

    # Set the AWS login data
    AWS.id: HJGRYCILJLKJYG
    AWS.key: 'kdjgfsgm;woormgl/aserigjksjdhasdfgn'
    AWS.keyname: test
    AWS.securitygroup: quick-start
    AWS.private_key: /root/test.pem

    # Set up an optional default cloud provider
    provider: AWS

    # Optionally configure default region
    AWS.location: ap-southeast-1
    AWS.availability_zone: ap-southeast-1b

    # Specify whether to use public or private IP for deploy script
    AWS.ssh_interface: public

    # Configure which user to use to run the deploy script
    AWS.ssh_username: ec2-user

Set up an initial profile at ``/etc/salt/cloud.profiles``:

.. code-block:: yaml

    base_aws:
      provider: aws
      image: ami-e565ba8c
      size: Micro Instance
      os: RHEL6

The profile can be realized now with a salt command:

.. code-block:: yaml

    # salt-cloud -p base_aws ami.example.com

The created virtual machine will be named ``ami.example.com`` in the amazon
cloud and will have the same salt ``id``.

Once the vm is created it will start up the Salt Minion and connect back to
the Salt Master.

Required Settings
=================

AWS has several options that are always required:

.. code-block:: yaml

    # Set the AWS login data
    AWS.id: HJGRYCILJLKJYG
    AWS.key: 'kdjgfsgm;woormgl/aserigjksjdhasdfgn'
    AWS.keyname: test
    AWS.securitygroup: quick-start
    AWS.private_key: /root/test.pem

Optional Settings
=================

AWS allows a location to be set for servers to be deployed in. Availability
zones exist inside regions, and may be added to increase specificity.

.. code-block:: yaml

    # Optionally configure default region
    AWS.location: ap-southeast-1
    AWS.availability_zone: ap-southeast-1b

AWS instances can have a public or private IP, or both. When an instance is
deployed, Salt Cloud needs to log into it via SSH to run the deploy script.
By default, the public IP will be used for this. If the salt-cloud command
is run from another AWS instance, the private IP should be used.

.. code-block:: yaml

    # Specify whether to use public or private IP for deploy script
    AWS.ssh_interface: public

AWS instances may not allow remote access to the root user by default. Instead,
another user must be used to run the deploy script using sudo. Some common
usernames include ec2-user (for Amazon Linux), ubuntu (for Ubuntu instances)
and bitnami (for images provided by Bitnami).

.. code-block:: yaml

    # Configure which user to use to run the deploy script
    AWS.ssh_username: ec2-user

Multiple usernames can be provided, in which case Salt Cloud will attempt to
guess the correct username. This is mostly useful in the main configuration
file:

.. code-block:: yaml

    AWS.ssh_username:
      - ec2-user
      - ubuntu
      - bitnami

Multiple security groups can also be specified in the same fashion:

.. code-block:: yaml

    AWS.securitygroup:
      - default
      - extra


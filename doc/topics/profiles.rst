VM Profiles
===========

Salt cloud designates virtual machines inside the profile configuration file.
The profile configuration file defaults to ``/etc/salt/cloud.profiles`` and is a
yaml configuration. The syntax for declaring profiles is simple:

.. code-block:: yaml

    fedora_rackspace:
      provider: rackspace
      image: Fedora 17
      size: 256 server
      script: Fedora

A few key peices of information need to be declared and can change based on the
public cloud provider. A number of additional parameters can also be inserted:

.. code-block:: yaml

    centos_rackspace:
      provider: rackspace
      image: CentOS 6.2
      size: 1024 server
      script: RHEL6
      minion:
        master: salt.example.com
      grains:
        role: webserver

Some parameters can be specified in the main Salt cloud config file and then
are applied to all cloud profiles. For instance if only a single cloud provider
is being used then the provider option can be declared in the Salt cloud config
file.

The 'script' option is the name of the bootstrap script that will be executed to turn the new instance into
a salt minion. If salt-cloud and the salt-minion are located on the same machine, salt-cloud will ensure that
the key for the new minion is automatically accepted by the master. If 'script: None' is specified, salt-cloud 
will just boot up the instance and will not run any scripts. The specific `OS: RHEL`, `OS: Ubuntu` design is being
deprecated in favor of new options that rely on the salt bootstrap script at http://bootstrap.saltstack.org. The new
style will use the following format ``script: python-bootstrap`` ``script: wget-bootstrap``.

New-Style Bootstrap Script Salt-Cloud 'OS' Options
--------------------------------------------------

.. code-block:: yaml

    curl-bootstrap-git
    curl-bootstrap
    python-bootstrap
    wget-bootstrap
    wget-bootstrap-nocert

Larger Example
--------------

.. code-block:: yaml

    rhel_aws:
      provider: aws
      image: ami-e565ba8c
      size: Micro Instance
      script: RHEL6
      minion:
          cheese: edam

    ubuntu_aws:
      provider: aws
      image: ami-7e2da54e
      size: Micro Instance
      script: Ubuntu
      minion:
          cheese: edam

    ubuntu_rackspace:
      provider: rackspace
      image: Ubuntu 12.04 LTS
      size: 256 server
      script: Ubuntu
      minion:
          cheese: edam

    fedora_rackspace:
      provider: rackspace
      image: Fedora 17
      size: 256 server
      script: Fedora
      minion:
          cheese: edam

    cent_linode:
      provider: linode
      image: CentOS 6.2 64bit
      size: Linode 512
      script: RHEL6

    cent_gogrid:
      provider: gogrid
      image: 12834
      size: 512MB
      script: RHEL6

    cent_joyent:
      provider: joyent
      image: centos-6
      script: RHEL6
      size: Small 1GB

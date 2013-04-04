==========
Salt Cloud
==========

Salt Cloud is a tool for provisioning salted minions across various cloud
providers. Currently supported providers are:

.. code-block:: yaml

    - Amazon EC2
    - Eucalyptus (using EC2)
    - GoGrid
    - HP Cloud (using OpenStack)
    - Joyent
    - Linode
    - OpenStack
    - Rackspace (using OpenStack)

The salt-cloud command can be used to query configured providers, create VMs on
them, deploy salt-minion on those VMs and destroy them when no longer needed.

Salt Cloud requires Salt to be installed, but does not require any Salt daemons
to be running. However, if used in a salted environment, it is best to run Salt
Cloud on the salt-master, so that it can properly lay down salt keys when it
deploys machines, and then properly remove them later. If Salt Cloud is run in
this manner, minions will automatically be approved by the master; no need to
manually authenticate them later.


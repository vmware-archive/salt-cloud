:orphan:

.. _contents:

.. warning:: Outdated documentation

    The ``salt-cloud`` project `has been merged into the main Salt repository
    as of Salt's 2014.1 release`__.

    .. __: http://docs.saltstack.com/en/latest/topics/releases/2014.1.0.html#salt-cloud-merged-into-salt

    We recommend installing salt-cloud using a package manager as usual. Some
    distributions (RHEL/Cent) have split packages and so the package name will
    be ``salt-cloud`` and require a separate install. Some distributions do not
    split packages and it will be bundled within the ``salt-master`` package.

    Verify which version you have installed by running ``salt-cloud
    --version``; if the version number does not start with ``2014`` you are
    running an old release.

    No further development will take place in this repository. It will be left
    in the current state for historical purposes. Issues should be filed on the
    Salt repository.

    Current documentation now lives within the main Salt documentation.

    * `The main salt-cloud Table of Contents
      <http://docs.saltstack.com/en/latest/topics/cloud/index.html>`_
    * `Full list of cloud modules
      <http://docs.saltstack.com/en/latest/salt-modindex.html#cap-c>`_
    * `Archived release notes
      <http://docs.saltstack.com/en/latest/topics/cloud/releases/index.html>`_

    The documentation for the final salt-cloud release, v0.8.11, is included
    below.

----------

Salt Cloud Documentation
========================

Salt cloud is a public cloud provisioning tool. Salt cloud is made to integrate
Salt into cloud providers in a clean way so that minions on public cloud
systems can be quickly and easily modeled and provisioned.

Salt cloud allows for cloud based minions to be managed via virtual machine
maps and profiles. This means that individual cloud VMs can be created, or
large groups of cloud VMs can be created at once or managed.

Virtual machines created with Salt cloud install salt on the target virtual
machine and assign it to the specified master. This means that virtual
machines can be provisioned and then potentially never logged into.

While Salt Cloud has been made to work with Salt, it is also a generic
cloud management platform and can be used to manage non Salt centric clouds.

Getting Started
===============

* :doc:`Installing salt cloud <topics/install/index>`

Some quick guides covering getting started with Amazon AWS, Rackspace, and
Parallels.

* :doc:`Getting Started With AWS <topics/aws>`
* :doc:`Getting Started With Rackspace <topics/rackspace>`
* :doc:`Getting Started With Parallels <topics/parallels>`
* :doc:`Getting Started With SoftLayer <topics/softlayer>`

Core Configuration
==================

The core configuration of Salt cloud is handled in the cloud configuration
file. This file is comprised of global configurations for interfacing with
cloud providers.

* :doc:`Core Configuration <topics/config>`

Windows Configuration
=====================

Salt Cloud may be used to spin up a Windows minion, and then install the Salt
Minion client on that instance. At this time, Salt Cloud itself still needs to
be run from a Linux or Unix machine.

* :doc:`Windows Configuration <topics/windows>`

Using Salt Cloud
================

Salt cloud works via profiles and maps. Simple profiles for cloud VMs are
defined and can be used directly, or a map can be defined specifying
a large group of virtual machines to create.

* :doc:`Profiles <topics/profiles>`
* :doc:`Maps <topics/map>`

Once a VM has been deployed, a number of actions may be available to perform
on it, depending on the specific cloud provider.

* :doc:`Actions <topics/action>`

Depending on your cloud provider, a number of functions may also be available
which do not require a VM to be specified.

* :doc:`Functions <topics/function>`

Miscellaneous Options
=====================

* :doc:`Miscellaneous <topics/misc>`

Extending Salt Cloud
====================

Salt cloud extensions work in a way similar to Salt modules. Therefore
extending Salt cloud to manage more public cloud providers and operating
systems is easy.

* :doc:`Adding Cloud Providers <topics/cloud>`
* :doc:`Adding OS Support <topics/deploy>`

Feature Comparison
==================

A table is available which compares various features available across all
supported cloud providers.

* :doc:`Features <topics/features>`

Releases
========

* :doc:`Release Notes <topics/releases/index>`

Reference
=========

* :doc:`Command-line interface <ref/cli/salt-cloud>`

* :doc:`Full table of contents </contents>`

===================================
``salt-cloud`` is Now Part of Salt!
===================================

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

Frequently asked questions
--------------------------

What Salt release includes ``salt-cloud``?
    Salt will include native ``salt-cloud`` in the `Salt Hydrogen release`__.

    .. __: https://github.com/saltstack/salt/issues?milestone=39

What does this mean for the future of ``salt-cloud``?
    One fewer dependency.

    ``salt-cloud`` will continue to operate in the same way and the config
    files will live in the same location as before. The only end-user
    difference is ``salt-cloud`` will not need to be installed as a separate
    package.

What will happen to the ``salt-cloud`` repository and issue tracker?
    We will leave the ``salt-cloud`` repository in place on GitHub for the
    foreseeable future. It will contain this deprecation notice and serve as a
    historical reference.

Has the commit history and authorship for ``salt-cloud`` been lost?
    **No!**

    We have merged these two repositories using ``git mv`` followed by a
    regular ``git merge`` that preserves all the rich Git history and
    authorship of ``salt-cloud``. All commits made to ``salt-cloud`` can be
    referenced using the exact same SHA1 in the Salt repository.

    In order to view the full history of a file that came from the
    ``salt-cloud`` repository from within the Salt repository use the
    ``--follow`` flag in Git. Unfortunately, at the time of writing, GitHub's
    history view does not include this flag. For example, to view the full
    history of the ``ec2`` driver::

        git log --follow path/to/clouds/ec2.py

    Note, any commit messages that reference GitHub issues from a commit from
    ``salt-cloud`` will get confused and link to the corresponding issue in the
    Salt repository (if there is one of that same issue number).


.. image:: https://badges.gitter.im/saltstack/salt-cloud.svg
   :alt: Join the chat at https://gitter.im/saltstack/salt-cloud
   :target: https://gitter.im/saltstack/salt-cloud?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
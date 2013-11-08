===================================
``salt-cloud`` is Now Part of Salt!
===================================

.. note:: This repository is deprecated.

    All new pull requests and issues should be filed against the `main Salt
    repository`__.

The Salt team is excited to report that the ``salt-cloud`` repository has been
merged into the main Salt repository.

The merge happened on November 8th, 2013 in `pull request #8352`__.

.. __: https://github.com/saltstack/salt
.. __: https://github.com/saltstack/salt/pull/8352

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

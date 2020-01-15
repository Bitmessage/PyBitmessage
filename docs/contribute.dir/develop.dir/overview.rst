Developing 
==========

Devops tasks
------------

Bitmessage makes use of fabric_ to define tasks such as building documentation or running checks and tests on the code. If you can install 

.. _fabric: https://fabfile.org

Code style and linters
----------------------

We aim to be PEP8 compliant but we recognize that we have a long way still to go. Currently we have style and lint exceptions specified at the most specific place we can. We are ignoring certain issues project-wide in order to avoid alert-blindness, avoid style and lint regressions and to allow continuous integration to hook into the output from the tools. While it is hoped that all new changes pass the checks, fixing some existing violations are mini-projects in themselves. Current thinking on ignorable violations is reflected in the options and comments in setup.cfg. Module and line-level lint warnings represent refactoring opportunities.

Pull requests
-------------

There is a template at PULL_REQUEST_TEMPLATE.md that appears in the pull-request description. Please replace this text with something appropriate to your changes based on the ideas in the template.

Bike-shedding
-------------

Beyond having well-documented, Pythonic code with static analysis tool checks, extensive test coverage and powerful devops tools, what else can we have? Without violating any linters there is room for making arbitrary decisions solely for the sake of project consistency. These are the stuff of the pedant's PR comments. Rather than have such conversations in PR comments, we can lay out the result of discussion here.

I'm putting up a strawman for each topic here, mostly based on my memory of reading related Stack Overflow articles etc. If contributors feel strongly (and we don't have anything better to do) then maybe we can convince each other to update this section.

Trailing vs hanging braces
   Data
      Hanging closing brace is preferred, trailing commas always to help reduce churn in diffs
   Function, class, method args
      Inline until line-length, then style as per data
   Nesting
      Functions
         Short: group hanging close parentheses 
         Long: one closing parentheses per line

Single vs double quotes
   Single quotes are preferred; less strain on the hands, eyes

   Double quotes are only better so as to contain single quotes, but we want to contain doubles as often 

Line continuation
   Implicit parentheses continuation is preferred

British vs American spelling
   We should be consistent, it looks like we have American to British at approx 140 to 60 in the code. There's not enough occurrences that we couldn't be consistent one way or the other. It breaks my heart that British spelling could lose this one but I'm happy to 'z' things up for the sake of consistency. So I put forward British to be preferred. Either that strawman wins out, or I incite interest in ~bike-shedding~ guiding the direction of this crucial topic from others.

Dependency graph
----------------

These images are not very useful right now but the aim is to tweak the settings of one or more of them to be informative, and/or divide them up into smaller graphs.

To re-build them, run `fab build_docs:dep_graphs=true`. Note that the dot graph takes a lot of time.

.. figure:: ../../../../_static/deps-neato.png
   :alt: neato graph of dependencies
   :width: 100 pc

   :index:`Neato` graph of dependencies

.. figure:: ../../../../_static/deps-sfdp.png
   :alt: SFDP graph of dependencies
   :width: 100 pc

   :index:`SFDP` graph of dependencies

.. figure:: ../../../../_static/deps-dot.png
   :alt: Dot graph of dependencies
   :width: 100 pc

   :index:`Dot` graph of dependencies

Key management
--------------

Nitro key
^^^^^^^^^

Regular contributors are enouraged to take further steps to protect their key and the Nitro Key (Start) is recommended by the BitMessage project for this purpose.

Debian-quirks
~~~~~~~~~~~~~

Stretch makes use of the directory ~/.gnupg/private-keys-v1.d/ to store the private keys. This simplifies some steps of the Nitro Key instructions. See step 5 of Debian's subkeys_ wiki page

.. _subkeys: https://wiki.debian.org/Subkeys


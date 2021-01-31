User Agent
==========

Bitmessage user agents are a modified browser user agent with more structure
to aid parsers and provide some coherence. The user agent strings are arranged
in a stack with the most underlying software listed first.

Basic format::

   /Name:Version/Name:Version/.../

Example::

   /PyBitmessage:0.2.2/Corporate Mail System:0.8/
   /Surdo:5.64/surdo-qt:0.4/

The version numbers are not defined to any strict format, although this guide
recommends:

 * Version numbers in the form of Major.Minor.Revision (2.6.41)
 * Repository builds using a date in the format of YYYYMMDD (20110128)

For git repository builds, implementations are free to use the git commitish.
However the issue lies in that it is not immediately obvious without the
repository which version preceeds another. For this reason, we lightly
recommend dates in the format specified above, although this is by no means
a requirement.

Optional ``-r1``, ``-r2``, ... can be appended to user agent version numbers.
This is another light recommendation, but not a requirement. Implementations
are free to specify version numbers in whatever format needed insofar as it
does not include ``(``, ``)``, ``:`` or ``/`` to interfere with the user agent
syntax.

An optional comments field after the version number is also allowed. Comments
should be delimited by parenthesis ``(...)``. The contents of comments is
entirely implementation defined although this document recommends the use of
semi-colons ``;`` as a delimiter between pieces of information.

Example::

   /cBitmessage:0.2(iPad; U; CPU OS 3_2_1)/AndroidBuild:0.8/

Reserved symbols are therefore: ``/ : ( )``

They should not be misused beyond what is specified in this section.

``/``
   separates the code-stack
``:``
   specifies the implementation version of the particular stack
``( and )``
   delimits a comment which optionally separates data using ``;``

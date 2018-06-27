Documentation
=============

Sphinx is used to pull richly formatted comments out of code, merge them with hand-written documentation and render it
in HTML and other formats.

To build the docs, simply run `$ fab -H localhost build_docs` once you have set up Fabric.

Restructured Text (RsT) vs MarkDown (md)
----------------------------------------

There's much on the internet about this. Suffice to say RsT_ is preferred for Python documentation while md is preferred for web markup or for certain other languages.

.. _Rst: [http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html]` style is preferred, 

`md` files can also be incorporated by using mdinclude directives in the indices. They are translated to RsT before rendering to the various formats. Headers are translated as a hard-coded level `(H1: =, H2: -, H3: ^, H4: ~, H5: ", H6: #`.  This represents a small consideration for both styles. If markup is not translated to rst well enough, switch to rst.



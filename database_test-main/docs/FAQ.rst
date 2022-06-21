BPPRC FAQ
=========

This is a list of Frequently Asked Questions about Sphinx.  Feel free to
suggest new entries!

How do I...
-----------

... create PDF files without LaTeX?
   You can use `rst2pdf <http://rst2pdf.googlecode.com>`_ version 0.12 or greater
   which comes with built-in Sphinx integration.  See the :ref:`builders`
   section for details.

... get section numbers?
   They are automatic in LaTeX output; for HTML, give a ``:numbered:`` option to
   the :rst:dir:`toctree` directive where you want to start numbering.

... customize the look of the built HTML files?
   Use themes, see :doc:`theming`.

... add global substitutions or includes?
   Add them in the :confval:`rst_epilog` config value.

... display the whole TOC tree in the sidebar?
   Use the :data:`toctree` callable in a custom layout template, probably in the
   ``sidebartoc`` block.

... write my own extension?
   See the :ref:`extension tutorial <exttut>`.

... convert from my existing docs using MoinMoin markup?
   The easiest way is to convert to xhtml, then convert `xhtml to reST`_.  You'll
   still need to mark up classes and such, but the headings and code examples
   come through cleanly.

... create HTML slides from Sphinx documents?
   See the "Hieroglyph" package at http://github.com/nyergler/hieroglyph.

For many more extensions and other contributed stuff, see the sphinx-contrib_
repository.

.. _sphinx-contrib: https://bitbucket.org/birkenfeld/sphinx-contrib/

.. _usingwith:

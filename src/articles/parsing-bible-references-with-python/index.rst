:blogpost: true
:date: 2025-10-16
:author: Elias Prescott
:tags: bible

Parsing Bible References with Python
====================================

I like reading the bible and writing about it, but I don't like manually copying and pasting bible verses.
So, I write little parsers that can take a bible reference (e.g. "Genesis 1:1 (ESV)") and convert it into the referenced verses.

To make the parsing easy, I use `parsy`_ which is a lovely `parser combinator`_ library.
Here is how I do it:

.. _parsy: https://github.com/python-parsy/parsy
.. _parser combinator: https://en.wikipedia.org/wiki/Parser_combinator

.. note::

   This code is pulled directly from the source file that powers bible references on this blog,
   so it may change over time.

.. literalinclude:: ../../_ext/bible_ref_parser.py
   :language: python

Example usage:

>>> import bible_ref_parser
>>> bible_ref_parser.parse('Genesis 1:1 (CSB)')
BibleReference(book='Genesis', chapter=1, verse=1, version='CSB')

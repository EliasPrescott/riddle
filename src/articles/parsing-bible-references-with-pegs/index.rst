:blogpost: true
:date: 2026-01-07
:author: Elias Prescott
:tags: bible

Parsing Bible References with PEGs
==================================

I previously wrote about :doc:`/articles/parsing-bible-references-with-python/index`, but I wanted to document a simpler method.
One of my favorite Lisp(-like) languages is `Janet`_, and Janet has a "Parsing Expression Grammar" (PEG) module.
The short explanation is that PEGs are like Regexes on steroids.
You can find a more in-depth explanation in the `Janet docs`_.

.. _Janet: https://janet-lang.org/
.. _Janet docs: https://janet-lang.org/docs/peg.html

Without further ado, here is how I parse bible references in Janet:

.. code-block:: janet

   (def books
     '("Genesis" "Exodus" "Leviticus" "Numbers" "Deuteronomy"
       "Joshua" "Judges" "Ruth" "1 Samuel" "2 Samuel" "1 Kings"
       "2 Kings" "1 Chronicles" "2 Chronicles" "Ezra" "Nehemiah"
       "Esther" "Job" "Psalms" "Proverbs" "Ecclesiastes"
       "Song of Songs" "Isaiah" "Jeremiah" "Lamentations"
       "Ezekiel" "Daniel" "Hosea" "Joel" "Amos" "Obadiah" "Jonah"
       "Micah" "Nahum" "Habakkuk" "Zephaniah" "Haggai" "Zechariah"
       "Malachi" "Matthew" "Mark" "Luke" "John" "Acts" "Romans"
       "1 Corinthians" "2 Corinthians" "Galatians" "Ephesians"
       "Philippians" "Colossians" "1 Thessalonians"
       "2 Thessalonians" "1 Timothy" "2 Timothy" "Titus" "Philemon"
       "Hebrews" "James" "1 Peter" "2 Peter" "1 John" "2 John"
       "3 John" "Jude" "Revelation"))

   (def bible-ref
     ~{:book (<- (+ ,;books))
       :chapter (number :d+)
       :verse-single (number :d+)
       :verse-range (group (* (number :d+) "-" (number :d+)))
       :verse-section (* ":" (+ :verse-range :verse-single))
       :main (* :book :s :chapter (? :verse-section))})

   (peg/match bible-ref "Genesis 1")
   # => @["Genesis" 1]

   (peg/match bible-ref "Job 5:7")
   # => @["Job" 5 7]

   (peg/match bible-ref "Matthew 5:3-12")
   # => @["Matthew" 5 @[3 12]]

If you want to try out this bible parser quickly, you can run Janet using Nix, and then paste each block in succession into the REPL.

.. code-block:: bash

   $ nix run nixpkgs#janet

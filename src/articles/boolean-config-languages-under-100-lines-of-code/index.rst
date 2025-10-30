:blogpost: true
:date: 2025-10-30
:author: Elias Prescott

Boolean Config Languages in Under 100 Lines of Code
===================================================

I made `SchedLang`_ which is a config language for defining date scheduling patterns.
It provides various primitives for checking parts of a date (e.g. checking the month is January, or the day of the week is Sunday, etc...),
but it also provides boolean combinators for building larger patterns.

.. _SchedLang: https://github.com/EliasPrescott/schedlang

You can check specific dates against the patterns you define.

.. code-block:: bash

  > schedlang check "(And (Day 31) (Month Oct))" --date 2025-10-31
  true

Or you can generate a list of dates that match your pattern.

.. code-block:: bash

  > schedlang list "(And (Day 29) (Month Feb))" --years 20 --start 2025-01-01
  2028-02-29
  2032-02-29
  2036-02-29
  2040-02-29
  2044-02-29

I wrote it in `OCaml`_ and almost all the heavy lifting is done by the `Core`_ package.

.. _OCaml: https://ocaml.org/
.. _Core: https://ocaml.org/p/core/latest/doc/core/Core/index.html

As of writing this post, here is what the heart of SchedLang looks like:

.. code-block:: ocaml

  open Core

  module Property = struct
    type t =
      | Date of Date.t
      | Year of int
      | Month of Month.t
      | Day of int
      | DayOfWeek of Day_of_week.t
    [@@deriving sexp]

    let eval t d =
      match t with
      | Date x -> Date.equal d x
      | Year x -> Date.year d = x
      | Month x -> Month.equal (Date.month d) x
      | Day x -> Date.day d = x
      | DayOfWeek x -> Day_of_week.equal (Date.day_of_week d) x
  end

  type t = Property.t Blang.t
  [@@deriving sexp]

  let parse input : t = t_of_sexp (Sexp.of_string input)

  let eval rule d =
    Blang.eval rule (fun p -> Property.eval p d)

  let generate_possible_matches ?(years=1) (rule : t) ~(min : Date.t) =
    let dates = Date.dates_between ~min ~max:(Date.add_years min years) in
    List.filter ~f:(eval rule) dates

The ``[@@deriving sexp]`` lines provide all the parsing logic.
Sexp is short for s-expression and it allows you to represent arbitrary OCaml types as Lisp-style s-expressions.
Blang is short for boolean language and it allows you to define your own boolean languages where every expression evaluates to a bool.

The Core library makes defining new boolean config languages trivial.
Every time I added a new clause to the languages like ``DayOfWeek``, I didn't have to iterate or write any tests at all.
I just added the case to ``Property.t``, and then to ``Property.eval``, and I knew that it should work as long as the type checker was happy.

This is a contrived example because Core provides so much functionality, but it is still amazing just how easy it was to make this language.
If you were making a more complicated config language, getting the s-expression parsing or the boolean combinators for free would allow you to focus solely on implementing your domain-specific logic.
And having the full power of the OCaml type system means that it is often trivial to catch logic bugs at compile time.
Maybe you don't need a date pattern definition language, but you might need to define forwarding/block rules for an email client or WAF rules for an HTTP proxy.

There are all kinds of applications that could benefit from having a logical config language, and OCaml and the Core library make it easy to create those languages.

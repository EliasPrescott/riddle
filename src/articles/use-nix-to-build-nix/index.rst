:blogpost: true
:date: 2025-11-22
:author: Elias Prescott

.. meta::
   :description: Use Nix to Build Nix
   :property="og:url": https://australorp.dev/articles/use-nix-to-build-nix/index.html
   :property="og:type": website
   :property="og:title": Use Nix to Build Nix — australorp.dev
   :property="og:description": Building the latest version of the Nix C Bindings.
   :property="og:image": /_images/used-the-nix-to-build-the-nix.png

   :name="twitter:card": summary_large_image
   :property="twitter:domain": australorp.dev
   :property="twitter:url": https://australorp.dev/articles/use-nix-to-build-nix/index.html
   :name="twitter:title": Use Nix to Build Nix — australorp.dev
   :name="twitter:description": Building the latest version of the Nix C Bindings.
   :name="twitter:image": /_images/used-the-nix-to-build-the-nix.png

|

.. image:: used-the-nix-to-build-the-nix.png

|

Use Nix to Build Nix
====================

Imagine you were using `Nix's C Bindings`_ to prototype little programs that use Nix, but you really wanted to use ``nix_get_attr_byname_lazy`` which was only introduced in `3d777eb37f`_.
What would you do?
Well it turns out, you can just use Nix to build the latest version of the Nix bindings.

.. _3d777eb37f: https://github.com/NixOS/nix/commit/3d777eb37f42cb8b6cd88b6a7c6a846dcb8cbcff
.. _Nix's C Bindings: https://nix.dev/manual/nix/2.24/c-api

.. code-block:: nix

  {
    inputs = {
      nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
      nix-latest.url = "github:nixos/nix";
    };

    outputs = { self, nixpkgs, nix-latest }: let
      pkgs = nixpkgs.legacyPackages.aarch64-darwin;
      nix = nix-latest.packages.aarch64-darwin;
    in {
      devShells.aarch64-darwin.default = pkgs.mkShell {
        nativeBuildInputs = [
          nix.nix-expr-c
          nix.nix-store-c
          nix.nix-util-c
        ];
      };
    };
  }

``github:nixos/nix`` refers to the ``flake.nix`` file living in the root directory of https://github.com/nixos/nix.
It provides Nix's C bindings, and referencing it directly allows you to use the latest version of the C bindings, even if they haven't been released yet.

Using this technique, I was able to build a simple Nix repl using `Odin`_ and Nix's C bindings:

.. _Odin: https://odin-lang.org/

.. code-block:: bash

  $ nix develop

  $ odin run . -- "builtins.nixVersion"
  "2.33.0pre"

  $ odin run . -- "(import <nixpkgs> {}).superTuxKart.meta"
  {
    unsupported: a thunk
    longDescription: a string
    name: a thunk
    mainProgram: a string
    license: a thunk
    homepage: a string
    unfree: a thunk
    maintainers: a thunk
    available: a thunk
    broken: a thunk
    description: a string
    insecure: a thunk
    outputsToInstall: a thunk
    changelog: a thunk
    position: a thunk
    platforms: a thunk
  }

  $ odin run . -- "(import <nixpkgs> {}).superTuxKart.meta.longDescription"
  "SuperTuxKart is a Free 3D kart racing game, with many tracks,
  characters and items for you to try, similar in spirit to Mario
  Kart.
  "

If you want to try out this repl or get started with the Nix C bindings quickly, I posted all my code here: https://github.com/EliasPrescott/igloo.
Thanks for reading!

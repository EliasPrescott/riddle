:blogpost: true
:date: 2025-11-19
:author: Elias Prescott

Zig Development on the Edge with Nix
====================================

`Zig`_ has been undergoing some major changes in how it handles IO and async/await code recently, but not all of the changes have been officially released yet. I wanted to play around with the changes, but I didn't want to download and install Zig, and build the `Zig language server (ZLS)`_ from scratch manually. So, I am going to use `Nix`_ to do the legwork for me.

.. _Zig: https://ziglang.org/
.. _Zig language server (ZLS): https://github.com/zigtools/zls
.. _Nix: https://nixos.org/

Using Nix will have the added bonuses of reproducible builds and developer environments across time (if we want that), and it makes it easy to share development environments across different machines and operating systems.

.. code-block:: bash

  $ mkdir zig-learning
  $ cd zig-learning
  $ nix flake init

The ``nix flake init`` command just sets up a simple ``flake.nix`` file in the current directory.

We will be using https://github.com/mitchellh/zig-overlay to provide a build definition of Zig.

To figure out how I should use nix-overlay, I used ``nix repl`` to interactively explore it. ``:lf github:mitchellh/zig-overlay`` loads the specified flake into your current session so you can play around with it. If you wanted to load a flake in your current directory, you could run ``:lf .``

.. code-block:: bash

  $ nix repl
  Nix 2.31.2
  Type :? for help.
  nix-repl> :lf github:mitchellh/zig-overlay
  ...output omitted...

  nix-repl> packages.${builtins.currentSystem}
  {
    "0.10.0" = «derivation /nix/store/lhyrc59qyi81wd89dzh3jj1zh1z7xzcr-zig-0.10.0.drv»;
    "0.10.1" = «derivation /nix/store/6860nypdk6rbah0bbr5vf60p640719gp-zig-0.10.1.drv»;
    "0.11.0" = «derivation /nix/store/gv82n2nfagx1nzygy0l02fi9mbviaw98-zig-0.11.0.drv»;
    "0.12.0" = «derivation /nix/store/9cysq2frqb1bpnsn67vbqk3v3l19lbd0-zig-0.12.0.drv»;
    "0.12.1" = «derivation /nix/store/yswv7wr6dfzzh2fyqisz3kij4x6kj2sh-zig-0.12.1.drv»;
    "0.13.0" = «derivation /nix/store/pshsnf6h8di1kq4zqpm6xa34rldffmcv-zig-0.13.0.drv»;
    "0.14.0" = «derivation /nix/store/9gb2ndjd8ipm5yahgy167yjwrc2v3q45-zig-0.14.0.drv»;
    "0.14.1" = «derivation /nix/store/2kxjgpn629p9507vzhq0yb70mcskcbyl-zig-0.14.1.drv»;
    "0.15.1" = «derivation /nix/store/7ianhmcsmxx00hdl1a6qm7mfc6hwibqa-zig-0.15.1.drv»;
    "0.15.2" = «derivation /nix/store/3sf737cwjzgsxhk1z2rv4w900znx52f1-zig-0.15.2.drv»;
    "0.7.0" = «derivation /nix/store/5lrsflwrxc3d4xzbipr8yz000bqcwnl8-zig-0.7.0.drv»;
    "0.8.0" = «derivation /nix/store/69bz18i86wqn48w01c57hsn9mzp6nj4l-zig-0.8.0.drv»;
    "0.8.1" = «derivation /nix/store/7ij4pw69i6pj9s964j747mxl15sgnpn1-zig-0.8.1.drv»;
    "0.9.0" = «derivation /nix/store/0frwqxy14q6nw3940rsy8b8hszkar8nm-zig-0.9.0.drv»;
    "0.9.1" = «derivation /nix/store/5gdkaxxk3a6yv9rxhh6a72m3yj21shzg-zig-0.9.1.drv»;
    default = «repeated»;
    master = «derivation /nix/store/zxvs7yg0wzd35273nvws50xlcc8svk5w-zig-0.16.0-dev.1364+f0a3df98d.drv»;
    ...rest of output omitted for brevity...
  }

Every Zig version for the past few years is recorded in zig-overlay. But I want to use master. Now let's go back to `flake.nix` and add zig-overlay:

.. code-block:: nix

  {
    description = "Zig Development on the Edge with Nix";

    inputs = {
      nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
      # Added so we can use eachDefaultSystem
      flake-utils.url = "github:numtide/flake-utils";

      # Added zig-overlay as a flake input and set its nixpkgs to
      # follow our version of nixpkgs.
      zig-overlay.url = "github:mitchellh/zig-overlay";
      zig-overlay.inputs.nixpkgs.follows = "nixpkgs";
    };

    outputs = { self, nixpkgs, flake-utils, zig-overlay }:
    flake-utils.lib.eachDefaultSystem (system: {
      packages = {
        zig = zig-overlay.packages.${system}.master;
      };
    });
  }

To test that we did this right, let's try running Zig:

.. code-block:: bash

  $ nix run .#zig -- version
  0.16.0-dev.1364+f0a3df98d

The path ``.`` tells Nix to look for a flake in the current directory, and the ``#zig`` directs it to our Zig package that we just defined.

If you would rather play with our Zig executable interactively, you can use ``nix shell``:

.. code-block:: bash

  $ nix shell .#zig

  $ zig version
  0.16.0-dev.1364+f0a3df98d

  $ which zig
  /nix/store/4llr3sxjdm12yq8h2i8aizca0cx0jbsl-zig-0.16.0-dev.1364+f0a3df98d/bin/zig

Now that we have Zig working, let's add zls so I can get error messages and autocompletion in my editor.

Zls is available as a package within nixpkgs, but if we pull it from there, then (as far as I know) we are forced to use the latest stable release which is ``0.15``. To make sure zls works with the latest bleeding-edge version of Zig, let's build it directly using its flake:

.. code-block:: bash

  {
    description = "Zig Development on the Edge with Nix";

    inputs = {
      nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
      flake-utils.url = "github:numtide/flake-utils";

      zig-overlay.url = "github:mitchellh/zig-overlay";
      zig-overlay.inputs.nixpkgs.follows = "nixpkgs";

      # We added zls as a flake input, and we set it to use our version
      # of nixpkgs and our version of zig-overlay.
      zls-flake.url = "github:zigtools/zls";
      zls-flake.inputs.nixpkgs.follows = "nixpkgs";
      zls-flake.inputs.zig-overlay.follows = "zig-overlay";
    };

    outputs = { self, nixpkgs, flake-utils, zig-overlay, zls }:
    flake-utils.lib.eachDefaultSystem (system: {
      packages = {
        zig = zig-overlay.packages.${system}.master;
        zls = zls-flake.packages.${system}.zls;
      };
    });
  }

You could run ``nix shell .#zig .#zls``, but that's a lot of work to type each time. Instead, nix flakes provide a standard way of defining reproducible dev shells: ``nix develop``.

.. code-block:: nix

  {
    description = "Zig Development on the Edge with Nix";

    inputs = {
      nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
      flake-utils.url = "github:numtide/flake-utils";

      zig-overlay.url = "github:mitchellh/zig-overlay";
      zig-overlay.inputs.nixpkgs.follows = "nixpkgs";

      zls-flake.url = "github:zigtools/zls";
      zls-flake.inputs.nixpkgs.follows = "nixpkgs";
      zls-flake.inputs.zig-overlay.follows = "zig-overlay";
    };

    outputs = { self, nixpkgs, flake-utils, zig-overlay, zls-flake }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      # I moved zig and zls here so I can easily refer to them in
      # multiple places.
      zig = zig-overlay.packages.${system}.master;
      zls = zls-flake.packages.${system}.zls;
    in {
      # https://nix.dev/manual/nix/2.18/language/constructs#inheriting-attributes
      packages = {
        inherit zig zls;
      };

      # Here is our new dev shell definition.
      devShells.default = pkgs.mkShell {
        packages = [
          zig
          zls
        ];
      };
    });
  }

Now you can run ``nix develop`` and it will automatically create a new shell with zig and zls available to us.

.. code-block:: bash

  $ nix develop

  $ zig version
  0.16.0-dev.1364+f0a3df98d

  $ zls version
  0.16.0-dev

Now that we have our dev shell ready, I can close my editor, run ``nix develop``, reopen my editor so it can find zig and zls, and then I can run some zig code and play around with the new features.

.. code-block:: zig

  const std = @import("std");
  const Io = std.Io;
  const Allocator = std.mem.Allocator;
  const assert = std.debug.assert;

  fn doWork(io: Io) void {
      std.debug.print("working...\n", .{});
      io.sleep(.fromSeconds(1), .awake) catch {};
  }

  pub fn main() !void {
      var debug_alloc: std.heap.DebugAllocator(.{}) = .init;
      defer assert(debug_alloc.deinit() == .ok);
      const gpa = debug_alloc.allocator();

      var threaded: std.Io.Threaded = .init(gpa);
      defer threaded.deinit();
      const io = threaded.io();

      doWork(io);
  }

.. code-block:: bash

  $ zig run main.zig
  working...
  done!

See `Zig's New Async I/O`_ for more details on the new Zig features I am using here. I hope you enjoyed the post!

.. _Zig's New Async I/O: https://andrewkelley.me/post/zig-new-async-io-text-version.html

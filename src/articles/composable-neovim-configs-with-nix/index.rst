:blogpost: true
:date: 2025-10-28
:author: Elias Prescott

Composable NeoVim Configs with Nix
==================================

If you define your NeoVim config in Nix using `Nixvim`_, then you can compose it with other people's configs.
Here is a minimal Nix flake that shows how you can use my NeoVim config, while overriding the colorscheme to your own preference:

.. _Nixvim: https://github.com/nix-community/nixvim

.. code-block:: nix

  {
    description = "Using Eli's NeoVim config and overriding the colorscheme";

    inputs = {
      nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
      nixvim = {
        url = "github:nix-community/nixvim";
        inputs.nixpkgs.follows = "nixpkgs";
      };
      elis-stuff = {
        # hardcoding the ref to make this example more stable
        url = "github:eliasprescott/the-kitchen?ref=26e8fc1816cf87b71d586b49df9ca0aee0c140d2";
        inputs.nixpkgs.follows = "nixpkgs";
      };
    };

    outputs = { self, nixpkgs, nixvim, elis-stuff }:
      let
        # change this to whatever your local system is
        system = "aarch64-darwin";
        elis-neovim-config = elis-stuff.configs.${system}.neovim;
        ###
        ### Your overrides go below
        ###
        neovim-overrides = {
          colorscheme = "murphy";
        };
        # merging the remote config with neovim-overrides
        neovim-config = elis-neovim-config // neovim-overrides;
      in {
        packages.${system}.default = nixvim.legacyPackages.${system}.makeNixvim neovim-config;
      };
  }

If you would rather run my version of NeoVim directly, you can use ``nix run`` and a flake ref:

.. code-block:: bash

   nix run github:eliasprescott/the-kitchen#neovim

If you want to interactively explore my NeoVim config, use ``nix repl`` and ``:lf github:eliasprescott/the-kitchen``:

.. code-block:: bash

  > nix repl
  Nix 2.31.2
  Type :? for help.
  nix-repl> :lf github:eliasprescott/the-kitchen
  Added 13 variables.
  _type, configs, devShells, inputs, lastModified, lastModifiedDate, narHash, outPath, outputs, packages, rev, shortRev, sourceInfo

  nix-repl> configs.${builtins.currentSystem}.neovim
  {
    colorscheme = "gruvbox";
    extraConfigLuaPost = "vim.cmd [[\n  hi Normal guibg=none\n  hi NonText guibg=none\n  hi Normal ctermbg=none\n  hi NonText ctermbg=none\n  hi EndOfBuffer guibg=none\n]]\n";
    globals = { ... };
    keymaps = [ ... ];
    lsp = { ... };
    opts = { ... };
    plugins = { ... };
  }

From there you can explore each property individually, or you can prepend ``:p`` to the last command to recursively print the entire expression.

I am still not 100% sold on configuring NeoVim using Nix because it feels like an extra layer of indirection to have Nix expressions that generate the Lua config, but being able to explore and compose configuration in a structured manner is a genuinely interesting benefit.

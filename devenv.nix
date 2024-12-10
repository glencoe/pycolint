{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: {
  packages = [
    pkgs.git
    pkgs.antlr
    pkgs.tree-sitter
  ];

  languages.python = {
    enable = true;
    uv.enable = true;
    version = "3.13";
  };

  pre-commit.hooks = {
    shellcheck.enable = true;
    ruff.enable = true;
    mypy.enable = true;
    mypy.settings.binPath = "${config.env.DEVENV_STATE}/venv/bin/mypy";
    ripsecrets.enable = true;
    # vale.enable = true;
    yamlfmt.enable = true;
    actionlint.enable = true;
    alejandra.enable = true;
    check-added-large-files.enable = true;
    check-builtin-literals.enable = true;
    check-docstring-first.enable = true;
    check-json.enable = true;
    check-python.enable = true;
    check-shebang-scripts-are-executable.enable = true;
    check-symlinks.enable = true;
    check-toml.enable = true;
    check-vcs-permalinks.enable = true;
    # no-commit-to-branch.enable = true;
    pyright.enable = true;
    # reuse.enable = true;
  };
}

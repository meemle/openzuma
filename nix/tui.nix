# nix/tui.nix — Openzuma TUI (Ink/React) compiled with tsc and bundled
{ pkgs, openzumaNpmLib, ... }:
let
  src = ../ui-tui;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-RU4qSHgJPMyfRSEJDzkG4+MReDZDc6QbTD2wisa5QE0=";
  };

  npm = openzumaNpmLib.mkNpmPassthru { folder = "ui-tui"; attr = "tui"; pname = "openzuma-tui"; };

  packageJson = builtins.fromJSON (builtins.readFile (src + "/package.json"));
  version = packageJson.version;
in
pkgs.buildNpmPackage (npm // {
  pname = "openzuma-tui";
  inherit src npmDeps version;

  doCheck = false;

  installPhase = ''
    runHook preInstall

    mkdir -p $out/lib/openzuma-tui

    cp -r dist $out/lib/openzuma-tui/dist

    # runtime node_modules
    cp -r node_modules $out/lib/openzuma-tui/node_modules

    # @openzuma/ink is a file: dependency, we need to copy it in fr
    rm -f $out/lib/openzuma-tui/node_modules/@openzuma/ink
    cp -r packages/openzuma-ink $out/lib/openzuma-tui/node_modules/@openzuma/ink

    # package.json needed for "type": "module" resolution
    cp package.json $out/lib/openzuma-tui/

    runHook postInstall
  '';
})

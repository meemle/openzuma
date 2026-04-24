# nix/web.nix — Openzuma Web Dashboard (Vite/React) frontend build
{ pkgs, openzumaNpmLib, ... }:
let
  src = ../web;
  npmDeps = pkgs.fetchNpmDeps {
    inherit src;
    hash = "sha256-TS/vrCHbdvXkPcAPxImKzAd2pdDCrKlgYZkXBMQ+TEg=";
  };

  npm = openzumaNpmLib.mkNpmPassthru { folder = "web"; attr = "web"; pname = "openzuma-web"; };
in
pkgs.buildNpmPackage (npm // {
  pname = "openzuma-web";
  version = "0.0.0";
  inherit src npmDeps;

  doCheck = false;

  buildPhase = ''
    npx tsc -b
    npx vite build --outDir dist
  '';

  installPhase = ''
    runHook preInstall
    cp -r dist $out
    runHook postInstall
  '';
})

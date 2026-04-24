# nix/packages.nix — Openzuma Agent package built with uv2nix
{ inputs, ... }:
{
  perSystem =
    { pkgs, inputs', ... }:
    let
      openzumaVenv = pkgs.callPackage ./python.nix {
        inherit (inputs) uv2nix pyproject-nix pyproject-build-systems;
      };

      openzumaNpmLib = pkgs.callPackage ./lib.nix {
        npm-lockfile-fix = inputs'.npm-lockfile-fix.packages.default;
      };

      openzumaTui = pkgs.callPackage ./tui.nix {
        inherit openzumaNpmLib;
      };

      # Import bundled skills, excluding runtime caches
      bundledSkills = pkgs.lib.cleanSourceWith {
        src = ../skills;
        filter = path: _type: !(pkgs.lib.hasInfix "/index-cache/" path);
      };

      openzumaWeb = pkgs.callPackage ./web.nix {
        inherit openzumaNpmLib;
      };

      runtimeDeps = with pkgs; [
        nodejs_22
        ripgrep
        git
        openssh
        ffmpeg
        tirith
      ];

      runtimePath = pkgs.lib.makeBinPath runtimeDeps;

      # Lockfile hashes for dev shell stamps
      pyprojectHash = builtins.hashString "sha256" (builtins.readFile ../pyproject.toml);
      uvLockHash =
        if builtins.pathExists ../uv.lock then
          builtins.hashString "sha256" (builtins.readFile ../uv.lock)
        else
          "none";
    in
    {
      packages = {
        default = pkgs.stdenv.mkDerivation {
          pname = "openzuma-agent";
          version = (fromTOML (builtins.readFile ../pyproject.toml)).project.version;

          dontUnpack = true;
          dontBuild = true;
          nativeBuildInputs = [ pkgs.makeWrapper ];

          installPhase = ''
            runHook preInstall

            mkdir -p $out/share/openzuma-agent $out/bin
            cp -r ${bundledSkills} $out/share/openzuma-agent/skills
            cp -r ${openzumaWeb} $out/share/openzuma-agent/web_dist

            # copy pre-built TUI (same layout as dev: ui-tui/dist/ + node_modules/)
            mkdir -p $out/ui-tui
            cp -r ${openzumaTui}/lib/openzuma-tui/* $out/ui-tui/

            ${pkgs.lib.concatMapStringsSep "\n"
              (name: ''
                makeWrapper ${openzumaVenv}/bin/${name} $out/bin/${name} \
                  --suffix PATH : "${runtimePath}" \
                  --set OPENZUMA_BUNDLED_SKILLS $out/share/openzuma-agent/skills \
                  --set OPENZUMA_WEB_DIST $out/share/openzuma-agent/web_dist \
                  --set OPENZUMA_TUI_DIR $out/ui-tui \
                  --set OPENZUMA_PYTHON ${openzumaVenv}/bin/python3 \
                  --set OPENZUMA_NODE ${pkgs.nodejs_22}/bin/node
              '')
              [
                "openzuma"
                "openzuma-agent"
                "openzuma-acp"
              ]
            }

            runHook postInstall
          '';

          passthru.devShellHook = ''
            STAMP=".nix-stamps/openzuma-agent"
            STAMP_VALUE="${pyprojectHash}:${uvLockHash}"
            if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$STAMP_VALUE" ]; then
              echo "openzuma-agent: installing Python dependencies..."
              uv venv .venv --python ${pkgs.python312}/bin/python3 2>/dev/null || true
              source .venv/bin/activate
              uv pip install -e ".[all]"
              [ -d mini-swe-agent ] && uv pip install -e ./mini-swe-agent 2>/dev/null || true
              [ -d tinker-atropos ] && uv pip install -e ./tinker-atropos 2>/dev/null || true
              mkdir -p .nix-stamps
              echo "$STAMP_VALUE" > "$STAMP"
            else
              source .venv/bin/activate
              export OPENZUMA_PYTHON=${openzumaVenv}/bin/python3
            fi
          '';

          meta = with pkgs.lib; {
            description = "AI agent with advanced tool-calling capabilities";
            homepage = "https://github.com/meemle/openzuma";
            mainProgram = "openzuma";
            license = licenses.mit;
            platforms = platforms.unix;
          };
        };

        tui = openzumaTui;
        web = openzumaWeb;

        fix-lockfiles = openzumaNpmLib.mkFixLockfiles {
          packages = [ openzumaTui openzumaWeb ];
        };
      };
    };
}

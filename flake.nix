{
  description = "dev shell with cuda out of the box";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nix-gl-host.url = "github:numtide/nix-gl-host";
  };

  outputs =
    {
      self,
      nixpkgs,
      nix-gl-host,
    }:
    let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        config.allowUnfree = true;
        config.cudaSupport = true;
      };
    in
    {
      devShells.x86_64-linux.default =
        with pkgs;
        mkShell {

          packages = [
            nix-gl-host.defaultPackage.x86_64-linux
            pkgs.qt6.qtbase
            pkgs.qt6.qtwayland
            pkgs.python312Packages.pyqt6
          ];

          shellHook = ''
            export SSL_CERT_FILE=/etc/ssl/certs/ca-bundle.crt

            # Get host GPU driver path
            NIXGL_PATH=$(nixglhost -p)

            # Build additional library paths
            EXTRA_LIBS="${
              pkgs.lib.makeLibraryPath [
                pkgs.libx11
                pkgs.libGL
                pkgs.wayland
                pkgs.libxkbcommon
                pkgs.qt6.qtbase
                pkgs.qt6.qtwayland
              ]
            }"

            # Expose nix-provided PyQt6 to the uv venv's Python
            NIX_PYQT6_PATH="${pkgs.python312Packages.pyqt6}/${pkgs.python312.sitePackages}"
            export PYTHONPATH="$NIX_PYQT6_PATH:''${PYTHONPATH:-}"

            # Qt6 plugin path so PyQt6 can find platform plugins
            export QT_PLUGIN_PATH="${pkgs.qt6.qtbase}/lib/qt-6/plugins"
            export QT_QPA_PLATFORM="''${QT_QPA_PLATFORM:-wayland}"

            # Combine everything (append, don't overwrite!)
            export LD_LIBRARY_PATH="$NIXGL_PATH:$EXTRA_LIBS:$LD_LIBRARY_PATH"
          '';
        };
    };
}

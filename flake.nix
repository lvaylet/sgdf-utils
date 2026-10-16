{
  description = "Environnement de développement éphémère Python 3 pour l'automatisation des tâches du groupe scout SGDF de La Rochelle";

  inputs = {
    # Utilise l'entrée nixpkgs du registre Nix (résolue localement sur NixOS ou via nixpkgs-unstable)
    nixpkgs.url = "flake:nixpkgs";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forEachSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      devShells = forEachSystem ({ pkgs }:
        let
          pythonEnv = pkgs.python3.withPackages (pythonPackages: with pythonPackages; [
            pandas
            beautifulsoup4
            lxml
            xlrd
            openpyxl
            pytest
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [
              pythonEnv
              pkgs.ruff
            ];

            shellHook = ''
              echo "=================================================================="
              echo " Environnement éphémère SGDF La Rochelle actif (option : flake.nix)"
              echo " Interpréteur : $(python3 --version)"
              echo " Outils prêts : pandas, beautifulsoup4, lxml, xlrd, openpyxl, pytest, ruff"
              echo "=================================================================="
            '';
          };
        }
      );
    };
}

{
  description = "Environnement de développement éphémère Python 3 pour l'automatisation des tâches du groupe scout SGDF de La Rochelle";

  inputs = {
    # Utilise l'entrée nixpkgs du registre Nix (résolue localement sur NixOS ou via nixpkgs-unstable)
    nixpkgs.url = "flake:nixpkgs";
  };

  outputs = { self, nixpkgs }:
    let
      systemesSupportes = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      pourChaqueSysteme = f: nixpkgs.lib.genAttrs systemesSupportes (systeme: f {
        pkgs = import nixpkgs { inherit systeme; system = systeme; };
      });
    in
    {
      devShells = pourChaqueSysteme ({ pkgs }:
        let
          environnementPython = pkgs.python3.withPackages (paquetsPython: with paquetsPython; [
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
              environnementPython
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

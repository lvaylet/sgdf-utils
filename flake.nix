{
  description = "Environnement de développement éphémère Python 3, paquet applicatif et module NixOS pour l'automatisation SGDF de La Rochelle";

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
        inherit system;
        pkgs = import nixpkgs { inherit system; };
      });

      # Module NixOS déclaratif pour déployer le service sgdf-utils sur le homelab
      sgdfNixOSModule = { config, lib, pkgs, ... }:
        let
          cfg = config.services.sgdf-utils;
        in
        {
          options.services.sgdf-utils = {
            enable = lib.mkEnableOption "le service API HTTP REST SGDF Contacts Parents (sgdf-utils)";

            package = lib.mkOption {
              type = lib.types.package;
              default = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
              defaultText = lib.literalExpression "self.packages.\${pkgs.stdenv.hostPlatform.system}.default";
              description = "Paquet sgdf-contacts fournissant l'exécutable sgdf-api.";
            };

            host = lib.mkOption {
              type = lib.types.str;
              default = "127.0.0.1";
              description = "Adresse IP d'écoute du serveur HTTP FastAPI/Uvicorn.";
            };

            port = lib.mkOption {
              type = lib.types.port;
              default = 8000;
              description = "Port TCP d'écoute du serveur HTTP FastAPI/Uvicorn.";
            };

            dataDir = lib.mkOption {
              type = lib.types.str;
              default = "/var/lib/sgdf-utils";
              description = "Répertoire persistant contenant la base SQLite sgdf.sqlite3.";
            };

            environmentFile = lib.mkOption {
              type = lib.types.nullOr lib.types.path;
              default = null;
              example = "/run/secrets/sgdf-utils.env";
              description = "Chemin vers le fichier de secrets géré par sops-nix ou agenix contenant SGDF_API_KEY.";
            };
          };

          config = lib.mkIf cfg.enable {
            systemd.services.sgdf-utils = {
              description = "Service API HTTP REST SGDF Contacts Parents (sgdf-utils)";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];

              environment = {
                SGDF_HOST = cfg.host;
                SGDF_PORT = toString cfg.port;
                SGDF_DATABASE_URL = "sqlite:///${cfg.dataDir}/sgdf.sqlite3";
              };

              serviceConfig = {
                ExecStart = "${cfg.package}/bin/sgdf-api";
                WorkingDirectory = cfg.dataDir;
                DynamicUser = true;
                StateDirectory = "sgdf-utils";
                ProtectSystem = "strict";
                ProtectHome = true;
                PrivateTmp = true;
                NoNewPrivileges = true;
                Restart = "on-failure";
                RestartSec = 5;
              }
              // lib.optionalAttrs (cfg.environmentFile != null) {
                EnvironmentFile = cfg.environmentFile;
              }
              // lib.optionalAttrs (cfg.dataDir != "/var/lib/sgdf-utils") {
                ReadWritePaths = [ cfg.dataDir ];
              };
            };
          };
        };
    in
    {
      packages = forEachSystem ({ pkgs, ... }:
        let
          sgdfPackage = pkgs.python3Packages.buildPythonApplication {
            pname = "sgdf-contacts";
            version = "1.0.0";
            pyproject = true;
            src = nixpkgs.lib.cleanSource ./.;

            build-system = with pkgs.python3Packages; [
              setuptools
            ];

            dependencies = with pkgs.python3Packages; [
              pandas
              beautifulsoup4
              lxml
              xlrd
              openpyxl
              sqlmodel
              sqlalchemy
              fastapi
              uvicorn
              python-multipart
              httpx
            ];

            nativeCheckInputs = [
              pkgs.python3Packages.pytestCheckHook
              pkgs.ruff
            ];

            meta = {
              description = "Outils CLI et API HTTP REST de gestion des contacts parents SGDF La Rochelle";
              mainProgram = "sgdf-api";
            };
          };
        in
        {
          default = sgdfPackage;
          sgdf-contacts = sgdfPackage;
        }
        // nixpkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          oci-image = pkgs.dockerTools.buildLayeredImage {
            name = "sgdf-utils";
            tag = "latest";
            contents = [
              sgdfPackage
              pkgs.cacert
            ];
            config = {
              Cmd = [ "${sgdfPackage}/bin/sgdf-api" ];
              Env = [
                "SGDF_HOST=0.0.0.0"
                "SGDF_PORT=8000"
                "SGDF_DATABASE_URL=sqlite:////data/sgdf.sqlite3"
              ];
              ExposedPorts = {
                "8000/tcp" = { };
              };
              Volumes = {
                "/data" = { };
              };
              WorkingDir = "/data";
            };
          };
        }
      );

      apps = forEachSystem ({ pkgs, system }:
        let
          pkg = self.packages.${system}.default;
        in
        {
          default = {
            type = "app";
            program = "${pkg}/bin/sgdf-api";
            meta.description = "Lance le serveur API HTTP REST FastAPI SGDF Contacts Parents";
          };
          sgdf-api = {
            type = "app";
            program = "${pkg}/bin/sgdf-api";
            meta.description = "Lance le serveur API HTTP REST FastAPI SGDF Contacts Parents";
          };
          sgdf-extract = {
            type = "app";
            program = "${pkg}/bin/sgdf-extract";
            meta.description = "Extrait et regroupe les contacts parents depuis ExportIndividus.xls";
          };
          sgdf-vcf = {
            type = "app";
            program = "${pkg}/bin/sgdf-vcf";
            meta.description = "Génère le fichier ContactParents.vcf depuis ContactsParents.xlsx";
          };
        }
      );

      nixosModules = {
        default = sgdfNixOSModule;
        sgdf-utils = sgdfNixOSModule;
      };

      checks = forEachSystem ({ pkgs, system }:
        let
          baseChecks = {
            package = self.packages.${system}.default;
          };
          linuxChecks = nixpkgs.lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux (
            let
              evalSystem = nixpkgs.lib.nixosSystem {
                inherit system;
                modules = [
                  self.nixosModules.default
                  {
                    boot.isContainer = true;
                    system.stateVersion = "25.05";
                    services.sgdf-utils = {
                      enable = true;
                      environmentFile = "/run/secrets/sgdf-utils.env";
                    };
                  }
                ];
              };
              svc = evalSystem.config.systemd.services.sgdf-utils;
              sc = svc.serviceConfig;
            in
            assert svc.environment.SGDF_HOST == "127.0.0.1";
            assert svc.environment.SGDF_PORT == "8000";
            assert svc.environment.SGDF_DATABASE_URL == "sqlite:////var/lib/sgdf-utils/sgdf.sqlite3";
            assert sc.DynamicUser == true;
            assert sc.StateDirectory == "sgdf-utils";
            assert sc.ProtectSystem == "strict";
            assert sc.ProtectHome == true;
            assert sc.PrivateTmp == true;
            assert sc.NoNewPrivileges == true;
            assert toString sc.EnvironmentFile == "/run/secrets/sgdf-utils.env";
            {
              oci-image = self.packages.${system}.oci-image;
              nixos-module = pkgs.runCommand "check-sgdf-utils-nixos-module" { } ''
                echo "ExecStart=${sc.ExecStart}" > "$out"
              '';
            }
          );
        in
        baseChecks // linuxChecks
      );

      devShells = forEachSystem ({ pkgs, ... }:
        let
          pythonEnv = pkgs.python3.withPackages (pythonPackages: with pythonPackages; [
            pandas
            beautifulsoup4
            lxml
            xlrd
            openpyxl
            sqlmodel
            sqlalchemy
            fastapi
            uvicorn
            python-multipart
            httpx
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
              echo " Outils prêts : pandas, beautifulsoup4, lxml, xlrd, openpyxl, sqlmodel, sqlalchemy, fastapi, uvicorn, python-multipart, httpx, pytest, ruff"
              echo "=================================================================="
            '';
          };
        }
      );
    };
}

{
  description = "A fully-featured cross-platform XML editor with XPath, validation, and schema support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    let
      # NixOS VM test (system-specific, not per-platform)
      nixosTest = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          ({ pkgs, ... }: {
            # Set state version to avoid warning
            system.stateVersion = "24.11";
            
            # Minimal NixOS configuration for testing
            boot.loader.systemd-boot.enable = true;
            fileSystems."/" = {
              device = "/dev/vda";
              fsType = "ext4";
            };
            
            # Install xml-editor GUI
            environment.systemPackages = [
              (self.packages.x86_64-linux.gui)
            ];
            
            # Enable X11 for GUI testing
            services.xserver = {
              enable = true;
              displayManager.lightdm.enable = true;
              desktopManager.xfce.enable = true;
            };
            
            # Test user
            users.users.testuser = {
              isNormalUser = true;
              password = "test";
              extraGroups = [ "wheel" ];
            };
            
            # Disable unnecessary services for faster testing
            systemd.services.systemd-udevd.serviceConfig.PrivateMounts = nixpkgs.lib.mkForce false;
          })
        ];
      };
      
      # VM test derivation
      vmTest = pkgs: pkgs.testers.runNixOSTest {
        name = "xml-editor-vm-test";
        
        nodes.machine = { config, pkgs, ... }: {
          imports = [ ];
          
          # Set state version to avoid warning
          system.stateVersion = "24.11";
          
          # Install xml-editor GUI
          environment.systemPackages = [
            self.packages.x86_64-linux.gui
          ];
          
          # Enable X11 for GUI testing
          services.xserver = {
            enable = true;
            displayManager.lightdm.enable = true;
          };
          
          # Enable automatic login to X session
          services.displayManager = {
            defaultSession = "none+icewm";
            autoLogin = {
              enable = true;
              user = "testuser";
            };
          };
          
          services.xserver.windowManager.icewm.enable = true;
          
          # Test user
          users.users.testuser = {
            isNormalUser = true;
            password = "test";
          };
        };
        
        testScript = ''
          start_all()
          machine.wait_for_unit("multi-user.target")
          
          # Wait for X server to be ready
          machine.wait_for_x()
          
          # Check that xml-editor command exists
          machine.succeed("which xml-editor")
          
          # Check that xml-editor-cli command exists and works
          machine.succeed("which xml-editor-cli")
          
          # Verify CLI version works (non-GUI)
          # This test already validates that the Python module is accessible
          machine.succeed("xml-editor-cli --help")
          
          # Test that the GUI application binary is executable
          machine.succeed("test -x $(which xml-editor)")
          
          # Launch the GUI application in the background and verify it runs for 10 seconds
          print("Launching GUI application...")
          machine.succeed("su - testuser -c 'DISPLAY=:0 xml-editor &' >&2")
          
          # Give the application a moment to start
          import time
          time.sleep(2)
          
          # Check that the process is running
          machine.succeed("pgrep -f xml-editor")
          print("GUI application started successfully")
          
          # Wait 10 seconds while checking the process is still alive
          for i in range(8):
              time.sleep(1)
              machine.succeed("pgrep -f xml-editor")
          
          print("GUI application has been running for 10+ seconds without crashing")
          
          # Clean up - kill the application (use execute instead of succeed to ignore exit code)
          machine.execute("pkill -f xml-editor")
          
          print("XML Editor VM test passed!")
        '';
      };
    in
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Common Python package build
        pythonPackage = { pname, gui ? false }:
          pkgs.python3Packages.buildPythonApplication {
            inherit pname;
            version = "1.0.0";
            
            src = ./.;
            
            format = "pyproject";

            extras = if gui then [ "gui" ] else [];

            pythonRelaxDeps = if gui then [ "PyQt6-QScintilla" ] else [];
            
            nativeBuildInputs = with pkgs.python3Packages; [
              setuptools
              wheel
            ] ++ pkgs.lib.optionals gui [
              pkgs.qt6.wrapQtAppsHook
            ];
            
            propagatedBuildInputs = with pkgs.python3Packages; [
              lxml
              pygments
            ] ++ pkgs.lib.optionals gui [
              pyqt6
              pyqt6-sip
              qscintilla-qt6
              pkgs.qt6.qtbase
              pkgs.qt6.qtwayland
            ];
            
            # Don't check for PyQt6-QScintilla in build phase as it's provided by system
            doCheck = false;
            
            meta = with pkgs.lib; {
              description = "A fully-featured cross-platform XML editor with XPath, validation, and schema support";
              homepage = "https://github.com/profiluefter/xml-editor";
              license = licenses.mit;
              maintainers = [ ];
              platforms = platforms.unix;
              mainProgram = if gui then "xml-editor" else "xml-editor-cli";
            };
          };
        
        # GUI package
        xml-editor-gui = pythonPackage {
          pname = "xml-editor-gui";
          gui = true;
        };
        
        # CLI package (same as GUI but different package name)
        xml-editor-cli = pythonPackage {
          pname = "xml-editor-cli";
          gui = false;
        };
        
        # Test script
        testScript = pkgs.writeShellScriptBin "test-xml-editor" ''
          set -e
          echo "Testing XML Editor installation..."
          
          # Test CLI version
          echo "Testing CLI package..."
          if ! command -v xml-editor-cli &> /dev/null; then
            echo "ERROR: xml-editor-cli command not found"
            exit 1
          fi
          echo "✓ xml-editor-cli command found"
          
          # Test Python module import
          echo "Testing Python module import..."
          ${pkgs.python3}/bin/python3 -c "import xmleditor; print('✓ xmleditor module imported successfully')" || {
            echo "ERROR: Failed to import xmleditor module"
            exit 1
          }
          
          # Test XML utilities
          echo "Testing XML utilities..."
          ${pkgs.python3}/bin/python3 -c "
from xmleditor.xml_utils import XMLUtilities
xml = '<?xml version=\"1.0\"?><root><child>test</child></root>'
is_valid, msg = XMLUtilities.validate_xml(xml)
assert is_valid, 'XML validation failed'
print('✓ XML validation works')
" || {
            echo "ERROR: XML utilities test failed"
            exit 1
          }
          
          # Test XPath
          echo "Testing XPath functionality..."
          ${pkgs.python3}/bin/python3 -c "
from xmleditor.xml_utils import XMLUtilities
xml = '<?xml version=\"1.0\"?><root><child>test</child></root>'
results = XMLUtilities.xpath_query(xml, '//child/text()')
assert len(results) == 1 and results[0] == 'test', 'XPath query failed'
print('✓ XPath functionality works')
" || {
            echo "ERROR: XPath test failed"
            exit 1
          }
          
          # Test formatting
          echo "Testing XML formatting..."
          ${pkgs.python3}/bin/python3 -c "
from xmleditor.xml_utils import XMLUtilities
xml = '<root><child>test</child></root>'
formatted = XMLUtilities.format_xml(xml)
assert '<child>' in formatted, 'XML formatting failed'
print('✓ XML formatting works')
" || {
            echo "ERROR: XML formatting test failed"
            exit 1
          }
          
          echo ""
          echo "================================================"
          echo "All tests passed! ✓"
          echo "================================================"
        '';
        
      in
      {
        packages = {
          default = xml-editor-gui;
          gui = xml-editor-gui;
          cli = xml-editor-cli;
          inherit xml-editor-gui xml-editor-cli;
        };
        
        apps = {
          default = {
            type = "app";
            program = "${xml-editor-gui}/bin/xml-editor";
          };
          gui = {
            type = "app";
            program = "${xml-editor-gui}/bin/xml-editor";
          };
          cli = {
            type = "app";
            program = "${xml-editor-cli}/bin/xml-editor-cli";
          };
          test = {
            type = "app";
            program = "${testScript}/bin/test-xml-editor";
          };
        };
        
        checks = {
          # Basic build check
          build-gui = xml-editor-gui;
          build-cli = xml-editor-cli;
          
          # Run tests
          functionality = pkgs.runCommand "xml-editor-functionality-test" {
            buildInputs = [ xml-editor-cli testScript ];
          } ''
            ${testScript}/bin/test-xml-editor
            touch $out
          '';
          
          # NixOS VM test (only on x86_64-linux)
          vm-test = if system == "x86_64-linux" 
            then vmTest pkgs
            else pkgs.runCommand "vm-test-skipped" {} ''
              echo "VM test skipped on ${system} (only runs on x86_64-linux)" > $out
            '';
        };
        
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pyqt6
            python3Packages.lxml
            python3Packages.pygments
            python3Packages.setuptools
            python3Packages.wheel
            qt6.qtbase
            qt6.qtwayland
          ];
          
          shellHook = ''
            echo "XML Editor development environment"
            echo "Run 'python -m xmleditor.main' to start the application"
            echo "Run 'python test_functionality.py' to run tests"
          '';
        };
      }
    ) // {
      # Add system-specific NixOS test configuration
      nixosConfigurations.test-vm = nixosTest;
    };
}

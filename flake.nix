{
  description = "A fully-featured cross-platform XML editor with XPath, validation, and schema support";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
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
            
            nativeBuildInputs = with pkgs.python3Packages; [
              setuptools
              wheel
            ];
            
            propagatedBuildInputs = with pkgs.python3Packages; [
              pyqt6
              pyqt6-sip
              lxml
              pygments
            ] ++ pkgs.lib.optionals gui [
              pkgs.qt6.qtbase
              pkgs.qt6.qtwayland
            ];
            
            buildInputs = pkgs.lib.optionals gui [
              pkgs.libsForQt5.qscintilla
              pkgs.qt6.qtbase
            ];
            
            # Don't check for PyQt6-QScintilla in build phase as it's provided by system
            doCheck = false;
            
            postInstall = pkgs.lib.optionalString gui ''
              # Wrap GUI application with Qt environment
              wrapProgram $out/bin/xml-editor \
                --prefix QT_PLUGIN_PATH : ${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix} \
                --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.qt6.qtbase ]}
            '';
            
            meta = with pkgs.lib; {
              description = "A fully-featured cross-platform XML editor with XPath, validation, and schema support";
              homepage = "https://github.com/profiluefter/xml-editor";
              license = licenses.mit;
              maintainers = [ ];
              platforms = platforms.unix;
              mainProgram = "xml-editor";
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
          if ! command -v xml-editor &> /dev/null; then
            echo "ERROR: xml-editor command not found"
            exit 1
          fi
          echo "✓ xml-editor command found"
          
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
            program = "${xml-editor-cli}/bin/xml-editor";
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
    );
}

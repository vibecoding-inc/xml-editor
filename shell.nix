{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pyqt6
    python3Packages.pyqt6-sip
    python3Packages.lxml
    python3Packages.pygments
    python3Packages.saxonche
    python3Packages.setuptools
    python3Packages.wheel
    python3Packages.build
    qt6.qtbase
    qt6.qtwayland
  ];
  
  shellHook = ''
    echo "=========================================="
    echo "XML Editor Development Environment"
    echo "=========================================="
    echo ""
    echo "Available commands:"
    echo "  python -m xmleditor.main     - Run the application"
    echo "  python test_functionality.py - Run tests"
    echo "  python -m build              - Build distribution packages"
    echo ""
    echo "To install in development mode:"
    echo "  pip install -e ."
    echo ""
  '';
}

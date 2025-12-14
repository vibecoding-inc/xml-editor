{ pkgs ? import <nixpkgs> { } }:

let
  saxonchePkg = pkgs.python3Packages.buildPythonPackage rec {
    pname = "saxonche";
    version = "12.9.0";
    format = "wheel";

    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/2f/f5/136f27f36d2d301d1f60b90e47567f8d85763c9d71073c1c32f33828d9d7/saxonche-12.9.0-cp312-cp312-manylinux_2_24_x86_64.whl";
      sha256 = "490f30e9486750f6a066de2b467114dfd6e14d23c8ce645cad64e663f580490a";
    };

    nativeBuildInputs = [
      pkgs.unzip
      pkgs.autoPatchelfHook
    ];
    buildInputs = [ pkgs.zlib ];

    doCheck = false;
  };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pyqt6
    python3Packages.pyqt6-sip
    python3Packages.lxml
    python3Packages.pygments
    saxonchePkg
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

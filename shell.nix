{ pkgs ? import <nixpkgs> { } }:

let
  saxonchePkg = pkgs.python3Packages.buildPythonPackage rec {
    pname = "saxonche";
    version = "12.9.0";
    format = "wheel";

    src = pkgs.python3Packages.fetchPypi {
      inherit pname version;
      format = "wheel";
      wheel = "saxonche-12.9.0-cp313-cp313-manylinux_2_24_x86_64.whl";
      sha256 = "b7d295ddeae3e7c355cf53035ec47a1db301a8b9bc917636f893b56a31a48187";
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

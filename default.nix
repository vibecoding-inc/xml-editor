{ pkgs ? import <nixpkgs> { }
, lib ? pkgs.lib
, python3 ? pkgs.python3
, buildPythonApplication ? pkgs.python3Packages.buildPythonApplication
, gui ? true
}:

buildPythonApplication rec {
  pname = if gui then "xml-editor-gui" else "xml-editor-cli";
  version = "1.0.0";
  
  src = ./.;
  
  format = "pyproject";
  
  nativeBuildInputs = with python3.pkgs; [
    setuptools
    wheel
  ];
  
  propagatedBuildInputs = with python3.pkgs; [
    pyqt6
    pyqt6-sip
    lxml
    pygments
    openai
  ] ++ lib.optionals gui [
    pkgs.qt6.qtbase
    pkgs.qt6.qtwayland
  ];
  
  buildInputs = lib.optionals gui [
    pkgs.libsForQt5.qscintilla
    pkgs.qt6.qtbase
  ];
  
  # Don't check for PyQt6-QScintilla in build phase as it's provided by system
  doCheck = false;
  
  postInstall = lib.optionalString gui ''
    # Wrap GUI application with Qt environment
    wrapProgram $out/bin/xml-editor \
      --prefix QT_PLUGIN_PATH : ${pkgs.qt6.qtbase}/${pkgs.qt6.qtbase.qtPluginPrefix} \
      --prefix PATH : ${lib.makeBinPath [ pkgs.qt6.qtbase ]}
  '';
  
  meta = with lib; {
    description = "A fully-featured cross-platform XML editor with XPath, validation, and schema support";
    homepage = "https://github.com/profiluefter/xml-editor";
    license = licenses.mit;
    maintainers = [ ];
    platforms = platforms.unix;
    mainProgram = "xml-editor";
  };
}

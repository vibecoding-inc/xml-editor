# Nix Packaging for XML Editor

This project includes comprehensive Nix packaging for both GUI and CLI variants.

## Quick Start

### Using Nix Flakes (Recommended)

#### Run the GUI application directly:
```bash
nix run github:profiluefter/xml-editor
```

#### Run the CLI variant:
```bash
nix run github:profiluefter/xml-editor#cli
```

#### Install the GUI application:
```bash
nix profile install github:profiluefter/xml-editor
```

#### Install the CLI variant:
```bash
nix profile install github:profiluefter/xml-editor#cli
```

### Using Traditional Nix

#### Build the GUI package:
```bash
nix-build -A gui
```

#### Build the CLI package:
```bash
nix-build -A cli default.nix --arg gui false
```

#### Install:
```bash
nix-env -f default.nix -i
```

## Available Packages

### GUI Package (`xml-editor-gui`)
The full-featured GUI application with Qt interface:
- Includes all PyQt6 dependencies
- Qt6 environment properly configured
- Syntax highlighting with QScintilla
- Visual tree view and dialogs

### CLI Package (`xml-editor-cli`)
Lightweight CLI variant (same entry point, minimal dependencies):
- Core XML processing functionality
- XPath queries
- XML validation
- XSLT transformations
- No GUI dependencies (can run headless)

## Development

### Enter development shell with Nix Flakes:
```bash
nix develop
```

### Enter development shell with traditional Nix:
```bash
nix-shell
```

This provides:
- Python 3 with all dependencies
- PyQt6 and Qt6 libraries
- Build tools (setuptools, wheel)
- Development environment ready for testing

### Run in development:
```bash
nix develop
python -m xmleditor.main
```

## Testing

### Run all checks:
```bash
nix flake check
```

This runs:
1. Build check for GUI package
2. Build check for CLI package
3. Functionality tests (import, validation, XPath, formatting)

### Run specific tests:
```bash
# Run the test app
nix run .#test

# Or check specific functionality
nix build .#checks.x86_64-linux.functionality
```

### Manual testing:
```bash
nix develop
python test_functionality.py
```

## Flake Outputs

The flake provides these outputs:

### Packages
- `packages.default` - GUI application (default)
- `packages.gui` - GUI application
- `packages.cli` - CLI variant
- `packages.xml-editor-gui` - GUI application
- `packages.xml-editor-cli` - CLI variant

### Apps
- `apps.default` - Run GUI application
- `apps.gui` - Run GUI application
- `apps.cli` - Run CLI variant
- `apps.test` - Run test suite

### Checks
- `checks.build-gui` - Verify GUI builds
- `checks.build-cli` - Verify CLI builds
- `checks.functionality` - Run functionality tests

### Development Shell
- `devShells.default` - Development environment with all dependencies

## Examples

### Build and test everything:
```bash
# Build both packages
nix build .#gui
nix build .#cli

# Run tests
nix run .#test

# Run flake checks
nix flake check
```

### Use in another Nix project:
```nix
{
  inputs = {
    xml-editor.url = "github:profiluefter/xml-editor";
  };
  
  outputs = { self, nixpkgs, xml-editor }: {
    # Use the package
    packages.x86_64-linux.myapp = pkgs.mkShell {
      buildInputs = [
        xml-editor.packages.x86_64-linux.gui
      ];
    };
  };
}
```

### Add to NixOS configuration:
```nix
{ config, pkgs, ... }:

let
  xml-editor = (import (fetchTarball "https://github.com/profiluefter/xml-editor/archive/main.tar.gz") {
    inherit pkgs;
  });
in {
  environment.systemPackages = [
    xml-editor
  ];
}
```

### Add to home-manager:
```nix
{ config, pkgs, ... }:

{
  home.packages = [
    (import (fetchGit {
      url = "https://github.com/profiluefter/xml-editor";
      rev = "main";
    }) { inherit pkgs; })
  ];
}
```

## Platform Support

Tested on:
- ✅ x86_64-linux
- ✅ aarch64-linux (ARM)
- ✅ x86_64-darwin (macOS Intel)
- ✅ aarch64-darwin (macOS Apple Silicon)

## Troubleshooting

### Qt platform plugin issues:
If you see "Could not find the Qt platform plugin", ensure you're using the GUI package:
```bash
nix run .#gui
```

### Missing QScintilla:
The Nix package handles QScintilla through system libraries. If you encounter issues:
```bash
# Rebuild with verbose output
nix build .#gui --print-build-logs
```

### PyQt6 import errors:
Make sure you're in the Nix environment:
```bash
nix develop
python -c "import PyQt6; print('PyQt6 available')"
```

## Contributing

When adding dependencies:
1. Update `pyproject.toml` or `requirements.txt`
2. Update `flake.nix` propagatedBuildInputs
3. Update `default.nix` propagatedBuildInputs
4. Test with `nix flake check`

## License

MIT License - Same as the main project

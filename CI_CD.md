# CI/CD Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for the XML Editor project.

## Overview

The project uses GitHub Actions for automated testing, building, and releasing. There are two main workflows:

1. **CI Workflow** (`ci.yml`) - Runs automated tests on every push and pull request
2. **Release Workflow** (`release.yml`) - Builds packages when a release is created

## CI Workflow

The CI workflow automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

### Jobs

#### Python Tests (`test-python`)
- **Platforms**: Ubuntu
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Tests Run**:
  - `test_functionality.py` - Core XML functionality tests
  - `test_schema_generation.py` - Schema generation tests

This job ensures the Python package works across different Python versions.

#### Nix Flake Checks (`test-nix`)
- **Platform**: Ubuntu (Linux)
- **Tests Run**:
  - All checks defined in `flake.nix`:
    - `build-gui` - Build the GUI package
    - `build-cli` - Build the CLI package
    - `functionality` - Run functionality tests
    - `vm-test` - Run NixOS VM tests (x86_64-linux only)

The Nix checks ensure the Nix packages build correctly and pass all tests, including a NixOS VM test that validates the application can be installed and run in a NixOS environment.

## Release Workflow

The release workflow runs on:
- Creation of a GitHub release
- Manual trigger via workflow dispatch (with tag input)

### Jobs

#### Build Python Packages (`build-python-packages`)
- **Platforms**: Ubuntu
- **Outputs**: Python wheels and source distributions in `dist/` directory
- **Artifacts**: Uploaded as `python-package-ubuntu-latest` artifacts

These packages can be installed via pip and work on all platforms (the Python package is platform-independent).

#### Build Nix Packages (`build-nix-packages`)
- **Platforms**: x86_64-linux, aarch64-linux
- **Packages Built**:
  - GUI package (`xml-editor`)
  - CLI package (`xml-editor-cli`)
- **Artifacts**: Uploaded as `nix-package-{system}` artifacts

Note: The aarch64-linux build uses QEMU for cross-compilation.

#### Create Release Assets (`create-release-assets`)
- Collects all artifacts from previous jobs
- Uploads them to the GitHub release

## NixOS VM Test

The NixOS VM test is a unique feature that validates the application can run in a NixOS environment:

### What it Tests
1. Boots a minimal NixOS VM with X11 support
2. Installs the xml-editor GUI package
3. Verifies both GUI and CLI commands are available
4. Tests that the CLI can run successfully
5. **Launches the GUI application and verifies it runs for at least 10 seconds without crashing**
6. Ensures the GUI binary is executable

This comprehensive test ensures the application not only installs correctly but also launches and runs stably.

### How to Run Locally

```bash
# Run all Nix checks (including VM test)
nix flake check

# Run only the VM test
nix build .#checks.x86_64-linux.vm-test

# Run a specific check
nix build .#checks.x86_64-linux.functionality
```

### VM Test Details
- **VM Configuration**: Minimal NixOS with lightdm and icewm
- **Auto-login**: Enabled for testing
- **GUI Launch Test**: Application is started and must run for 10+ seconds without crashing
- **Test Duration**: ~35 seconds (including GUI runtime verification)
- **Platform**: x86_64-linux only (skipped on other platforms)

## Local Testing

### Python Tests

```bash
# Install dependencies
pip install -e .

# Run tests
python test_functionality.py
python test_schema_generation.py
python test_themes.py
```

### Nix Build

```bash
# Build GUI package
nix build .#gui

# Build CLI package
nix build .#cli

# Run the application
nix run .#gui
nix run .#cli
```

### Running Tests with Nix

```bash
# Run all checks
nix flake check -L

# Build and run specific tests
nix build .#checks.x86_64-linux.functionality -L
nix build .#checks.x86_64-linux.vm-test -L
```

## Caching

The Nix workflow uses the `magic-nix-cache-action` to cache build artifacts, significantly speeding up subsequent builds. This cache is shared across workflow runs.

## Troubleshooting

### CI Failures

1. **Python tests fail**: Check if dependencies are correctly specified in `pyproject.toml`
2. **Nix build fails**: Run `nix flake check` locally to reproduce the issue
3. **VM test fails**: The VM test requires x86_64-linux and may need more resources

### Release Issues

1. **Artifacts not uploaded**: Check if all jobs completed successfully
2. **Cross-compilation fails**: Verify QEMU setup for aarch64-linux builds

## Future Improvements

Potential enhancements to consider:
- Add code coverage reporting
- Add integration tests for the GUI
- Implement automatic versioning
- Add performance benchmarks
- Create Docker containers for the application

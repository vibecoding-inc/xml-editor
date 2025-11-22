# Tests

This directory contains all tests for the XML Editor application.

## Structure

- `unit/` - Unit tests that test individual components without GUI or external dependencies
- `integration/` - Integration tests that test GUI components and require display/PyQt6

## Running Tests

### Run all tests
```bash
python tests/run_tests.py all
```

### Run only unit tests
```bash
python tests/run_tests.py unit
```

### Run only integration tests
```bash
python tests/run_tests.py integration
```

## Test Categories

### Unit Tests

- `test_xml_utilities.py` - Tests for XML validation, XPath queries, formatting, and tree structure
- `test_schema_generation.py` - Tests for XSD and DTD schema generation
- `test_themes.py` - Tests for theme definitions and integration
- `test_close_tab_fix.py` - Tests for tab closing fix with None file paths
- `test_monaco_html.py` - Tests for Monaco editor HTML structure validation
- `test_multiplayer_files.py` - Tests for multiplayer collaboration file structure

### Integration Tests

- `test_monaco_imports.py` - Tests for importing Monaco editor modules
- `test_monaco_editor_gui.py` - Tests for Monaco editor GUI functionality
- `test_monaco_render.py` - Tests for Monaco editor rendering
- `test_monaco_screenshot.py` - Tests for Monaco editor screenshot capture
- `test_console_output.py` - Tests for console output capture

## CI/CD

The CI pipeline runs unit tests on multiple Python versions (3.8, 3.10, 3.12).
Integration tests are skipped in CI as they require a display server.

## Writing New Tests

Use Python's `unittest` framework. Follow the existing test structure:

```python
import unittest

class TestMyFeature(unittest.TestCase):
    """Test description."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_something(self):
        """Test that something works."""
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()
```

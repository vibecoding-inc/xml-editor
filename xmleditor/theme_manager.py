"""
Theme Manager for XML Editor.

Provides Catppuccin color schemes and system theme detection.
Catppuccin themes: https://github.com/catppuccin/catppuccin
"""

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication
from enum import Enum


class ThemeType(Enum):
    """Available theme types."""
    SYSTEM = "system"
    CATPPUCCIN_LATTE = "catppuccin_latte"
    CATPPUCCIN_FRAPPE = "catppuccin_frappe"
    CATPPUCCIN_MACCHIATO = "catppuccin_macchiato"
    CATPPUCCIN_MOCHA = "catppuccin_mocha"


class Theme:
    """Theme definition with all colors needed for the editor."""
    
    def __init__(self, name, is_dark, colors):
        self.name = name
        self.is_dark = is_dark
        self.colors = colors
    
    def get_color(self, key):
        """Get color value by key."""
        return self.colors.get(key, "#000000")


# Catppuccin Latte (Light theme)
CATPPUCCIN_LATTE = Theme(
    name="Catppuccin Latte",
    is_dark=False,
    colors={
        # Base colors
        "base": "#eff1f5",           # Background
        "text": "#4c4f69",           # Foreground text
        "subtext0": "#6c6f85",       # Comments
        "subtext1": "#5c5f77",       # Line numbers
        "surface0": "#ccd0da",       # Lighter surface
        "surface1": "#bcc0cc",       # Medium surface
        "surface2": "#acb0be",       # Darker surface
        "overlay0": "#9ca0b0",       # Margins
        "overlay1": "#8c8fa1",
        "overlay2": "#7c7f93",
        
        # Accent colors for syntax highlighting
        "rosewater": "#dc8a78",
        "flamingo": "#dd7878",
        "pink": "#ea76cb",
        "mauve": "#8839ef",          # Keywords, tags
        "red": "#d20f39",            # Errors
        "maroon": "#e64553",
        "peach": "#fe640b",          # Numbers
        "yellow": "#df8e1d",         # Strings
        "green": "#40a02b",          # Attributes
        "teal": "#179299",
        "sky": "#04a5e5",
        "sapphire": "#209fb5",
        "blue": "#1e66f5",           # Values, attribute values
        "lavender": "#7287fd",
        
        # UI colors
        "caret_line": "#e6e9ef",     # Current line highlight
        "selection": "#ccd0da",       # Selection background
        "matched_brace": "#04a5e5",  # Matched brace highlight (sky - bright blue for visibility)
        "edge_color": "#dce0e8",     # Edge column
    }
)

# Catppuccin Frappé (Dark theme - softer)
CATPPUCCIN_FRAPPE = Theme(
    name="Catppuccin Frappé",
    is_dark=True,
    colors={
        "base": "#303446",
        "text": "#c6d0f5",
        "subtext0": "#a5adce",
        "subtext1": "#b5bfe2",
        "surface0": "#414559",
        "surface1": "#51576d",
        "surface2": "#626880",
        "overlay0": "#737994",
        "overlay1": "#838ba7",
        "overlay2": "#949cbb",
        
        "rosewater": "#f2d5cf",
        "flamingo": "#eebebe",
        "pink": "#f4b8e4",
        "mauve": "#ca9ee6",
        "red": "#e78284",
        "maroon": "#ea999c",
        "peach": "#ef9f76",
        "yellow": "#e5c890",
        "green": "#a6d189",
        "teal": "#81c8be",
        "sky": "#99d1db",
        "sapphire": "#85c1dc",
        "blue": "#8caaee",
        "lavender": "#babbf1",
        
        "caret_line": "#3b4252",
        "selection": "#414559",
        "matched_brace": "#99d1db",  # Matched brace highlight (sky - bright for visibility)
        "edge_color": "#414559",
    }
)

# Catppuccin Macchiato (Dark theme - medium)
CATPPUCCIN_MACCHIATO = Theme(
    name="Catppuccin Macchiato",
    is_dark=True,
    colors={
        "base": "#24273a",
        "text": "#cad3f5",
        "subtext0": "#a5adcb",
        "subtext1": "#b8c0e0",
        "surface0": "#363a4f",
        "surface1": "#494d64",
        "surface2": "#5b6078",
        "overlay0": "#6e738d",
        "overlay1": "#8087a2",
        "overlay2": "#939ab7",
        
        "rosewater": "#f4dbd6",
        "flamingo": "#f0c6c6",
        "pink": "#f5bde6",
        "mauve": "#c6a0f6",
        "red": "#ed8796",
        "maroon": "#ee99a0",
        "peach": "#f5a97f",
        "yellow": "#eed49f",
        "green": "#a6da95",
        "teal": "#8bd5ca",
        "sky": "#91d7e3",
        "sapphire": "#7dc4e4",
        "blue": "#8aadf4",
        "lavender": "#b7bdf8",
        
        "caret_line": "#2c2f40",
        "selection": "#363a4f",
        "matched_brace": "#91d7e3",  # Matched brace highlight (sky - bright for visibility)
        "edge_color": "#363a4f",
    }
)

# Catppuccin Mocha (Dark theme - deepest)
CATPPUCCIN_MOCHA = Theme(
    name="Catppuccin Mocha",
    is_dark=True,
    colors={
        "base": "#1e1e2e",
        "text": "#cdd6f4",
        "subtext0": "#a6adc8",
        "subtext1": "#bac2de",
        "surface0": "#313244",
        "surface1": "#45475a",
        "surface2": "#585b70",
        "overlay0": "#6c7086",
        "overlay1": "#7f849c",
        "overlay2": "#9399b2",
        
        "rosewater": "#f5e0dc",
        "flamingo": "#f2cdcd",
        "pink": "#f5c2e7",
        "mauve": "#cba6f7",
        "red": "#f38ba8",
        "maroon": "#eba0ac",
        "peach": "#fab387",
        "yellow": "#f9e2af",
        "green": "#a6e3a1",
        "teal": "#94e2d5",
        "sky": "#89dceb",
        "sapphire": "#74c7ec",
        "blue": "#89b4fa",
        "lavender": "#b4befe",
        
        "caret_line": "#262637",
        "selection": "#313244",
        "matched_brace": "#89dceb",  # Matched brace highlight (sky - bright for visibility)
        "edge_color": "#313244",
    }
)


class ThemeManager:
    """Manages themes for the XML Editor."""
    
    # Available themes
    THEMES = {
        ThemeType.CATPPUCCIN_LATTE: CATPPUCCIN_LATTE,
        ThemeType.CATPPUCCIN_FRAPPE: CATPPUCCIN_FRAPPE,
        ThemeType.CATPPUCCIN_MACCHIATO: CATPPUCCIN_MACCHIATO,
        ThemeType.CATPPUCCIN_MOCHA: CATPPUCCIN_MOCHA,
    }
    
    @staticmethod
    def detect_system_theme():
        """Detect if system is using dark mode."""
        app = QApplication.instance()
        if app:
            palette = app.palette()
            # Check if the window background is dark
            bg_color = palette.color(QPalette.ColorRole.Window)
            # A simple heuristic: if the background is darker than mid-gray, it's dark mode
            luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue()) / 255
            return luminance < 0.5
        return False
    
    @staticmethod
    def get_system_appropriate_theme():
        """Get a theme appropriate for the system color scheme."""
        is_dark = ThemeManager.detect_system_theme()
        if is_dark:
            return CATPPUCCIN_MOCHA
        else:
            return CATPPUCCIN_LATTE
    
    @staticmethod
    def get_theme(theme_type):
        """Get theme by type."""
        if theme_type == ThemeType.SYSTEM:
            return ThemeManager.get_system_appropriate_theme()
        return ThemeManager.THEMES.get(theme_type, CATPPUCCIN_MOCHA)
    
    @staticmethod
    def get_theme_names():
        """Get list of available theme names."""
        return {
            ThemeType.SYSTEM: "System (Auto)",
            ThemeType.CATPPUCCIN_LATTE: "Catppuccin Latte (Light)",
            ThemeType.CATPPUCCIN_FRAPPE: "Catppuccin Frappé (Dark)",
            ThemeType.CATPPUCCIN_MACCHIATO: "Catppuccin Macchiato (Dark)",
            ThemeType.CATPPUCCIN_MOCHA: "Catppuccin Mocha (Dark)",
        }

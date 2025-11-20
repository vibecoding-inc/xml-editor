# Theme Reference

This document provides a reference for the Catppuccin themes implemented in the XML Editor.

## Theme Overview

The XML Editor now supports 5 theme options:

1. **System (Auto)** - Automatically detects system dark/light mode
2. **Catppuccin Latte** - Light theme
3. **Catppuccin Frappé** - Dark theme (soft)
4. **Catppuccin Macchiato** - Dark theme (medium)
5. **Catppuccin Mocha** - Dark theme (deep)

## Theme Details

### Catppuccin Latte (Light Theme)
- **Base Background**: `#eff1f5` (light gray-blue)
- **Text Color**: `#4c4f69` (dark blue-gray)
- **Best for**: Daytime coding, well-lit environments

Key syntax colors:
- Tags: `#8839ef` (purple)
- Attributes: `#40a02b` (green)
- Strings: `#df8e1d` (yellow)
- Numbers: `#fe640b` (orange)
- Comments: `#6c6f85` (muted gray)

### Catppuccin Frappé (Dark Theme - Soft)
- **Base Background**: `#303446` (blue-gray)
- **Text Color**: `#c6d0f5` (light blue-white)
- **Best for**: Evening coding, reduced eye strain

Key syntax colors:
- Tags: `#ca9ee6` (lavender)
- Attributes: `#a6d189` (soft green)
- Strings: `#e5c890` (yellow)
- Numbers: `#ef9f76` (peach)
- Comments: `#a5adce` (muted blue)

### Catppuccin Macchiato (Dark Theme - Medium)
- **Base Background**: `#24273a` (dark blue-gray)
- **Text Color**: `#cad3f5` (light blue-white)
- **Best for**: Late evening coding, moderate contrast

Key syntax colors:
- Tags: `#c6a0f6` (purple)
- Attributes: `#a6da95` (green)
- Strings: `#eed49f` (yellow)
- Numbers: `#f5a97f` (peach)
- Comments: `#a5adcb` (muted blue)

### Catppuccin Mocha (Dark Theme - Deep)
- **Base Background**: `#1e1e2e` (very dark blue-gray)
- **Text Color**: `#cdd6f4` (light blue-white)
- **Best for**: Night coding, low-light environments, OLED displays

Key syntax colors:
- Tags: `#cba6f7` (purple)
- Attributes: `#a6e3a1` (green)
- Strings: `#f9e2af` (yellow)
- Numbers: `#fab387` (peach)
- Comments: `#a6adc8` (muted blue)

## System Theme Detection

The "System (Auto)" option uses Qt's QPalette to detect if the operating system is using a dark theme:

- It calculates the luminance of the window background color
- If luminance < 0.5 (darker), it selects **Catppuccin Mocha**
- If luminance >= 0.5 (lighter), it selects **Catppuccin Latte**

This ensures the editor always has appropriate contrast regardless of system settings.

## UI Elements Themed

All themes consistently apply colors to:

1. **Editor**:
   - Background
   - Text/foreground
   - Current line highlight
   - Selection background

2. **Margins**:
   - Line number background
   - Line number text
   - Fold marker background

3. **Syntax Highlighting** (via QScintilla lexer):
   - XML tags/elements
   - Attribute names
   - Attribute values (strings)
   - Numbers
   - Comments
   - CDATA sections
   - Entities
   - Unknown/error tags

4. **Interactive Elements**:
   - Matched brace highlighting
   - Unmatched brace highlighting
   - Edge column marker
   - Caret (cursor)

## Changing Themes

To change themes:

1. Open the application
2. Go to **View** menu → **Theme**
3. Select your preferred theme
4. Theme is applied immediately
5. Preference is saved for next session

## Theme Accessibility

All Catppuccin themes are designed with accessibility in mind:

- **High Contrast**: All themes meet WCAG AA standards for contrast
- **Colorblind-Friendly**: Color choices work well for common types of color blindness
- **Consistent**: Similar semantic colors across all themes (e.g., errors always red-ish)
- **Readable**: Carefully chosen font colors for long coding sessions

## Credits

Themes based on the [Catppuccin](https://catppuccin.com/) color palette, which is:
- Created by the Catppuccin community
- Licensed under MIT
- Available for hundreds of applications
- Focused on pastel colors that are soothing to the eyes

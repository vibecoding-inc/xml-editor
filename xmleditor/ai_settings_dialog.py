"""
AI Settings Dialog for configuring the AI API endpoint and credentials.
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QGroupBox, QMessageBox, QComboBox, QApplication,
    QCheckBox
)
from PyQt6.QtCore import Qt


class AISettingsManager:
    """Manages AI settings storage in user's home directory."""
    
    DEFAULT_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "openai/gpt-4o-mini"
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "xml-editor"
        self.config_file = self.config_dir / "ai_settings.json"
        self._settings = None
    
    def _ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self):
        """Load settings from the config file."""
        if self._settings is not None:
            return self._settings
        
        default_settings = {
            "api_url": self.DEFAULT_API_URL,
            "api_key": "",
            "model": self.DEFAULT_MODEL,
            "enter_sends_message": True,  # True = Enter sends, Shift+Enter newline
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults to handle new settings
                    default_settings.update(saved_settings)
            except (json.JSONDecodeError, IOError):
                pass
        
        self._settings = default_settings
        return self._settings
    
    def save_settings(self, settings):
        """Save settings to the config file."""
        self._ensure_config_dir()
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            self._settings = settings
            
            # Set restrictive permissions on the config file (owner read/write only)
            os.chmod(self.config_file, 0o600)
            return True
        except IOError as e:
            return False
    
    def get_api_url(self):
        """Get the configured API URL."""
        return self.load_settings().get("api_url", self.DEFAULT_API_URL)
    
    def get_api_key(self):
        """Get the configured API key."""
        return self.load_settings().get("api_key", "")
    
    def get_model(self):
        """Get the configured model name."""
        return self.load_settings().get("model", self.DEFAULT_MODEL)
    
    def is_configured(self):
        """Check if API key is configured."""
        return bool(self.get_api_key().strip())
    
    def reload_settings(self):
        """Force reload settings from disk."""
        self._settings = None
        return self.load_settings()


class AISettingsDialog(QDialog):
    """Dialog for configuring AI API settings."""
    
    # Common OpenAI-compatible endpoints
    PRESET_ENDPOINTS = {
        "OpenRouter (Default)": "https://openrouter.ai/api/v1/chat/completions",
        "OpenAI": "https://api.openai.com/v1/chat/completions",
        "Local (Ollama)": "http://localhost:11434/v1/chat/completions",
        "Custom": "",
    }
    
    COMMON_MODELS = [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-4-turbo",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        "google/gemini-2.0-flash-exp",
        "google/gemini-pro",
        "mistralai/mistral-large",
        "meta-llama/llama-3.1-70b-instruct",
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = AISettingsManager()
        self.setWindowTitle("AI Assistant Settings")
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # API Configuration Group
        api_group = QGroupBox("API Configuration")
        api_layout = QFormLayout(api_group)
        
        # Endpoint preset selector
        self.endpoint_preset = QComboBox()
        self.endpoint_preset.addItems(list(self.PRESET_ENDPOINTS.keys()))
        self.endpoint_preset.currentTextChanged.connect(self.on_preset_changed)
        api_layout.addRow("Endpoint Preset:", self.endpoint_preset)
        
        # API URL
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://openrouter.ai/api/v1/chat/completions")
        api_layout.addRow("API URL:", self.api_url_input)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API Key:", self.api_key_input)
        
        # Show/Hide API Key button
        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.setMaximumWidth(60)
        self.show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        api_layout.addRow("", self.show_key_btn)
        
        # Model selection
        self.model_input = QComboBox()
        self.model_input.setEditable(True)
        self.model_input.addItems(self.COMMON_MODELS)
        self.model_input.setCurrentText("openai/gpt-4o-mini")
        api_layout.addRow("Model:", self.model_input)
        
        layout.addWidget(api_group)
        
        # Behavior Settings Group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        # Enter key behavior
        self.enter_sends_checkbox = QCheckBox("Enter sends message (Shift+Enter for newline)")
        self.enter_sends_checkbox.setToolTip(
            "When checked, pressing Enter sends the message and Shift+Enter adds a newline.\n"
            "When unchecked, pressing Enter adds a newline and Shift+Enter sends the message."
        )
        behavior_layout.addRow(self.enter_sends_checkbox)
        
        layout.addWidget(behavior_group)
        
        # Info label
        info_label = QLabel(
            "💡 Settings are stored in ~/.config/xml-editor/ai_settings.json\n"
            "The API key is stored with restricted file permissions."
        )
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Test connection button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("🔗 Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(self.test_btn)
        
        self.test_status = QLabel("")
        test_layout.addWidget(self.test_status, 1)
        layout.addLayout(test_layout)
        
        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def on_preset_changed(self, preset_name):
        """Handle preset selection change."""
        if preset_name in self.PRESET_ENDPOINTS:
            url = self.PRESET_ENDPOINTS[preset_name]
            if url:  # Not custom
                self.api_url_input.setText(url)
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("Show")
    
    def load_current_settings(self):
        """Load current settings into the form."""
        settings = self.settings_manager.load_settings()
        
        self.api_url_input.setText(settings.get("api_url", ""))
        self.api_key_input.setText(settings.get("api_key", ""))
        self.model_input.setCurrentText(settings.get("model", "openai/gpt-3.5-turbo"))
        self.enter_sends_checkbox.setChecked(settings.get("enter_sends_message", True))
        
        # Set preset based on URL
        current_url = settings.get("api_url", "")
        preset_found = False
        for name, url in self.PRESET_ENDPOINTS.items():
            if url == current_url:
                self.endpoint_preset.setCurrentText(name)
                preset_found = True
                break
        
        if not preset_found and current_url:
            self.endpoint_preset.setCurrentText("Custom")
    
    def save_settings(self):
        """Save settings and close dialog."""
        settings = {
            "api_url": self.api_url_input.text().strip(),
            "api_key": self.api_key_input.text().strip(),
            "model": self.model_input.currentText().strip(),
            "enter_sends_message": self.enter_sends_checkbox.isChecked(),
        }
        
        if not settings["api_url"]:
            QMessageBox.warning(self, "Validation Error", "API URL is required.")
            return
        
        if self.settings_manager.save_settings(settings):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings.")
    
    def test_connection(self):
        """Test the API connection."""
        api_url = self.api_url_input.text().strip()
        api_key = self.api_key_input.text().strip()
        model = self.model_input.currentText().strip()
        
        if not api_url or not api_key:
            self.test_status.setText("❌ API URL and Key required")
            self.test_status.setStyleSheet("color: red;")
            return
        
        self.test_status.setText("⏳ Testing...")
        self.test_status.setStyleSheet("color: gray;")
        self.test_btn.setEnabled(False)
        
        # Force UI update
        QApplication.processEvents()
        
        try:
            # Prepare a minimal test request
            data = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }).encode('utf-8')
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            req = urllib.request.Request(api_url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    self.test_status.setText("✅ Connection successful!")
                    self.test_status.setStyleSheet("color: green;")
                else:
                    self.test_status.setText(f"⚠️ Unexpected status: {response.status}")
                    self.test_status.setStyleSheet("color: orange;")
        
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.test_status.setText("❌ Invalid API key")
            elif e.code == 404:
                self.test_status.setText("❌ Invalid API URL")
            else:
                self.test_status.setText(f"❌ HTTP Error: {e.code}")
            self.test_status.setStyleSheet("color: red;")
        
        except urllib.error.URLError as e:
            self.test_status.setText(f"❌ Connection failed: {str(e.reason)[:30]}")
            self.test_status.setStyleSheet("color: red;")
        
        except Exception as e:
            self.test_status.setText(f"❌ Error: {str(e)[:30]}")
            self.test_status.setStyleSheet("color: red;")
        
        finally:
            self.test_btn.setEnabled(True)

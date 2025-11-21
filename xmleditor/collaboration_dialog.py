"""
Dialogs for collaborative editing sessions.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt


class HostSessionDialog(QDialog):
    """Dialog for hosting a collaboration session."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Host Collaboration Session")
        self.setModal(True)
        self.resize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Host a collaboration session to allow others to edit this document with you.\n"
            "Share the Room Name with others so they can join your session."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Server URL
        server_layout = QHBoxLayout()
        server_label = QLabel("Server URL:")
        server_label.setMinimumWidth(100)
        server_layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("wss://your-worker.workers.dev")
        # Placeholder URL - users must deploy their own worker
        self.server_input.setText("wss://your-worker.workers.dev")
        server_layout.addWidget(self.server_input)
        
        layout.addLayout(server_layout)
        
        # Room name
        room_layout = QHBoxLayout()
        room_label = QLabel("Room Name:")
        room_label.setMinimumWidth(100)
        room_layout.addWidget(room_label)
        
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("my-document-room")
        # Generate a default room name
        import uuid
        default_room = f"room-{uuid.uuid4().hex[:8]}"
        self.room_input.setText(default_room)
        room_layout.addWidget(self.room_input)
        
        layout.addLayout(room_layout)
        
        # Info text
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(120)
        info_text.setPlainText(
            "How to deploy your Cloudflare Worker:\n"
            "1. Install wrangler: npm install -g wrangler\n"
            "2. Navigate to the 'cloudflare-worker' directory\n"
            "3. Run: wrangler deploy\n"
            "4. Use the deployed URL as the Server URL above\n\n"
            "Note: You'll need a Cloudflare account (free tier available)."
        )
        layout.addWidget(info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.host_button = QPushButton("Host Session")
        self.host_button.clicked.connect(self.accept)
        button_layout.addWidget(self.host_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_connection_info(self):
        """Get the server URL and room name."""
        return self.server_input.text().strip(), self.room_input.text().strip()


class JoinSessionDialog(QDialog):
    """Dialog for joining a collaboration session."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Join Collaboration Session")
        self.setModal(True)
        self.resize(500, 250)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Join an existing collaboration session by entering the server URL and room name\n"
            "provided by the host."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Server URL
        server_layout = QHBoxLayout()
        server_label = QLabel("Server URL:")
        server_label.setMinimumWidth(100)
        server_layout.addWidget(server_label)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("wss://your-worker.workers.dev")
        self.server_input.setText("wss://your-worker.workers.dev")
        server_layout.addWidget(self.server_input)
        
        layout.addLayout(server_layout)
        
        # Room name
        room_layout = QHBoxLayout()
        room_label = QLabel("Room Name:")
        room_label.setMinimumWidth(100)
        room_layout.addWidget(room_label)
        
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("room-name-from-host")
        room_layout.addWidget(self.room_input)
        
        layout.addLayout(room_layout)
        
        # Warning
        warning = QLabel(
            "⚠️ Warning: Joining a session will replace your current document content\n"
            "with the shared document. Make sure to save any unsaved changes first."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #ff6b6b; padding: 10px;")
        layout.addWidget(warning)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.join_button = QPushButton("Join Session")
        self.join_button.clicked.connect(self.accept)
        button_layout.addWidget(self.join_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_connection_info(self):
        """Get the server URL and room name."""
        return self.server_input.text().strip(), self.room_input.text().strip()

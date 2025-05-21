"""
  Copyright (c) 2025 Alexandre Kavadias 

  This project is licensed under the Educational and Non-Commercial Use License.
  See the LICENSE file for details.
"""


import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMenuBar, QMenu, QInputDialog,QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QTextCursor,QIcon,QAction
from PyQt6.QtCore import QThread, pyqtSignal, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView

import markdown  # Convert Markdown to HTML

API_URL = "http://192.168.68.106:8000/chat/"
API_URL_HISTORY = "http://192.168.68.106:8000/get-item/"
SESSION_ID="123"

# Worker Thread for Chatbot Processing
class ChatbotWorker(QThread):
    result = pyqtSignal(object)  # Signal emitted when chatbot response is ready

    def __init__(self, url, user_message,method="POST"):
        super().__init__()
        self.payload = user_message  # Store user message
        self.url = url
        self.method = method
        print(f"ChatbotWorker initialized with payload: {self.payload}")

    def run(self):
        """Simulates chatbot processing in a separate thread"""
        import requests
        try:
            print(f"ChatbotWorker::run: {self.url}, method: {self.method}, payload: {self.payload}")
            if self.method=="POST":
                response = requests.post(
                    self.url,
                    json=self.payload,
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("response") or data.get("reply", {}).get("response", "")
                    self.result.emit(reply)
                else:
                    self.result.emit(f"[Error] API returned status {response.status_code}")
            elif self.method == "GET":
                
                response = requests.get(
                    self.url,
                    params=self.payload if self.payload else None,
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("history") or data.get("history", {}).get("history", "")
                   
                    self.result.emit(reply)
                else:
                    self.result.emit(f"[Error] API returned status {response.status_code}")

        except Exception as e:
            self.result.emit(f"[Error] {e}")
        


class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.session_id= SESSION_ID
        self.api_url = API_URL  # Instance variable for API URL
    
        self.setStyleSheet(self.material_style())
        self.init_menu()
        self.init_ui()

    def get_session_history(self):
         # Start chatbot processing in a separate thread
        self.worker = ChatbotWorker(API_URL_HISTORY+self.session_id,None,"GET")
        self.worker.result.connect(self.display_bot_response)
        self.worker.start()

    def material_style(self):
        # Material Design inspired stylesheet with blue accents
        return f"""
        QWidget {{
            background: #bcd5f7;
            font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
            font-size: 15px;
            background-repeat: no-repeat;
            background-position: top right;
        }}
        QLabel {{
            color: #1976d2;
            font-weight: bold;
        }}
        QLineEdit {{
            border: 2px solid #90caf9;
            border-radius: 6px;
            padding: 8px;
            background: #e3f2fd;
            color: #0d47a1;
        }}
        QLineEdit:focus {{
            border: 2px solid #1976d2;
            background: #ffffff;
        }}
        QTextEdit {{
            border: 2px solid #90caf9;
            border-radius: 8px;
            background: #e3f2fd;
            color: #263238;
            padding: 8px;
        }}
        QPushButton {{
            background-color: #1976d2;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 24px;
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: #1565c0;
        }}
        QPushButton:pressed {{
            background-color: #0d47a1;
        }}
        """


    def init_ui(self):
        # Set window properties
        self.setWindowTitle("Chatbot")
        self.setGeometry(100, 100, 800, 600)
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "robot.png")
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        # Add the menu bar at the top
        layout.setMenuBar(self.menubar)

        session_layout = QHBoxLayout()
        session_label = QLabel("Session ID:")
        self.session_input = QLineEdit(self.session_id)
        self.session_input.setFixedWidth(120)
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_input)
        self.set_session_id_button = QPushButton("Save")
        self.set_session_id_button.clicked.connect(self.set_session_id)
        session_layout.addWidget(self.set_session_id_button)

        self.get_history_button = QPushButton("Get history")
        self.get_history_button.clicked.connect(self.get_session_history)
        session_layout.addWidget(self.get_history_button)
        session_layout.addStretch()
        layout.addLayout(session_layout)

        # Chat display area (non-editable)
        self.chat_display = QWebEngineView()

        html_content = self.get_html_content()
        self.chat_display.setHtml(html_content)
       

        layout.addWidget(self.chat_display)

        # Message input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setText("give me a receip for a lemon cake")
        self.input_field.returnPressed.connect(self.send_message)  # Handle Enter key
        layout.addWidget(self.input_field)

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # Set layout
        self.setLayout(layout)
        
    def set_session_id(self):
        """Set the session ID from the input field."""
        new_session_id = self.session_input.text().strip()
        if new_session_id:
            self.session_id = new_session_id
            print(f"New session ID: {self.session_id}")
        else:
            print("Invalid session ID")


    def get_html_content(self):
        """Returns the HTML content for the chat display."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Chatbot Web View</title>
            <style>
            body {
                background: #e3f2fd; 
            }
            #chatContainer {
                color: #263238; 
                padding: 8px;
                display: flex;
                flex-direction: column;
                font-family: Segoe UI;
                font-weight: normal;
            }
            .message {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 5px;
                width: fit-content;
                max-width: 80%;
            }
            .message.User {
                margin-left: auto;
                margin-right: 0;
                border: 2px solid #00838f; 
                border-radius: 8px;
                background:#e0f7fa;
                color:#00838f;
                text-align:right;
                font-size: 0.9rem;
            }

            .message.Model {
                margin-right: auto;
                margin-left: 0;
                border: 2px solid #1976d2; 
                border-radius: 8px;
                background:#c7dded;
                color:#1976d2;
                text-align:left;
                font-size: 0.9rem;
            }
            .message.thinking {
                margin-right: auto;
                margin-left: 0;
                border: 2px solid #1976d2; 
                border-radius: 8px;
                background:#c7dded;
                color:#1976d2;
                text-align:left;
                font-size: 0.9rem;
            }
            </style>

        </head>
        <body>
            <div id="chatContainer"></div>
        </body>
        </html>
        """

    def init_menu(self):
       
        # Create a menu bar and add File/Exit and Options/URL
        menubar = QMenuBar(self)
        menubar.setNativeMenuBar(False)
        menubar.setStyleSheet("""
            QMenuBar {
                background: transparent;
                color: #1976d2;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 15px;
                font-weight: bold;
            }
            QMenuBar::item {
                background: transparent;
                color: #1976d2;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 15px;
                font-weight: bold;
            }
            QMenuBar::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)
        menu_style = """
            QMenu {
                background: #f5f7fa;
                color: #1976d2;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 15px;
                font-weight: bold;
            }
            QMenu::item {
                color: #1976d2 !important;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif !important;
                font-size: 15px !important;
                font-weight: bold !important;
                background: transparent !important;
            }
            QMenu::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
            QAction { /* Style QAction directly when the menu's stylesheet is active */
                color: #1976d2 !important;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif !important;
                font-size: 15px !important;
                font-weight: bold !important;
                background: transparent !important;
            }
            QAction:hover {
                background: #e3f2fd;
                color: #1976d2;
            }
        """
        file_menu = QMenu("File", self)
        file_menu.setStyleSheet(menu_style)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(exit_action)

        options_menu = QMenu("Options", self)
        options_menu.setStyleSheet(menu_style)
        url_action = QAction("API Endpoint", self)
        url_action.triggered.connect(self.change_api_url)

        options_menu.addAction(url_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(options_menu)
        # Insert the menubar at the top of the layout
        self.menubar = menubar

    def change_api_url(self):
        """Change the API URL using a QInputDialog"""
        dlg =  QInputDialog(self)                 
        dlg.setInputMode(QInputDialog.InputMode.TextInput) 
        dlg.setLabelText("Enter new API URL:")    
                            
        dlg.resize(500,100)
        dlg.setTextValue(self.api_url)                             
        ok = dlg.exec()                                
        url = dlg.textValue()
        if ok and url:
            self.api_url = url
            print(f"New API URL: {self.api_url}")

    def send_message(self):
        """Handles sending a message and chatbot response."""
        message = self.input_field.text().strip()
        try:
            if message:
                self.inject_chat_message("User",message)
                self.inject_wait_message()
                #self.display_message(message, "user")  # Display user message (right)
                self.input_field.clear()


                # Display "thinking" message
                #self.display_message("_Thinking..._", "bot")
                #self.inject_chat_message("model",)

                # Start chatbot processing in a separate thread
                self.worker = ChatbotWorker(API_URL,{"prompt":message,"session_id": self.session_id})
                self.worker.result.connect(self.display_bot_response)
                self.worker.start()

                
        except Exception as e:
            print(f"Exception: {e}")
            self.inject_chat_message("Model",f"Exception: {e}")
            #self.display_message(f"Exception: {e}", "bot")  # Display bot message (left)

    

    

    def display_bot_response(self, response):
        """Displays the chatbot response once the thread finishes."""
        # Remove "thinking" message before adding real response
        js_code = """
            var chatContainer = document.getElementById("chatContainer");
            var messageDiv = chatContainer.lastElementChild;
            if (messageDiv && messageDiv.className === "message thinking") {
                chatContainer.removeChild(messageDiv);
            }
        """
        self.chat_display.page().runJavaScript(js_code)
        if  isinstance(response,list):
            for item in response:
                if isinstance(item,dict):
                    if item["role"]=="model":
                        self.inject_chat_message("Model",item["parts"])
                    elif item["role"]=="user":
                        self.inject_chat_message("User",item["parts"])
                    else:
                        self.inject_chat_message("System",f"Unknown item: {item}")
                
        else:
            self.inject_chat_message("Model",response)
        #self.display_message(response, "bot")

    def inject_wait_message(self):
        
        """Injects a "thinking" message into the chat display."""
        
        print("Injecting wait message")
        js_code = """
        var chatContainer = document.getElementById("chatContainer");
        var messageDiv = document.createElement("div");
        messageDiv.className = "message thinking";
        messageDiv.innerHTML = "<b>Model</b> Thinking...";
        chatContainer.appendChild(messageDiv);
        window.scrollTo(0, document.body.scrollHeight);
        """
        self.chat_display.page().runJavaScript(js_code)


    def inject_chat_message(self, sender, message):
    
        message_html = markdown.markdown(message)
        safe_html = json.dumps(f"<b>{sender}:</b> {message_html}")
        js_code = f"""
        var chatContainer = document.getElementById(\"chatContainer\");
        var messageDiv = document.createElement(\"div\");
        messageDiv.className = \"message {sender}\";
        messageDiv.innerHTML = \"<b>{sender}</b> {message_html.replace("\"","\\""").replace("\n","")}\";
        chatContainer.appendChild(messageDiv);
        window.scrollTo(0, document.body.scrollHeight);
        """
        print("-"*10)
        print(js_code)
        print("-"*10)

        print("-"*10)
        print(safe_html)
        print("-"*10)
        safe_html
        self.chat_display.page().runJavaScript(js_code)

    def load_finished_handler(self, ok):
        if ok:
            pass

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_window = ChatApp()
    chat_window.show()
    sys.exit(app.exec())

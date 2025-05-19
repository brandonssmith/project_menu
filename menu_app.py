import sys
import os
import subprocess
import json
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QListWidget, QLabel, QListWidgetItem, QDialog,
                            QPushButton, QHBoxLayout, QMessageBox, QComboBox,
                            QGridLayout, QFrame, QMenuBar, QMenu, QFileDialog,
                            QLineEdit, QFormLayout, QScrollArea, QToolTip)
from PyQt6.QtCore import Qt, QUrl, QSize, QSettings, QTimer, QPoint
from PyQt6.QtGui import QDesktopServices, QIcon, QFont, QAction, QTextDocument

def detect_project_type(project_path):
    """Detect the type of project and return its icon and type name."""
    # Check for various project indicators
    if os.path.exists(os.path.join(project_path, "package.json")):
        # Check for specific frameworks
        if os.path.exists(os.path.join(project_path, "next.config.js")):
            return "⚛️", "Next.js"
        elif os.path.exists(os.path.join(project_path, "angular.json")):
            return "🅰️", "Angular"
        elif os.path.exists(os.path.join(project_path, "vue.config.js")):
            return "⚡", "Vue.js"
        elif os.path.exists(os.path.join(project_path, "react-scripts")):
            return "⚛️", "React"
        else:
            return "📦", "Node.js"
    
    if os.path.exists(os.path.join(project_path, "requirements.txt")):
        # Check for specific Python frameworks
        if os.path.exists(os.path.join(project_path, "manage.py")):
            return "🐍", "Django"
        elif os.path.exists(os.path.join(project_path, "flask_app.py")):
            return "🌶️", "Flask"
        else:
            return "🐍", "Python"
    
    if os.path.exists(os.path.join(project_path, "Cargo.toml")):
        return "🦀", "Rust"
    
    if os.path.exists(os.path.join(project_path, "pom.xml")):
        return "☕", "Java"
    
    if os.path.exists(os.path.join(project_path, "build.gradle")):
        return "☕", "Gradle"
    
    if os.path.exists(os.path.join(project_path, "composer.json")):
        return "🐘", "PHP"
    
    if os.path.exists(os.path.join(project_path, "Gemfile")):
        return "💎", "Ruby"
    
    if os.path.exists(os.path.join(project_path, "go.mod")):
        return "🦫", "Go"
    
    if os.path.exists(os.path.join(project_path, "pubspec.yaml")):
        return "🎯", "Flutter"
    
    if os.path.exists(os.path.join(project_path, "CMakeLists.txt")):
        return "⚙️", "C/C++"
    
    if os.path.exists(os.path.join(project_path, "mix.exs")):
        return "💧", "Elixir"
    
    if os.path.exists(os.path.join(project_path, "project.clj")):
        return "🧪", "Clojure"
    
    if os.path.exists(os.path.join(project_path, "build.sbt")):
        return "⚡", "Scala"
    
    if os.path.exists(os.path.join(project_path, "Dockerfile")):
        return "🐳", "Docker"
    
    # Check for web files
    web_files = ['.html', '.js', '.css', '.ts', '.jsx', '.tsx']
    if any(any(f.endswith(ext) for ext in web_files) for f in os.listdir(project_path)):
        return "🌐", "Web"
    
    # Default icon for unknown project type
    return "��", "Project"

class NodeLaunchDialog(QDialog):
    def __init__(self, project_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Launch Node.js Project")
        self.setGeometry(200, 200, 500, 250)
        self.project_path = project_path
        
        layout = QVBoxLayout(self)
        
        # Get package.json info
        package_json_path = os.path.join(project_path, "package.json")
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                self.project_name = package_data.get('name', 'Unknown Project')
                self.project_url = package_data.get('homepage', '')
                self.scripts = package_data.get('scripts', {})
        except Exception as e:
            self.project_name = "Unknown Project"
            self.project_url = ""
            self.scripts = {}
            QMessageBox.warning(self, "Error", f"Could not read package.json: {str(e)}")
        
        # Add project info
        info_label = QLabel(f"Project: {self.project_name}")
        info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(info_label)
        
        if self.project_url:
            url_label = QLabel(f"URL: {self.project_url}")
            layout.addWidget(url_label)
        
        # Add script selection
        if self.scripts:
            script_layout = QHBoxLayout()
            script_label = QLabel("Select script to run:")
            script_layout.addWidget(script_label)
            
            self.script_combo = QComboBox()
            for script_name in self.scripts.keys():
                self.script_combo.addItem(script_name)
            script_layout.addWidget(self.script_combo)
            layout.addLayout(script_layout)
        else:
            no_scripts_label = QLabel("No npm scripts found in package.json")
            no_scripts_label.setStyleSheet("color: red;")
            layout.addWidget(no_scripts_label)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        if self.project_url:
            open_url_btn = QPushButton("Open URL")
            open_url_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.project_url)))
            button_layout.addWidget(open_url_btn)
        
        if self.scripts:
            launch_btn = QPushButton("Run Script")
            launch_btn.clicked.connect(self.launch_project)
            button_layout.addWidget(launch_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def launch_project(self):
        if not self.scripts:
            QMessageBox.warning(self, "Error", "No npm scripts available to run")
            return
            
        selected_script = self.script_combo.currentText()
        try:
            subprocess.Popen(["npm", "run", selected_script], cwd=self.project_path, shell=True)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run npm script: {str(e)}")

class ProjectTooltip(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Description label
        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("font-size: 11px;")
        self.desc_label.setMaximumWidth(300)  # Limit width for better readability
        layout.addWidget(self.desc_label)
        
        # Hide initially
        self.hide()
    
    def show_tooltip(self, text, pos):
        self.desc_label.setText(text.get('description', ''))
        self.adjustSize()
        
        # Position the tooltip
        screen = QApplication.primaryScreen().geometry()
        tooltip_size = self.sizeHint()
        
        # Calculate position to ensure tooltip stays on screen
        x = pos.x() + 20
        y = pos.y() + 20
        
        if x + tooltip_size.width() > screen.right():
            x = pos.x() - tooltip_size.width() - 20
        if y + tooltip_size.height() > screen.bottom():
            y = pos.y() - tooltip_size.height() - 20
        
        self.move(x, y)
        self.show()

def extract_readme_info(project_path):
    """Extract information from README files in the project directory."""
    readme_files = ['README.md', 'README.txt', 'README', 'readme.md', 'readme.txt']
    info = {
        'title': os.path.basename(project_path),
        'description': 'No description available'
    }
    
    # Try to find and read README file
    for readme in readme_files:
        readme_path = os.path.join(project_path, readme)
        if os.path.exists(readme_path):
            try:
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract title (first heading or first line)
                    title_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
                    if title_match:
                        info['title'] = title_match.group(1).strip()
                    
                    # Extract first sentence or two after title
                    # Look for content after the first heading
                    content_after_title = re.split(r'^#.+\n+', content, maxsplit=1, flags=re.MULTILINE)
                    if len(content_after_title) > 1:
                        # Get the first paragraph
                        first_para = content_after_title[1].split('\n\n')[0]
                        
                        # Clean up the text
                        desc = first_para.strip()
                        desc = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', desc)  # Remove markdown links
                        desc = re.sub(r'`([^`]+)`', r'\1', desc)  # Remove code formatting
                        desc = re.sub(r'\*\*([^*]+)\*\*', r'\1', desc)  # Remove bold
                        desc = re.sub(r'\*([^*]+)\*', r'\1', desc)  # Remove italic
                        desc = re.sub(r'\n+', ' ', desc)  # Replace newlines with spaces
                        
                        # Split into sentences and take first two
                        sentences = re.split(r'(?<=[.!?])\s+', desc)
                        if len(sentences) > 2:
                            desc = ' '.join(sentences[:2])
                        
                        info['description'] = desc
                    
                    break  # Stop after finding first README
            except Exception as e:
                print(f"Error reading README: {e}")
    
    return info

class ProjectCard(QFrame):
    def __init__(self, project_name, project_path, main_window, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.main_window = main_window
        self.setFixedSize(140, 105)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        # Create layout for the card
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Get project type and icon
        icon, project_type = detect_project_type(project_path)
        
        # Project name label
        name_label = QLabel(project_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-size: 12px; font-weight: bold;")
        layout.addWidget(name_label)
        
        # Project type label
        type_label = QLabel(project_type)
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(type_label)
        
        # Add some spacing
        layout.addSpacing(2)
        
        # Add the project type icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # Make the card clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Initialize tooltip
        self.tooltip = ProjectTooltip()
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.show_tooltip)
        
        # Load project info
        self.project_info = extract_readme_info(project_path)
    
    def enterEvent(self, event):
        self.tooltip_timer.start(500)  # Show tooltip after 500ms
    
    def leaveEvent(self, event):
        self.tooltip_timer.stop()
        self.tooltip.hide()
    
    def show_tooltip(self):
        self.tooltip.show_tooltip(self.project_info, self.mapToGlobal(QPoint(0, 0)))
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.main_window.launch_project(self.project_path)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 500, 150)
        
        # Create layout
        layout = QFormLayout(self)
        
        # Projects directory input
        self.dir_input = QLineEdit()
        self.dir_input.setText(parent.settings.value("projects_directory", "C:\\code"))
        
        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_directory)
        
        # Create horizontal layout for directory input and browse button
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        
        layout.addRow("Projects Directory:", dir_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Projects Directory",
            self.dir_input.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if dir_path:
            self.dir_input.setText(dir_path)
    
    def save_settings(self):
        self.parent().settings.setValue("projects_directory", self.dir_input.text())
        self.parent().settings.sync()
        self.accept()
        # Reload projects with new directory
        self.parent().load_projects()

class ProjectMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cursor Projects Menu")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize settings
        self.settings = QSettings("CursorProjects", "Menu")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add title label
        title = QLabel("My Projects")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create container widget for the grid
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(15)  # Reduced spacing between cards
        self.grid_layout.setContentsMargins(20, 20, 20, 20)  # Add margins around the grid
        
        # Set the container as the scroll area's widget
        scroll_area.setWidget(container)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)
        
        # Load projects
        self.load_projects()
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def is_valid_project(self, project_path):
        """Check if the directory contains a valid application project."""
        # Common project configuration files
        config_files = [
            "package.json",      # Node.js
            "requirements.txt",   # Python
            "setup.py",          # Python
            "pyproject.toml",    # Python (modern)
            "Cargo.toml",        # Rust
            "pom.xml",          # Java/Maven
            "build.gradle",      # Java/Gradle
            "composer.json",     # PHP
            "Gemfile",          # Ruby
            "go.mod",           # Go
            "tsconfig.json",    # TypeScript
            "angular.json",     # Angular
            "vue.config.js",    # Vue.js
            "next.config.js",   # Next.js
            "nuxt.config.js",   # Nuxt.js
            "webpack.config.js", # Webpack
            "vite.config.js",   # Vite
            "docker-compose.yml", # Docker
            "Dockerfile",       # Docker
            ".env",             # Environment config
            "config.json",      # Generic config
            "app.json",         # React Native
            "pubspec.yaml",     # Flutter
            "CMakeLists.txt",   # C/C++
            "Makefile",         # C/C++/Generic
            "mix.exs",          # Elixir
            "project.clj",      # Clojure
            "build.sbt",        # Scala
            "build.xml",        # Ant
            "bower.json",       # Bower
            "yarn.lock",        # Yarn
            "pnpm-lock.yaml",   # pnpm
            "package-lock.json" # npm
        ]

        # Check for configuration files
        for config_file in config_files:
            if os.path.exists(os.path.join(project_path, config_file)):
                return True

        # Check for source code files
        source_extensions = {
            # Web
            '.html', '.htm', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.sass', '.less',
            # Python
            '.py', '.pyx', '.pyd', '.pyi',
            # Java
            '.java', '.class', '.jar',
            # C/C++
            '.c', '.cpp', '.h', '.hpp', '.cc', '.cxx',
            # Go
            '.go',
            # Rust
            '.rs',
            # PHP
            '.php',
            # Ruby
            '.rb',
            # Swift
            '.swift',
            # Kotlin
            '.kt', '.kts',
            # C#
            '.cs',
            # F#
            '.fs',
            # Scala
            '.scala',
            # Dart
            '.dart',
            # TypeScript
            '.ts', '.tsx',
            # CoffeeScript
            '.coffee',
            # Lua
            '.lua',
            # Shell
            '.sh', '.bash', '.zsh',
            # PowerShell
            '.ps1',
            # Batch
            '.bat', '.cmd',
            # SQL
            '.sql',
            # Database
            '.db', '.sqlite', '.sqlite3',
            # Markup
            '.md', '.rst', '.txt',
            # Config
            '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf',
            # Other
            '.exe', '.dll', '.so', '.dylib'
        }

        # Check for source files
        for file in os.listdir(project_path):
            if any(file.endswith(ext) for ext in source_extensions):
                return True

        # Check for common project directories
        project_dirs = [
            'src', 'source', 'app', 'lib', 'libs', 'bin', 'dist', 'build',
            'public', 'static', 'assets', 'resources', 'tests', 'test',
            'docs', 'examples', 'samples', 'scripts', 'tools', 'utils',
            'components', 'pages', 'views', 'controllers', 'models',
            'templates', 'styles', 'themes', 'config', 'conf', 'settings',
            'migrations', 'seeds', 'fixtures', 'data', 'content'
        ]

        # Check for project directories
        for dir_name in project_dirs:
            if os.path.isdir(os.path.join(project_path, dir_name)):
                return True

        return False
    
    def load_projects(self):
        # Clear existing projects
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get projects directory from settings
        base_dir = self.settings.value("projects_directory", "C:\\code")
        if not os.path.exists(base_dir):
            error_label = QLabel(f"Error: {base_dir} directory not found")
            error_label.setStyleSheet("color: red;")
            self.grid_layout.addWidget(error_label, 0, 0)
            return
        
        row = 0
        col = 0
        max_cols = 4  # Increased number of columns since cards are smaller
        
        for project_name in os.listdir(base_dir):
            project_path = os.path.join(base_dir, project_name)
            if os.path.isdir(project_path) and self.is_valid_project(project_path):
                # Create project card
                card = ProjectCard(project_name, project_path, self)
                
                # Set alternating background colors
                if (row + col) % 2 == 0:
                    card.setStyleSheet("""
                        QFrame {
                            background-color: #f0f0f0;
                            border-radius: 8px;
                        }
                        QFrame:hover {
                            background-color: #e0e0e0;
                        }
                    """)
                else:
                    card.setStyleSheet("""
                        QFrame {
                            background-color: #ffffff;
                            border-radius: 8px;
                        }
                        QFrame:hover {
                            background-color: #f5f5f5;
                        }
                    """)
                
                # Add card to grid
                self.grid_layout.addWidget(card, row, col)
                
                # Update position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
    
    def launch_project(self, project_path):
        # Check for common project files
        if os.path.exists(os.path.join(project_path, "package.json")):
            # Node.js project - show launch dialog
            dialog = NodeLaunchDialog(project_path, self)
            dialog.exec()
        elif os.path.exists(os.path.join(project_path, "requirements.txt")):
            # Python project
            main_py = self.find_main_python_file(project_path)
            if main_py:
                subprocess.Popen(["python", main_py], cwd=project_path, shell=True)
        else:
            # Try to find any Python file
            main_py = self.find_main_python_file(project_path)
            if main_py:
                subprocess.Popen(["python", main_py], cwd=project_path, shell=True)
    
    def find_main_python_file(self, project_path):
        # Look for common Python entry points
        common_names = ["main.py", "app.py", "run.py", "start.py"]
        for name in common_names:
            if os.path.exists(os.path.join(project_path, name)):
                return name
        
        # If no common name found, look for any Python file
        for file in os.listdir(project_path):
            if file.endswith(".py"):
                return file
        return None

def main():
    app = QApplication(sys.argv)
    window = ProjectMenu()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
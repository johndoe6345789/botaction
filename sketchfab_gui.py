"""
Sketchfab Model Fetcher - PyQt6 GUI

A graphical interface for fetching and analyzing Sketchfab 3D models.
"""

import sys
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QFormLayout,
    QProgressBar, QFileDialog, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QSplitter, QMessageBox, QStatusBar, QFrame, QScrollArea, QMenu,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPalette, QColor, QAction, QClipboard

from sketchfab_fetcher import SketchfabFetcher


class FetchWorker(QThread):
    """Background worker for fetching model data."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.fetcher = SketchfabFetcher()

    def run(self):
        try:
            self.progress.emit("Extracting model ID...")
            model_id = self.fetcher.extract_model_id(self.url)
            if not model_id:
                self.error.emit("Could not extract model ID from URL")
                return

            self.progress.emit("Fetching API data...")
            result = {
                'url': self.url,
                'model_id': model_id,
                'api_data': None,
                'embed_config': None,
                'encryption_info': None,
            }

            try:
                result['api_data'] = self.fetcher.fetch_model_api(model_id)
            except Exception as e:
                self.progress.emit(f"API fetch failed: {e}")

            self.progress.emit("Fetching embed config...")
            try:
                result['embed_config'] = self.fetcher.fetch_embed_config(model_id)
            except Exception as e:
                self.progress.emit(f"Embed config failed: {e}")

            self.progress.emit("Extracting encryption info...")
            try:
                result['encryption_info'] = self.fetcher.get_encryption_info(model_id)
            except Exception as e:
                self.progress.emit(f"Encryption info failed: {e}")

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    """Background worker for downloading files."""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str, int)  # message, percentage

    def __init__(self, model_id: str, output_dir: str):
        super().__init__()
        self.model_id = model_id
        self.output_dir = output_dir
        self.fetcher = SketchfabFetcher()

    def run(self):
        try:
            self.progress.emit("Getting file configuration...", 10)
            downloaded = {}

            config = self.fetcher.fetch_embed_config(self.model_id)
            if not config or 'files' not in config:
                self.error.emit("Could not get file configuration")
                return

            output_path = Path(self.output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files = config.get('files', [])
            total_files = len(files) + 1  # +1 for thumbnail

            for i, file_info in enumerate(files):
                file_uid = file_info.get('uid', 'unknown')
                binz_url = file_info.get('osgjsUrl')

                if binz_url:
                    self.progress.emit(f"Downloading model file {i+1}...", int((i+1) / total_files * 80))
                    try:
                        response = self.fetcher.session.get(binz_url)
                        if response.status_code == 200:
                            filename = f"{self.model_id}_{file_uid}.binz"
                            filepath = output_path / filename
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            downloaded['binz'] = str(filepath)

                            # Save params
                            params = file_info.get('p', [])
                            if params:
                                params_file = output_path / f"{self.model_id}_{file_uid}_params.json"
                                with open(params_file, 'w') as f:
                                    json.dump(params, f, indent=2)
                                downloaded['params'] = str(params_file)
                    except Exception as e:
                        self.progress.emit(f"Failed to download: {e}", 0)

            # Download thumbnail
            self.progress.emit("Downloading thumbnail...", 90)
            try:
                api_data = self.fetcher.fetch_model_api(self.model_id)
                if api_data:
                    thumbnails = api_data.get('thumbnails', {}).get('images', [])
                    if thumbnails:
                        largest = max(thumbnails, key=lambda x: x.get('width', 0))
                        thumb_url = largest.get('url')
                        if thumb_url:
                            response = self.fetcher.session.get(thumb_url)
                            if response.status_code == 200:
                                ext = thumb_url.split('.')[-1].split('?')[0]
                                thumb_path = output_path / f"{self.model_id}_thumbnail.{ext}"
                                with open(thumb_path, 'wb') as f:
                                    f.write(response.content)
                                downloaded['thumbnail'] = str(thumb_path)
            except:
                pass

            self.progress.emit("Download complete!", 100)
            self.finished.emit(downloaded)

        except Exception as e:
            self.error.emit(str(e))


class CopyableTreeWidget(QTreeWidget):
    """Tree widget with copy functionality via double-click and right-click menu."""

    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.itemDoubleClicked.connect(self.copy_item_value)

        # Make items editable for selection/copy
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def show_context_menu(self, position):
        """Show right-click context menu."""
        item = self.itemAt(position)
        if not item:
            return

        menu = QMenu(self)

        # Copy value action
        copy_value_action = QAction("Copy Value", self)
        copy_value_action.triggered.connect(lambda: self.copy_text(item.text(1)))
        menu.addAction(copy_value_action)

        # Copy property name action
        copy_name_action = QAction("Copy Property Name", self)
        copy_name_action.triggered.connect(lambda: self.copy_text(item.text(0)))
        menu.addAction(copy_name_action)

        # Copy both action
        copy_both_action = QAction("Copy Both (Name: Value)", self)
        copy_both_action.triggered.connect(
            lambda: self.copy_text(f"{item.text(0)}: {item.text(1)}")
        )
        menu.addAction(copy_both_action)

        menu.addSeparator()

        # Copy all children values
        if item.childCount() > 0:
            copy_all_action = QAction("Copy All Child Values", self)
            copy_all_action.triggered.connect(lambda: self.copy_all_children(item))
            menu.addAction(copy_all_action)

        menu.exec(self.mapToGlobal(position))

    def copy_item_value(self, item, column):
        """Copy item value on double-click."""
        text = item.text(column)
        if text:
            self.copy_text(text)
            # Show feedback in status bar if we can find it
            main_window = self.window()
            if hasattr(main_window, 'status_bar'):
                main_window.status_bar.showMessage(f"Copied: {text[:50]}{'...' if len(text) > 50 else ''}", 2000)

    def copy_text(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def copy_all_children(self, item):
        """Copy all child item values."""
        lines = []
        for i in range(item.childCount()):
            child = item.child(i)
            lines.append(f"{child.text(0)}: {child.text(1)}")
        self.copy_text("\n".join(lines))


class CopyableLabel(QLabel):
    """Label that can be copied via double-click or right-click."""

    def __init__(self, text: str = "-"):
        super().__init__(text)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Show right-click context menu."""
        menu = QMenu(self)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_text)
        menu.addAction(copy_action)

        select_all_action = QAction("Select All", self)
        select_all_action.triggered.connect(self.select_all)
        menu.addAction(select_all_action)

        menu.exec(self.mapToGlobal(position))

    def copy_text(self):
        """Copy label text to clipboard."""
        clipboard = QApplication.clipboard()
        selected = self.selectedText()
        clipboard.setText(selected if selected else self.text())

    def select_all(self):
        """Select all text."""
        self.setSelection(0, len(self.text()))

    def mouseDoubleClickEvent(self, event):
        """Select all on double-click."""
        self.setSelection(0, len(self.text()))
        super().mouseDoubleClickEvent(event)


class ThumbnailLabel(QLabel):
    """Custom label for displaying thumbnails."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 150)
        self.setMaximumSize(400, 300)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)
        self.setText("No thumbnail")

    def set_image_from_url(self, url: str, session):
        """Load image from URL."""
        try:
            response = session.get(url)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                scaled = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
        except:
            self.setText("Failed to load")


class ModelInfoPanel(QGroupBox):
    """Panel displaying model information."""

    def __init__(self):
        super().__init__("Model Information")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        layout.setSpacing(8)

        self.name_label = CopyableLabel("-")
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("", 12, QFont.Weight.Bold))

        self.author_label = CopyableLabel("-")
        self.views_label = CopyableLabel("-")
        self.likes_label = CopyableLabel("-")
        self.faces_label = CopyableLabel("-")
        self.vertices_label = CopyableLabel("-")
        self.downloadable_label = CopyableLabel("-")
        self.license_label = CopyableLabel("-")

        layout.addRow("Name:", self.name_label)
        layout.addRow("Author:", self.author_label)
        layout.addRow("Views:", self.views_label)
        layout.addRow("Likes:", self.likes_label)
        layout.addRow("Faces:", self.faces_label)
        layout.addRow("Vertices:", self.vertices_label)
        layout.addRow("Downloadable:", self.downloadable_label)
        layout.addRow("License:", self.license_label)

        self.setLayout(layout)

    def update_info(self, api_data: Dict[str, Any], embed_config: Dict[str, Any] = None):
        """Update the panel with model data."""
        if not api_data:
            return

        self.name_label.setText(api_data.get('name', '-'))
        self.author_label.setText(api_data.get('user', {}).get('username', '-'))
        self.views_label.setText(f"{api_data.get('viewCount', 0):,}")
        self.likes_label.setText(f"{api_data.get('likeCount', 0):,}")

        # Get face/vertex count from embed config if available
        if embed_config:
            self.faces_label.setText(f"{embed_config.get('faceCount', 0):,}")
            self.vertices_label.setText(f"{embed_config.get('vertexCount', 0):,}")

        downloadable = api_data.get('isDownloadable', False)
        self.downloadable_label.setText("Yes" if downloadable else "No")
        self.downloadable_label.setStyleSheet(
            "color: #4CAF50;" if downloadable else "color: #f44336;"
        )

        license_info = api_data.get('license', {})
        if license_info:
            self.license_label.setText(license_info.get('label', 'Unknown'))
        else:
            self.license_label.setText("Not specified")

    def clear(self):
        """Clear all fields."""
        for label in [self.name_label, self.author_label, self.views_label,
                      self.likes_label, self.faces_label, self.vertices_label,
                      self.downloadable_label, self.license_label]:
            label.setText("-")
            label.setStyleSheet("")


class EncryptionInfoPanel(QGroupBox):
    """Panel displaying encryption information."""

    def __init__(self):
        super().__init__("Encryption Information")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tree = CopyableTreeWidget()
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setColumnWidth(0, 150)
        self.tree.setAlternatingRowColors(True)
        self.tree.setWordWrap(True)

        layout.addWidget(self.tree)
        self.setLayout(layout)

    def update_info(self, encryption_info: Dict[str, Any]):
        """Update the panel with encryption data."""
        self.tree.clear()

        if not encryption_info:
            item = QTreeWidgetItem(["No encryption info", ""])
            self.tree.addTopLevelItem(item)
            return

        for file_data in encryption_info.get('files', []):
            file_uid = file_data.get('uid', 'unknown')
            file_item = QTreeWidgetItem([f"File: {file_uid}", ""])

            # Add file properties - full values, no ellipsis
            QTreeWidgetItem(file_item, ["UID", file_uid])
            QTreeWidgetItem(file_item, ["Encrypted", str(file_data.get('encrypted', False))])
            QTreeWidgetItem(file_item, ["Model Size", f"{file_data.get('model_size', 0):,} bytes"])
            QTreeWidgetItem(file_item, ["OSGJS Size", f"{file_data.get('osgjs_size', 0):,} bytes"])
            QTreeWidgetItem(file_item, ["URL", file_data.get('url', '-')])

            if file_data.get('key_material'):
                km = file_data['key_material']
                key_item = QTreeWidgetItem(file_item, ["Key Material", ""])
                QTreeWidgetItem(key_item, ["Length", f"{km.get('raw_length', 0)} bytes"])
                QTreeWidgetItem(key_item, ["Key (32 bytes)", km.get('potential_key', '-')])
                QTreeWidgetItem(key_item, ["IV (16 bytes)", km.get('potential_iv', '-')])
                key_item.setExpanded(True)

            self.tree.addTopLevelItem(file_item)
            file_item.setExpanded(True)

        # Resize columns to fit content
        self.tree.resizeColumnToContents(0)

    def clear(self):
        """Clear the tree."""
        self.tree.clear()


class FileListPanel(QGroupBox):
    """Panel displaying file URLs and download options."""

    def __init__(self):
        super().__init__("Files")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tree = CopyableTreeWidget()
        self.tree.setHeaderLabels(["Type", "URL / Info"])
        self.tree.setColumnWidth(0, 120)
        self.tree.setWordWrap(True)

        layout.addWidget(self.tree)
        self.setLayout(layout)

    def update_files(self, embed_config: Dict[str, Any]):
        """Update file list from embed config."""
        self.tree.clear()

        if not embed_config or 'files' not in embed_config:
            return

        for file_info in embed_config.get('files', []):
            file_item = QTreeWidgetItem([
                "Model File",
                file_info.get('osgjsUrl', '-')
            ])

            QTreeWidgetItem(file_item, ["UID", file_info.get('uid', '-')])
            QTreeWidgetItem(file_item, ["Model Size", f"{file_info.get('modelSize', 0):,} bytes"])
            QTreeWidgetItem(file_item, ["OSGJS Size", f"{file_info.get('osgjsSize', 0):,} bytes"])
            QTreeWidgetItem(file_item, ["Wireframe Size", f"{file_info.get('wireframeSize', 0):,} bytes"])

            self.tree.addTopLevelItem(file_item)
            file_item.setExpanded(True)

        # Add thumbnails
        thumbnails = embed_config.get('thumbnails', {}).get('images', [])
        if thumbnails:
            thumb_parent = QTreeWidgetItem(["Thumbnails", f"{len(thumbnails)} available"])
            for thumb in thumbnails:
                QTreeWidgetItem(thumb_parent, [
                    f"{thumb.get('width')}x{thumb.get('height')}",
                    thumb.get('url', '-')
                ])
            self.tree.addTopLevelItem(thumb_parent)

        # Resize columns to fit content
        self.tree.resizeColumnToContents(0)

    def clear(self):
        """Clear the tree."""
        self.tree.clear()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.fetcher = SketchfabFetcher()
        self.current_result = None
        self.fetch_worker = None
        self.download_worker = None

        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        self.setWindowTitle("Sketchfab Model Fetcher")
        self.setMinimumSize(900, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # URL input section
        url_group = QGroupBox("Model URL")
        url_layout = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://sketchfab.com/3d-models/model-name-abc123...")
        self.url_input.returnPressed.connect(self.fetch_model)

        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setFixedWidth(100)
        self.fetch_btn.clicked.connect(self.fetch_model)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.fetch_btn)
        url_group.setLayout(url_layout)
        main_layout.addWidget(url_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - thumbnail and info
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.thumbnail = ThumbnailLabel()
        left_layout.addWidget(self.thumbnail)

        self.info_panel = ModelInfoPanel()
        left_layout.addWidget(self.info_panel)

        # Download section
        download_group = QGroupBox("Download")
        download_layout = QVBoxLayout()

        dir_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText(str(Path.cwd() / "downloads"))
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.output_dir)
        dir_layout.addWidget(self.browse_btn)

        self.download_btn = QPushButton("Download Files")
        self.download_btn.clicked.connect(self.download_files)
        self.download_btn.setEnabled(False)

        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)

        download_layout.addLayout(dir_layout)
        download_layout.addWidget(self.download_btn)
        download_layout.addWidget(self.download_progress)
        download_group.setLayout(download_layout)
        left_layout.addWidget(download_group)

        left_layout.addStretch()
        splitter.addWidget(left_panel)

        # Right panel - tabs
        self.tabs = QTabWidget()

        # Encryption tab
        self.encryption_panel = EncryptionInfoPanel()
        self.tabs.addTab(self.encryption_panel, "Encryption")

        # Files tab
        self.files_panel = FileListPanel()
        self.tabs.addTab(self.files_panel, "Files")

        # Raw JSON tab
        self.json_view = QTextEdit()
        self.json_view.setReadOnly(True)
        self.json_view.setFont(QFont("Monospace", 9))
        self.tabs.addTab(self.json_view, "Raw JSON")

        # Description tab
        self.description_view = QTextEdit()
        self.description_view.setReadOnly(True)
        self.tabs.addTab(self.description_view, "Description")

        splitter.addWidget(self.tabs)
        splitter.setSizes([350, 550])

        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def setup_style(self):
        """Apply dark theme styling."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8c;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QTreeWidget {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::item:hover {
                background-color: #2a2a2a;
            }
            QHeaderView::section {
                background-color: #333;
                color: #e0e0e0;
                padding: 4px;
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #333;
                color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0e639c;
            }
            QTabBar::tab:hover:!selected {
                background-color: #444;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                background-color: #2a2a2a;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
                border-radius: 3px;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QSplitter::handle {
                background-color: #444;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
            QMenu {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QMenu::separator {
                height: 1px;
                background-color: #444;
                margin: 4px 0;
            }
        """)

    def fetch_model(self):
        """Start fetching model data."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a model URL")
            return

        # Clear previous data
        self.clear_all()

        # Disable UI
        self.fetch_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Start worker
        self.fetch_worker = FetchWorker(url)
        self.fetch_worker.finished.connect(self.on_fetch_complete)
        self.fetch_worker.error.connect(self.on_fetch_error)
        self.fetch_worker.progress.connect(self.on_fetch_progress)
        self.fetch_worker.start()

    def on_fetch_progress(self, message: str):
        """Handle fetch progress updates."""
        self.status_bar.showMessage(message)

    def on_fetch_complete(self, result: Dict[str, Any]):
        """Handle fetch completion."""
        self.current_result = result

        # Update UI
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)

        # Update panels
        api_data = result.get('api_data', {})
        embed_config = result.get('embed_config', {})

        self.info_panel.update_info(api_data, embed_config)
        self.encryption_panel.update_info(result.get('encryption_info'))
        self.files_panel.update_files(embed_config)

        # Load thumbnail
        if api_data:
            thumbnails = api_data.get('thumbnails', {}).get('images', [])
            if thumbnails:
                largest = max(thumbnails, key=lambda x: x.get('width', 0))
                self.thumbnail.set_image_from_url(
                    largest.get('url', ''),
                    self.fetcher.session
                )

        # Update description
        if api_data:
            desc = api_data.get('description', 'No description available')
            self.description_view.setPlainText(desc)

        # Update JSON view
        self.json_view.setPlainText(json.dumps(result, indent=2, default=str))

        self.status_bar.showMessage(f"Fetched: {api_data.get('name', 'Unknown')}")

    def on_fetch_error(self, error: str):
        """Handle fetch error."""
        self.fetch_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Error: {error}")
        QMessageBox.critical(self, "Fetch Error", error)

    def browse_directory(self):
        """Open directory browser."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory",
            self.output_dir.text()
        )
        if directory:
            self.output_dir.setText(directory)

    def download_files(self):
        """Start downloading files."""
        if not self.current_result:
            return

        model_id = self.current_result.get('model_id')
        if not model_id:
            QMessageBox.warning(self, "Error", "No model ID available")
            return

        output_dir = self.output_dir.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Error", "Please select an output directory")
            return

        # Disable UI
        self.download_btn.setEnabled(False)
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)

        # Start worker
        self.download_worker = DownloadWorker(model_id, output_dir)
        self.download_worker.finished.connect(self.on_download_complete)
        self.download_worker.error.connect(self.on_download_error)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.start()

    def on_download_progress(self, message: str, percent: int):
        """Handle download progress."""
        self.status_bar.showMessage(message)
        self.download_progress.setValue(percent)

    def on_download_complete(self, downloaded: Dict[str, str]):
        """Handle download completion."""
        self.download_btn.setEnabled(True)
        self.download_progress.setVisible(False)

        files_list = "\n".join(f"- {k}: {v}" for k, v in downloaded.items())
        self.status_bar.showMessage(f"Downloaded {len(downloaded)} files")

        QMessageBox.information(
            self, "Download Complete",
            f"Downloaded files:\n{files_list}"
        )

    def on_download_error(self, error: str):
        """Handle download error."""
        self.download_btn.setEnabled(True)
        self.download_progress.setVisible(False)
        self.status_bar.showMessage(f"Download error: {error}")
        QMessageBox.critical(self, "Download Error", error)

    def clear_all(self):
        """Clear all panels."""
        self.current_result = None
        self.thumbnail.clear()
        self.thumbnail.setText("No thumbnail")
        self.info_panel.clear()
        self.encryption_panel.clear()
        self.files_panel.clear()
        self.json_view.clear()
        self.description_view.clear()
        self.download_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Sketchfab Model Fetcher")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

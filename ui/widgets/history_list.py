from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QLabel, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
import os

class HistoryListItem(QWidget):
    def __init__(self, text, audio_path, provider, icon=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Icon based on provider
        icon_label = QLabel()
        if icon and not icon.isNull():
            icon_pixmap = icon.pixmap(24, 24)
            icon_label.setPixmap(icon_pixmap)
        layout.addWidget(icon_label)

        # Text preview
        text_label = QLabel(text)
        layout.addWidget(text_label, stretch=1)

        # Store the audio path
        self.audio_path = audio_path

class HistoryListWidget(QListWidget):
    itemClicked = pyqtSignal(QListWidgetItem)

    def __init__(self, asset_manager=None, parent=None):
        super().__init__(parent)
        self.asset_manager = asset_manager
        self.setObjectName("historyListWidget")
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlternatingRowColors(True)

    def add_item(self, text_preview, audio_path, provider):
        """Add a new history item"""
        if not os.path.exists(audio_path):
            return

        # Get provider icon if asset_manager is available
        icon = None
        if self.asset_manager:
            icon = self.asset_manager.get_provider_icon(provider)
        
        item_widget = HistoryListItem(text_preview, audio_path, provider, icon)
        list_item = QListWidgetItem(self)
        list_item.setSizeHint(item_widget.sizeHint())
        list_item.setData(Qt.ItemDataRole.UserRole, audio_path)
        
        self.addItem(list_item)
        self.setItemWidget(list_item, item_widget)
        self.scrollToItem(list_item)

    def clear_history(self):
        """Clear all history items"""
        self.clear()

    def get_history_items(self):
        """Get all audio paths from history"""
        items = []
        for i in range(self.count()):
            item = self.item(i)
            audio_path = item.data(Qt.ItemDataRole.UserRole)
            items.append(audio_path)
        return items

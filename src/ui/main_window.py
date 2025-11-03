#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Main Window
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Import Tabs
try:
    from src.ui.stream_tab import StreamTab
    from src.ui.settings_tab import SettingsTab
    from src.ui.help_tab import HelpTab
    from src.core.stream_manager import StreamManager
except ModuleNotFoundError:
    from stream_tab import StreamTab
    from settings_tab import SettingsTab
    from help_tab import HelpTab
    from ..core.stream_manager import StreamManager


class MainWindow(QMainWindow):
    """
    Hauptfenster von TUXRTMPilot.

    Phase 4: StreamManager-Integration
    - Stream-Tab: Vollständig funktionsfähig
    - Settings-Tab: Einstellungen (Phase 4+)
    """

    def __init__(self):
        """Initialisiert das Hauptfenster."""
        super().__init__()

        self.setWindowTitle("TUXRTMPilot - Multi-Platform RTMP Streaming")
        self.setMinimumSize(1200, 700)

        # Dark Mode Style (KDE Breeze Dark)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #3c3c3c;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #4a4a4a;
            }
            QStatusBar {
                background-color: #3c3c3c;
                color: #ffffff;
                border-top: 1px solid #555555;
            }
        """)

        # StreamManager initialisieren
        self.stream_manager = StreamManager()

        # Central Widget mit Tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Tab 1: Stream
        self.stream_tab = StreamTab(self.stream_manager)
        self.tabs.addTab(self.stream_tab, "📡 Stream")

        # Tab 2: Einstellungen (Phase 4+)
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "⚙️ Einstellungen")

        # Tab 3: Hilfe
        self.help_tab = HelpTab()
        self.tabs.addTab(self.help_tab, "❓ Hilfe")

        self.setCentralWidget(self.tabs)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("✅ TUXRTMPilot bereit")

        # StreamManager-Signals mit Status Bar verbinden
        self.stream_manager.status_signal.connect(self.update_status)
        self.stream_manager.error_signal.connect(self.show_error)

        print("✅ MainWindow mit StreamManager initialisiert")

    def update_status(self, message: str) -> None:
        """
        Aktualisiert Status-Bar.

        Args:
            message: Status-Nachricht
        """
        self.status_bar.showMessage(message)

    def show_error(self, error: str) -> None:
        """
        Zeigt Fehler in Status-Bar.

        Args:
            error: Fehler-Nachricht
        """
        self.status_bar.showMessage(error)
        # TODO: QMessageBox für kritische Fehler (Phase 5)

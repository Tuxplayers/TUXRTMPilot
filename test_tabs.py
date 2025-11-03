#!/usr/bin/env python3
"""Minimaler Test für QTabWidget"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QWidget, QVBoxLayout, QLabel
)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Test")
        self.setMinimumSize(800, 600)

        # Tabs erstellen
        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        # Tab 1
        tab1 = QWidget()
        layout1 = QVBoxLayout()
        layout1.addWidget(QLabel("Dies ist Tab 1"))
        tab1.setLayout(layout1)
        tabs.addTab(tab1, "Tab 1")

        # Tab 2
        tab2 = QWidget()
        layout2 = QVBoxLayout()
        layout2.addWidget(QLabel("Dies ist Tab 2"))
        tab2.setLayout(layout2)
        tabs.addTab(tab2, "Tab 2")

        # Tab 3
        tab3 = QWidget()
        layout3 = QVBoxLayout()
        layout3.addWidget(QLabel("Dies ist Tab 3"))
        tab3.setLayout(layout3)
        tabs.addTab(tab3, "Tab 3")

        self.setCentralWidget(tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

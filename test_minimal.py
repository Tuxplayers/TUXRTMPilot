#!/usr/bin/env python3
"""Minimaler Test - NUR ein Tab, NUR ein Label"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QWidget, QLabel, QVBoxLayout
)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MINIMAL TEST")
        self.setMinimumSize(800, 600)

        # Tab Widget
        tabs = QTabWidget()

        # Nur EIN Tab mit nur EINEM Label
        tab1 = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Dies ist NUR EIN LABEL in NUR EINEM TAB"))
        tab1.setLayout(layout)
        tabs.addTab(tab1, "Test Tab")

        self.setCentralWidget(tabs)
        print("✅ Fenster erstellt - NUR 1 Tab, NUR 1 Label")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("✅ App gestartet")
    sys.exit(app.exec())

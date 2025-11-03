#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Settings Tab
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QCheckBox, QSpinBox, QComboBox, QPushButton, QLineEdit,
    QFileDialog
)
from PyQt6.QtCore import Qt

try:
    from src.utils.config import get_config
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.utils.config import get_config


class SettingsTab(QWidget):
    """
    Einstellungs-Tab für TUXRTMPilot.

    Erweiterte Einstellungen für Aufnahme, Performance, etc.
    """

    def __init__(self):
        """Initialisiert Settings-Tab."""
        super().__init__()

        self.config = get_config()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Aufnahme-Einstellungen
        recording_group = self._create_recording_settings()
        main_layout.addWidget(recording_group)

        # Performance-Einstellungen
        performance_group = self._create_performance_settings()
        main_layout.addWidget(performance_group)

        # Erweiterte Einstellungen
        advanced_group = self._create_advanced_settings()
        main_layout.addWidget(advanced_group)

        main_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("💾 Einstellungen speichern")
        self.save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("🔄 Zurücksetzen")
        self.reset_button.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_button)

        main_layout.addLayout(button_layout)

        # Style anwenden
        self._apply_style()

        # Einstellungen laden
        self._load_settings()

        print("✅ SettingsTab initialisiert")

    def _create_recording_settings(self) -> QGroupBox:
        """Erstellt Aufnahme-Einstellungen."""
        group = QGroupBox("📹 Aufnahme-Einstellungen")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Aufnahme-Pfad
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Aufnahme-Pfad:"))

        self.recording_path = QLineEdit()
        self.recording_path.setText(self.config.get('recording_path', '~/Videos'))
        path_layout.addWidget(self.recording_path)

        browse_button = QPushButton("📁 Durchsuchen")
        browse_button.clicked.connect(self._browse_recording_path)
        path_layout.addWidget(browse_button)

        layout.addLayout(path_layout)

        # Aufnahme-Format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Aufnahme-Format:"))

        self.recording_format = QComboBox()
        self.recording_format.addItems(['MP4 (H.264)', 'MKV (H.264)', 'FLV'])
        format_layout.addWidget(self.recording_format)

        layout.addLayout(format_layout)

        # Auto-Aufnahme
        self.auto_record = QCheckBox("📼 Automatisch bei Stream-Start aufnehmen")
        layout.addWidget(self.auto_record)

        return group

    def _create_performance_settings(self) -> QGroupBox:
        """Erstellt Performance-Einstellungen."""
        group = QGroupBox("⚡ Performance-Einstellungen")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Encoder-Preset
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("x264 Encoder-Preset:"))

        self.encoder_preset = QComboBox()
        self.encoder_preset.addItems([
            'ultrafast (Niedrigste CPU)',
            'superfast (Empfohlen)',
            'veryfast',
            'faster',
            'fast',
            'medium (Standard)',
            'slow (Beste Qualität)'
        ])
        self.encoder_preset.setCurrentIndex(1)  # superfast
        preset_layout.addWidget(self.encoder_preset)

        layout.addLayout(preset_layout)

        # Thread-Count
        thread_layout = QHBoxLayout()
        thread_layout.addWidget(QLabel("Encoder-Threads:"))

        self.encoder_threads = QSpinBox()
        self.encoder_threads.setRange(0, 16)
        self.encoder_threads.setValue(0)
        self.encoder_threads.setSpecialValueText("Auto")
        thread_layout.addWidget(self.encoder_threads)

        layout.addLayout(thread_layout)

        # Hardware-Encoding
        self.hardware_encoding = QCheckBox("🎮 Hardware-Encoding nutzen (wenn verfügbar)")
        self.hardware_encoding.setEnabled(False)  # Noch nicht implementiert
        layout.addWidget(self.hardware_encoding)

        return group

    def _create_advanced_settings(self) -> QGroupBox:
        """Erstellt erweiterte Einstellungen."""
        group = QGroupBox("🔧 Erweiterte Einstellungen")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Keyframe-Intervall
        keyframe_layout = QHBoxLayout()
        keyframe_layout.addWidget(QLabel("Keyframe-Intervall (Sekunden):"))

        self.keyframe_interval = QSpinBox()
        self.keyframe_interval.setRange(1, 10)
        self.keyframe_interval.setValue(2)
        keyframe_layout.addWidget(self.keyframe_interval)

        layout.addLayout(keyframe_layout)

        # Audio-Bitrate
        audio_layout = QHBoxLayout()
        audio_layout.addWidget(QLabel("Audio-Bitrate:"))

        self.audio_bitrate = QComboBox()
        self.audio_bitrate.addItems(['96 kbps', '128 kbps', '192 kbps', '256 kbps'])
        self.audio_bitrate.setCurrentText('128 kbps')
        audio_layout.addWidget(self.audio_bitrate)

        layout.addLayout(audio_layout)

        # Low-Latency
        self.low_latency = QCheckBox("⚡ Low-Latency-Modus (zerolatency tune)")
        self.low_latency.setChecked(True)
        layout.addWidget(self.low_latency)

        # Verbose Logging
        self.verbose_logging = QCheckBox("📝 Ausführliches Logging (GStreamer Debug)")
        layout.addWidget(self.verbose_logging)

        return group

    def _browse_recording_path(self) -> None:
        """Öffnet Dialog zur Auswahl des Aufnahme-Pfads."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Aufnahme-Pfad wählen",
            self.recording_path.text()
        )
        if path:
            self.recording_path.setText(path)

    def _load_settings(self) -> None:
        """Lädt gespeicherte Einstellungen."""
        # Aufnahme
        self.recording_path.setText(
            self.config.get('recording_path', '~/Videos')
        )
        recording_format = self.config.get('recording_format', 'MP4 (H.264)')
        self.recording_format.setCurrentText(recording_format)

        self.auto_record.setChecked(
            self.config.get('auto_record', False)
        )

        # Performance
        encoder_preset = self.config.get('encoder_preset', 'superfast (Empfohlen)')
        self.encoder_preset.setCurrentText(encoder_preset)

        self.encoder_threads.setValue(
            self.config.get('encoder_threads', 0)
        )

        # Erweitert
        self.keyframe_interval.setValue(
            self.config.get('keyframe_interval', 2)
        )

        audio_bitrate = self.config.get('audio_bitrate', '128 kbps')
        self.audio_bitrate.setCurrentText(audio_bitrate)

        self.low_latency.setChecked(
            self.config.get('low_latency', True)
        )

        self.verbose_logging.setChecked(
            self.config.get('verbose_logging', False)
        )

    def _save_settings(self) -> None:
        """Speichert Einstellungen."""
        # Aufnahme
        self.config.set('recording_path', self.recording_path.text())
        self.config.set('recording_format', self.recording_format.currentText())
        self.config.set('auto_record', self.auto_record.isChecked())

        # Performance
        self.config.set('encoder_preset', self.encoder_preset.currentText())
        self.config.set('encoder_threads', self.encoder_threads.value())

        # Erweitert
        self.config.set('keyframe_interval', self.keyframe_interval.value())
        self.config.set('audio_bitrate', self.audio_bitrate.currentText())
        self.config.set('low_latency', self.low_latency.isChecked())
        self.config.set('verbose_logging', self.verbose_logging.isChecked())

        self.config.save_config()

        print("✅ Einstellungen gespeichert")

    def _reset_settings(self) -> None:
        """Setzt Einstellungen auf Standard zurück."""
        self.recording_path.setText('~/Videos')
        self.recording_format.setCurrentText('MP4 (H.264)')
        self.auto_record.setChecked(False)
        self.encoder_preset.setCurrentText('superfast (Empfohlen)')
        self.encoder_threads.setValue(0)
        self.keyframe_interval.setValue(2)
        self.audio_bitrate.setCurrentText('128 kbps')
        self.low_latency.setChecked(True)
        self.verbose_logging.setChecked(False)

        print("✅ Einstellungen zurückgesetzt")

    def _apply_style(self) -> None:
        """Wendet Dark Mode Style an."""
        self.setStyleSheet("""
            QGroupBox {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 2px 10px;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QComboBox, QLineEdit, QSpinBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084e0;
            }
        """)

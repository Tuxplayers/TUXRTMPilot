#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Stream Tab
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QLineEdit, QPushButton, QSlider,
    QCheckBox, QTextEdit, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor

# Import Manager
try:
    from src.core.device_manager import DeviceManager
    from src.utils.config import get_config
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.core.device_manager import DeviceManager
    from src.utils.config import get_config


# Stream-Services mit RTMP-URLs
STREAM_SERVICES = {
    "Benutzerdefiniert": "",
    "YouTube": "rtmp://a.rtmp.youtube.com/live2",
    "Twitch": "rtmp://live.twitch.tv/app",
    "TikTok": "rtmp://push.tiktokapis.com/v2/live",
    "Facebook Live": "rtmps://live-api-s.facebook.com:443/rtmp",
    "Kick": "rtmp://fra.contribute.live-video.net/app",
    "Restream.io": "rtmp://live.restream.io/live",
}


class StreamTab(QWidget):
    """
    Stream-Tab für TUXRTMPilot.

    Enthält:
    - Geräteauswahl (Video/Audio)
    - Stream-Konfiguration (Plattform, URL, Key)
    - Preview-Bereich
    - Stream-Controls (Start/Stop)
    - Log-Ausgabe

    Phase 4: Mit StreamManager verbunden
    """

    def __init__(self, stream_manager):
        """
        Initialisiert Stream-Tab.

        Args:
            stream_manager: StreamManager-Instanz
        """
        super().__init__()

        # Manager
        self.stream_manager = stream_manager
        self.device_manager = DeviceManager()
        self.config = get_config()

        # State
        self.is_streaming = False
        self.is_preview_active = False

        # UI aufbauen
        self._setup_ui()
        self._apply_dark_style()
        self._load_config()
        self._connect_signals()
        self._connect_stream_manager()

        print("✅ StreamTab mit StreamManager initialisiert")

    def _setup_ui(self) -> None:
        """Erstellt die UI-Komponenten."""
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # === LINKE SEITE: Controls ===
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(400)

        # 1. Geräteauswahl
        device_group = self._create_device_group()
        left_layout.addWidget(device_group)

        # 2. Stream-Konfiguration
        stream_group = self._create_stream_config_group()
        left_layout.addWidget(stream_group)

        # 3. Stream-Controls
        controls_group = self._create_controls_group()
        left_layout.addWidget(controls_group)

        left_layout.addStretch()

        # === RECHTE SEITE: Preview & Log ===
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Preview
        preview_group = self._create_preview_group()
        right_layout.addWidget(preview_group, stretch=3)

        # Log
        log_group = self._create_log_group()
        right_layout.addWidget(log_group, stretch=1)

        # Layouts zusammenfügen
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

    def _create_device_group(self) -> QGroupBox:
        """Erstellt Geräteauswahl-Gruppe."""
        group = QGroupBox("🎥 Geräteauswahl")
        layout = QGridLayout()
        group.setLayout(layout)

        # Szenen-Schnellwahl (wie OBS)
        layout.addWidget(QLabel("⚡ Schnellwahl:"), 0, 0)
        scene_layout = QHBoxLayout()

        self.scene_webcam_btn = QPushButton("🎥 Webcam")
        self.scene_webcam_btn.setCheckable(True)
        self.scene_webcam_btn.clicked.connect(lambda: self._select_scene('webcam'))
        scene_layout.addWidget(self.scene_webcam_btn)

        self.scene_desktop_btn = QPushButton("🖥️ Desktop")
        self.scene_desktop_btn.setCheckable(True)
        self.scene_desktop_btn.clicked.connect(lambda: self._select_scene('desktop'))
        scene_layout.addWidget(self.scene_desktop_btn)

        layout.addLayout(scene_layout, 0, 1)

        # Video-Quelle (erweitert)
        layout.addWidget(QLabel("Video-Quelle:"), 1, 0)
        self.video_combo = QComboBox()
        video_sources = self.device_manager.get_video_sources()
        print(f"🔹 Lade {len(video_sources)} Video-Quellen in ComboBox:")
        for source in video_sources:
            print(f"   - {source['name']} [{source['device']}]")
            self.video_combo.addItem(source['name'], source['device'])
        layout.addWidget(self.video_combo, 1, 1)

        # Audio-Quelle
        layout.addWidget(QLabel("Audio-Quelle:"), 2, 0)
        self.audio_combo = QComboBox()
        audio_sources = self.device_manager.get_audio_sources()
        for source in audio_sources:
            self.audio_combo.addItem(source['name'], source['device'])
        layout.addWidget(self.audio_combo, 2, 1)

        # Lautstärke
        layout.addWidget(QLabel("🔊 Lautstärke:"), 3, 0)
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_label = QLabel("70%")
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout, 3, 1)

        # Mute Button
        self.mute_button = QPushButton("🔇 Mute")
        self.mute_button.setCheckable(True)
        layout.addWidget(self.mute_button, 4, 1)

        return group

    def _create_stream_config_group(self) -> QGroupBox:
        """Erstellt Stream-Konfigurations-Gruppe."""
        group = QGroupBox("📡 Stream-Konfiguration")
        layout = QGridLayout()
        group.setLayout(layout)

        # Plattform
        layout.addWidget(QLabel("Plattform:"), 0, 0)
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(STREAM_SERVICES.keys())
        layout.addWidget(self.platform_combo, 0, 1)

        # RTMP URL
        layout.addWidget(QLabel("RTMP-URL:"), 1, 0)
        self.rtmp_url_edit = QLineEdit()
        self.rtmp_url_edit.setPlaceholderText("rtmp://...")
        layout.addWidget(self.rtmp_url_edit, 1, 1)

        # Stream Key
        layout.addWidget(QLabel("Stream-Key:"), 2, 0)
        self.stream_key_edit = QLineEdit()
        self.stream_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.stream_key_edit.setPlaceholderText("••••••••••••••")
        layout.addWidget(self.stream_key_edit, 2, 1)

        # Key anzeigen Checkbox
        self.show_key_checkbox = QCheckBox("🔓 Key anzeigen")
        layout.addWidget(self.show_key_checkbox, 3, 1)

        # Quality-Einstellungen
        layout.addWidget(QLabel("Auflösung:"), 4, 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "1920x1080 (Full HD)",
            "1280x720 (HD)",
            "854x480 (SD)",
            "640x360 (Low)"
        ])
        self.resolution_combo.setCurrentText("1280x720 (HD)")
        layout.addWidget(self.resolution_combo, 4, 1)

        layout.addWidget(QLabel("Bitrate:"), 5, 0)
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "6000 kbps (Sehr hoch)",
            "4500 kbps (Hoch)",
            "2500 kbps (Mittel)",
            "1500 kbps (Niedrig)"
        ])
        self.bitrate_combo.setCurrentText("2500 kbps (Mittel)")
        layout.addWidget(self.bitrate_combo, 5, 1)

        return group

    def _create_controls_group(self) -> QGroupBox:
        """Erstellt Stream-Control-Buttons."""
        group = QGroupBox("🎬 Stream-Steuerung")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # LIVE GEHEN Button
        self.start_button = QPushButton("🔴 LIVE GEHEN")
        self.start_button.setMinimumHeight(50)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.start_button.setFont(font)
        layout.addWidget(self.start_button)

        # Stream stoppen Button
        self.stop_button = QPushButton("⏹️ Stream stoppen")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        return group

    def _create_preview_group(self) -> QGroupBox:
        """Erstellt Preview-Bereich."""
        group = QGroupBox("📺 Stream-Vorschau")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Preview-Label (für Video-Frame)
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #888888;
                border: 2px solid #555555;
                border-radius: 4px;
            }
        """)
        self.preview_label.setText("🎥 Preview inaktiv\n\nKlicke 'Preview starten' um eine Vorschau zu sehen")
        layout.addWidget(self.preview_label)

        # Preview-Button
        self.preview_button = QPushButton("▶️ Preview starten")
        layout.addWidget(self.preview_button)

        return group

    def _create_log_group(self) -> QGroupBox:
        """Erstellt Log-Bereich."""
        group = QGroupBox("📋 Log")
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Log-TextEdit
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setPlaceholderText("Ereignisse werden hier angezeigt...")
        layout.addWidget(self.log_text)

        # Initial-Log
        self.add_log("TUXRTMPilot gestartet")
        self.add_log(f"Video-Quellen: {self.video_combo.count()} erkannt")
        self.add_log(f"Audio-Quellen: {self.audio_combo.count()} erkannt")

        return group

    def _apply_dark_style(self) -> None:
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
                background: transparent;
            }
            QComboBox, QLineEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QComboBox:hover, QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            QComboBox::drop-down {
                border: none;
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
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QPushButton#start_button {
                background-color: #d32f2f;
            }
            QPushButton#start_button:hover {
                background-color: #e53935;
            }
            QSlider::groove:horizontal {
                background: #555555;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #555555;
                border-radius: 3px;
                background: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background: #0078d4;
            }
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                font-family: monospace;
            }
        """)

        # Special styling für Start-Button
        self.start_button.setObjectName("start_button")

    def _load_config(self) -> None:
        """Lädt gespeicherte Konfiguration."""
        # Video/Audio-Source aus Config
        video_device = self.config.get('video_source', 'screen')
        audio_device = self.config.get('audio_source', 'default')

        # Setze Auswahl in ComboBoxes
        for i in range(self.video_combo.count()):
            if self.video_combo.itemData(i) == video_device:
                self.video_combo.setCurrentIndex(i)
                break

        for i in range(self.audio_combo.count()):
            if self.audio_combo.itemData(i) == audio_device:
                self.audio_combo.setCurrentIndex(i)
                break

        # Plattform und URL
        platform = self.config.get('platform', 'Benutzerdefiniert')
        if platform in STREAM_SERVICES:
            self.platform_combo.setCurrentText(platform)
            self.rtmp_url_edit.setText(STREAM_SERVICES[platform])

        # Auflösung und Bitrate
        resolution = self.config.get('resolution', '1280x720')
        for i in range(self.resolution_combo.count()):
            if resolution in self.resolution_combo.itemText(i):
                self.resolution_combo.setCurrentIndex(i)
                break

        bitrate = self.config.get('bitrate', 2500)
        for i in range(self.bitrate_combo.count()):
            if str(bitrate) in self.bitrate_combo.itemText(i):
                self.bitrate_combo.setCurrentIndex(i)
                break

        self.add_log("Konfiguration geladen")

    def _connect_signals(self) -> None:
        """Verbindet Signal-Slots."""
        # Plattform-Wechsel → RTMP-URL automatisch setzen
        self.platform_combo.currentTextChanged.connect(self._on_platform_changed)

        # Key anzeigen Toggle
        self.show_key_checkbox.stateChanged.connect(self._toggle_key_visibility)

        # Lautstärke-Slider
        self.volume_slider.valueChanged.connect(self._on_volume_changed)

        # Mute-Button
        self.mute_button.toggled.connect(self._on_mute_toggled)

        # Stream-Buttons
        self.start_button.clicked.connect(self._on_start_stream)
        self.stop_button.clicked.connect(self._on_stop_stream)
        self.preview_button.clicked.connect(self._on_preview_toggle)

        # Config speichern bei Änderungen
        self.video_combo.currentIndexChanged.connect(self._save_config)
        self.audio_combo.currentIndexChanged.connect(self._save_config)
        self.platform_combo.currentIndexChanged.connect(self._save_config)
        self.resolution_combo.currentIndexChanged.connect(self._save_config)
        self.bitrate_combo.currentIndexChanged.connect(self._save_config)

    def _on_platform_changed(self, platform: str) -> None:
        """
        Wird aufgerufen wenn Plattform geändert wird.

        Setzt RTMP-URL automatisch.
        """
        if platform in STREAM_SERVICES:
            url = STREAM_SERVICES[platform]
            self.rtmp_url_edit.setText(url)

            if platform != "Benutzerdefiniert":
                self.rtmp_url_edit.setEnabled(False)
                self.add_log(f"Plattform gewechselt: {platform}")
            else:
                self.rtmp_url_edit.setEnabled(True)
                self.add_log("Benutzerdefinierte RTMP-URL")

    def _toggle_key_visibility(self, state: int) -> None:
        """Zeigt/Versteckt Stream-Key."""
        if state == Qt.CheckState.Checked.value:
            self.stream_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_checkbox.setText("🔓 Key verbergen")
        else:
            self.stream_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_checkbox.setText("🔓 Key anzeigen")

    def _on_volume_changed(self, value: int) -> None:
        """Aktualisiert Lautstärke-Label."""
        self.volume_label.setText(f"{value}%")

    def _on_mute_toggled(self, checked: bool) -> None:
        """Mute/Unmute Audio."""
        if checked:
            self.mute_button.setText("🔊 Unmute")
            self.volume_slider.setEnabled(False)
            self.add_log("Audio stummgeschaltet")
        else:
            self.mute_button.setText("🔇 Mute")
            self.volume_slider.setEnabled(True)
            self.add_log("Audio aktiviert")

    def _select_scene(self, scene_type: str) -> None:
        """
        Wählt eine Szene aus (wie OBS Scenes).

        Args:
            scene_type: 'webcam' oder 'desktop'
        """
        if scene_type == 'webcam':
            # Finde erste Webcam
            for i in range(self.video_combo.count()):
                device = self.video_combo.itemData(i)
                if device != 'screen':  # Alles außer Screen ist Webcam
                    self.video_combo.setCurrentIndex(i)
                    self.scene_webcam_btn.setChecked(True)
                    self.scene_desktop_btn.setChecked(False)
                    self.add_log("🎥 Szene: Webcam")
                    break

        elif scene_type == 'desktop':
            # Finde Screen Capture
            for i in range(self.video_combo.count()):
                device = self.video_combo.itemData(i)
                if device == 'screen':
                    self.video_combo.setCurrentIndex(i)
                    self.scene_desktop_btn.setChecked(True)
                    self.scene_webcam_btn.setChecked(False)
                    self.add_log("🖥️ Szene: Desktop")
                    break

    def _connect_stream_manager(self) -> None:
        """Verbindet StreamManager-Signals mit UI."""
        # StreamManager → UI
        self.stream_manager.status_signal.connect(self.add_log)
        self.stream_manager.error_signal.connect(self.add_log)
        self.stream_manager.state_changed_signal.connect(self._on_stream_state_changed)

        print("✅ StreamManager mit UI verbunden")

    def _on_stream_state_changed(self, state: str) -> None:
        """
        Wird aufgerufen wenn Stream-State sich ändert.

        Args:
            state: "idle", "starting", "streaming", "stopping"
        """
        if state == "streaming":
            self.is_streaming = True
        elif state == "idle":
            self.is_streaming = False

        self._update_button_states()

    def _on_start_stream(self) -> None:
        """Wird aufgerufen wenn 'LIVE GEHEN' geklickt."""
        # Validierung
        rtmp_url = self.rtmp_url_edit.text().strip()
        stream_key = self.stream_key_edit.text().strip()

        if not rtmp_url:
            self.add_log("❌ Fehler: RTMP-URL fehlt!")
            return

        if not stream_key:
            self.add_log("❌ Fehler: Stream-Key fehlt!")
            return

        # Config sammeln
        config = self._get_stream_config()

        # StreamManager starten
        self.add_log("🔴 Stream-Start angefordert...")
        success = self.stream_manager.start_stream(
            video_source=config['video_source'],
            audio_source=config['audio_source'],
            rtmp_url=config['rtmp_url'],
            stream_key=config['stream_key'],
            resolution=config['resolution'],
            bitrate=config['bitrate'],
            fps=config['fps']
        )

        if not success:
            self.add_log("❌ Stream konnte nicht gestartet werden!")

    def _on_stop_stream(self) -> None:
        """Wird aufgerufen wenn 'Stream stoppen' geklickt."""
        self.add_log("⏹️ Stream-Stop angefordert...")
        self.stream_manager.stop_stream()

    def _on_preview_toggle(self) -> None:
        """Wird aufgerufen wenn Preview-Button geklickt."""
        if not self.is_preview_active:
            self.add_log("▶️ Preview startet...")

            # Config sammeln
            config = self._get_stream_config()

            # StreamManager Preview starten
            success = self.stream_manager.start_preview(
                video_source=config['video_source'],
                resolution=config['resolution'],
                fps=config['fps']
            )

            if success:
                self.is_preview_active = True
                self.preview_button.setText("⏹️ Preview stoppen")
                self.preview_label.setText("🎥 Preview aktiv\n\n(Separates Fenster)")
            else:
                self.add_log("❌ Preview konnte nicht gestartet werden!")
        else:
            self.add_log("⏹️ Preview gestoppt")
            self.stream_manager.stop_preview()
            self.is_preview_active = False
            self.preview_button.setText("▶️ Preview starten")
            self.preview_label.setText("🎥 Preview inaktiv\n\nKlicke 'Preview starten' um eine Vorschau zu sehen")

    def _update_button_states(self) -> None:
        """Aktualisiert Button-States basierend auf Stream-Status."""
        self.start_button.setEnabled(not self.is_streaming)
        self.stop_button.setEnabled(self.is_streaming)

        if self.is_streaming:
            self.start_button.setText("🔴 LIVE")
        else:
            self.start_button.setText("🔴 LIVE GEHEN")

    def _get_stream_config(self) -> dict:
        """
        Sammelt aktuelle Stream-Konfiguration.

        Returns:
            Dict mit allen Stream-Settings
        """
        # Parse Resolution
        resolution_text = self.resolution_combo.currentText()
        resolution = resolution_text.split()[0]  # z.B. "1280x720"

        # Parse Bitrate
        bitrate_text = self.bitrate_combo.currentText()
        bitrate = int(bitrate_text.split()[0])  # z.B. "2500"

        return {
            'video_source': self.video_combo.currentData(),
            'audio_source': self.audio_combo.currentData(),
            'rtmp_url': self.rtmp_url_edit.text().strip(),
            'stream_key': self.stream_key_edit.text().strip(),
            'resolution': resolution,
            'bitrate': bitrate,
            'fps': 30,
            'volume': self.volume_slider.value() if not self.mute_button.isChecked() else 0,
        }

    def _save_config(self) -> None:
        """Speichert aktuelle Einstellungen in Config."""
        config = self._get_stream_config()

        self.config.set('video_source', config['video_source'])
        self.config.set('audio_source', config['audio_source'])
        self.config.set('platform', self.platform_combo.currentText())
        self.config.set('resolution', config['resolution'])
        self.config.set('bitrate', config['bitrate'])

        # Stream-Key NICHT in Config speichern (nur in .env)!
        # TODO: Verschlüsselte Speicherung über keyring (Phase 4)

        self.config.save_config()

    def add_log(self, message: str) -> None:
        """
        Fügt Log-Nachricht hinzu.

        Args:
            message: Log-Nachricht
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # Auto-Scroll zu letzter Zeile
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def update_preview(self, pixmap: QPixmap) -> None:
        """
        Aktualisiert Preview mit neuem Frame.

        Args:
            pixmap: Video-Frame als QPixmap
        """
        scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled)

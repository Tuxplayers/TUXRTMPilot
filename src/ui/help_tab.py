#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Help Tab
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QGroupBox
)
from PyQt6.QtCore import Qt


class HelpTab(QWidget):
    """
    Hilfe-Tab für TUXRTMPilot.

    Zeigt Informationen über das Programm, Lizenz, Autor und Anleitung.
    """

    def __init__(self):
        """Initialisiert Help-Tab."""
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Info-Bereich
        info_group = QGroupBox("ℹ️ Über TUXRTMPilot")
        info_layout = QVBoxLayout()
        info_group.setLayout(info_layout)

        # HTML-Text mit Infos
        self.info_text = QTextBrowser()
        self.info_text.setOpenExternalLinks(True)
        self.info_text.setHtml(self._get_help_html())

        info_layout.addWidget(self.info_text)
        layout.addWidget(info_group)

        # Style anpassen
        self._apply_style()

        print("✅ HelpTab initialisiert")

    def _get_help_html(self) -> str:
        """
        Erstellt HTML-Text mit Hilfe-Informationen.

        Returns:
            HTML-String
        """
        return """
        <html>
        <head>
            <style>
                body {
                    color: #ffffff;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 11pt;
                }
                h1 {
                    color: #0078d4;
                    font-size: 20pt;
                }
                h2 {
                    color: #1084e0;
                    font-size: 14pt;
                    margin-top: 20px;
                }
                h3 {
                    color: #4a9eff;
                    font-size: 12pt;
                }
                code {
                    background-color: #3c3c3c;
                    padding: 2px 5px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }
                a {
                    color: #4a9eff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
                .section {
                    margin-bottom: 20px;
                }
            </style>
        </head>
        <body>
            <h1>🐧 TUXRTMPilot</h1>
            <p><strong>Multi-Platform RTMP Streaming Tool für Linux/KDE</strong></p>

            <div class="section">
                <h2>📋 Über das Programm</h2>
                <p>
                    TUXRTMPilot ist ein benutzerfreundliches RTMP-Streaming-Tool für Linux,
                    entwickelt mit Python, PyQt6 und GStreamer. Es ermöglicht das Streaming
                    zu verschiedenen Plattformen wie YouTube, Twitch, TikTok, Facebook Live und mehr.
                </p>
                <p><strong>Features:</strong></p>
                <ul>
                    <li>📹 Screen Capture via PipeWire (Wayland/X11)</li>
                    <li>🎥 Webcam-Unterstützung (V4L2)</li>
                    <li>🎤 Audio-Mixing (Mikrofon + Desktop Audio)</li>
                    <li>📡 RTMP-Streaming zu allen gängigen Plattformen</li>
                    <li>🎬 Live-Preview (separates Fenster)</li>
                    <li>⚙️ Flexible Qualitätseinstellungen</li>
                </ul>
            </div>

            <div class="section">
                <h2>📖 Kurzanleitung</h2>

                <h3>1. Preview starten</h3>
                <p>
                    Wähle deine Video-Quelle (Webcam oder Screen Capture) und klicke auf
                    <strong>"▶️ Preview starten"</strong>. Bei Screen Capture öffnet sich
                    ein Dialog zur Auswahl des Bildschirms/Fensters.
                </p>

                <h3>2. Stream konfigurieren</h3>
                <p>
                    Wähle deine Streaming-Plattform aus der Liste und gib deinen
                    <strong>Stream-Key</strong> ein. Dieser ist in deinem Dashboard
                    der jeweiligen Plattform zu finden.
                </p>

                <h3>3. Live gehen</h3>
                <p>
                    Klicke auf <strong>"🔴 LIVE GEHEN"</strong> um den Stream zu starten.
                    Der Stream läuft parallel zur Preview.
                </p>

                <h3>4. Stream beenden</h3>
                <p>
                    Klicke auf <strong>"⏹️ Stream stoppen"</strong> um den Stream zu beenden.
                </p>
            </div>

            <div class="section">
                <h2>🔑 Stream-Keys finden</h2>
                <ul>
                    <li><strong>YouTube:</strong> YouTube Studio → Live-Streaming → Stream-Schlüssel</li>
                    <li><strong>Twitch:</strong> Creator Dashboard → Einstellungen → Stream → Primärer Stream-Schlüssel</li>
                    <li><strong>TikTok:</strong> TikTok Live Studio → Server-URL & Stream-Key</li>
                    <li><strong>Facebook:</strong> Creator Studio → Live → Stream-Key</li>
                </ul>
            </div>

            <div class="section">
                <h2>⚙️ Qualitätseinstellungen</h2>
                <p>
                    <strong>Empfohlene Einstellungen:</strong>
                </p>
                <ul>
                    <li>🎥 Full HD (1920x1080) - 4500-6000 kbps</li>
                    <li>🎥 HD (1280x720) - 2500-4500 kbps</li>
                    <li>🎥 SD (854x480) - 1500-2500 kbps</li>
                </ul>
                <p>
                    <em>Hinweis: Höhere Bitraten benötigen mehr Upload-Bandbreite!</em>
                </p>
            </div>

            <div class="section">
                <h2>👨‍💻 Autor</h2>
                <p>
                    <strong>Heiko Schäfer</strong><br>
                    E-Mail: <a href="mailto:contact@tuxhs.de">contact@tuxhs.de</a>
                </p>
            </div>

            <div class="section">
                <h2>📜 Lizenz</h2>
                <p>
                    TUXRTMPilot ist <strong>Freie Software</strong> und steht unter der
                    <strong>GNU General Public License v3.0</strong> (GPL-3.0).
                </p>
                <p>
                    Das bedeutet:
                </p>
                <ul>
                    <li>✅ Kostenlos nutzen</li>
                    <li>✅ Quellcode einsehen</li>
                    <li>✅ Änderungen vornehmen</li>
                    <li>✅ Weitergeben (auch kommerziell)</li>
                </ul>
                <p>
                    Bedingung: Abgeleitete Werke müssen ebenfalls unter GPL-3.0 stehen.
                </p>
                <p>
                    <strong>Voller Lizenztext:</strong>
                    <a href="https://www.gnu.org/licenses/gpl-3.0.html">
                        https://www.gnu.org/licenses/gpl-3.0.html
                    </a>
                </p>
            </div>

            <div class="section">
                <h2>🛠️ Technologie</h2>
                <p>
                    <strong>TUXRTMPilot</strong> nutzt folgende Open-Source-Technologien:
                </p>
                <ul>
                    <li><strong>Python 3.13+</strong> - Programmiersprache</li>
                    <li><strong>PyQt6</strong> - GUI-Framework</li>
                    <li><strong>GStreamer 1.26+</strong> - Multimedia-Framework</li>
                    <li><strong>PipeWire</strong> - Screen Capture (Wayland)</li>
                    <li><strong>V4L2</strong> - Webcam-Support</li>
                </ul>
            </div>

            <div class="section">
                <h2>⚠️ Wichtige Hinweise</h2>
                <p>
                    <strong>Stream-Keys niemals teilen!</strong> Dein Stream-Key ist wie ein Passwort.
                    Wer ihn kennt, kann in deinem Namen streamen.
                </p>
                <p>
                    <strong>Systemanforderungen:</strong>
                </p>
                <ul>
                    <li>Linux (Arch/CachyOS oder kompatibel)</li>
                    <li>KDE Plasma (oder andere Desktop-Umgebung mit PipeWire)</li>
                    <li>GStreamer mit allen Plugins installiert</li>
                    <li>Ausreichend Upload-Bandbreite (min. 5 Mbit/s)</li>
                </ul>
            </div>

            <div class="section">
                <h2>🐛 Support & Feedback</h2>
                <p>
                    Bei Problemen oder Fragen kannst du dich an den Autor wenden:
                </p>
                <p>
                    E-Mail: <a href="mailto:contact@tuxhs.de">contact@tuxhs.de</a>
                </p>
            </div>

            <hr>
            <p style="text-align: center; color: #888888;">
                <small>TUXRTMPilot v1.0.0 | GPL-3.0 License | © 2025 Heiko Schäfer</small>
            </p>
        </body>
        </html>
        """

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
            QTextBrowser {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px;
            }
        """)

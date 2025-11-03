#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Main Entry Point
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sys
import gi

# GStreamer initialisieren
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

from PyQt6.QtWidgets import QApplication

# Imports - sowohl als Modul als auch direkt ausführbar
try:
    from src.ui.main_window import MainWindow
    from src.core.device_manager import DeviceManager
    from src.utils.config import get_config
except ModuleNotFoundError:
    # Wenn direkt ausgeführt, füge Parent-Dir zum Path hinzu
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.ui.main_window import MainWindow
    from src.core.device_manager import DeviceManager
    from src.utils.config import get_config


def check_gstreamer_plugins() -> bool:
    """
    Prüft ob alle benötigten GStreamer-Elements verfügbar sind.

    Returns:
        True wenn alle Elements gefunden, False sonst
    """
    required_elements = [
        'pipewiresrc',     # Screen Capture
        'v4l2src',         # Webcam Support
        'autoaudiosrc',    # Auto Audio Source
        'x264enc',         # H.264 Encoder
        'flvmux',          # FLV Muxer
        'rtmpsink',        # RTMP Sink
        'videoconvert',    # Video Conversion
        'videoscale',      # Video Scaling
        'audioconvert',    # Audio Conversion
        'audioresample',   # Audio Resampling
    ]

    # AAC Audio Encoder - mehrere Optionen (prüfe mindestens einen)
    aac_encoders = ['fdkaacenc', 'voaacenc', 'faac', 'avenc_aac']
    aac_found = None

    missing = []

    for element_name in required_elements:
        factory = Gst.ElementFactory.find(element_name)
        if not factory:
            missing.append(element_name)

    # Prüfe AAC-Encoder (mindestens einer muss vorhanden sein)
    for encoder in aac_encoders:
        if Gst.ElementFactory.find(encoder):
            aac_found = encoder
            break

    if not aac_found:
        missing.append('aac-encoder (fdkaacenc/voaacenc/faac/avenc_aac)')

    if missing:
        print("❌ Fehlende GStreamer-Elements:")
        for element in missing:
            print(f"   - {element}")
        print("\n💡 Installation (Arch/CachyOS):")
        print("   sudo pacman -S gst-plugins-base gst-plugins-good")
        print("   sudo pacman -S gst-plugins-bad gst-plugins-ugly")
        print("   sudo pacman -S gst-plugin-pipewire")
        print("   sudo pacman -S gst-libav  # Für avenc_aac")
        return False

    print("✅ Alle benötigten GStreamer-Elements gefunden")
    if aac_found:
        print(f"   AAC-Encoder: {aac_found}")
    return True


def print_system_info() -> None:
    """Gibt System-Informationen aus."""
    print("\n" + "="*50)
    print("🐧 TUXRTMPilot - Multi-Platform RTMP Streaming")
    print("="*50)
    print(f"GStreamer: {Gst.version_string()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: Linux/KDE")
    print("="*50 + "\n")


def main() -> int:
    """
    Hauptfunktion - Einstiegspunkt der Anwendung.
    
    Returns:
        Exit-Code (0 = Erfolg, 1 = Fehler)
    """
    # GStreamer initialisieren
    Gst.init(None)
    print_system_info()
    
    # Plugin-Check
    if not check_gstreamer_plugins():
        print("\n⚠️ TUXRTMPilot kann nicht gestartet werden!")
        return 1
    
    # Config laden
    config = get_config()
    print(f"📁 Config: {config.config_file}")
    
    # Device-Manager initialisieren
    device_manager = DeviceManager()
    device_manager.list_all_devices()
    
    # PyQt6 Application erstellen
    app = QApplication(sys.argv)
    app.setApplicationName("TUXRTMPilot")
    app.setOrganizationName("TuxHS")
    
    # Hauptfenster erstellen und anzeigen
    window = MainWindow()
    window.show()
    
    print("\n🚀 TUXRTMPilot gestartet!")
    print("💡 Phase 1: Core Foundation aktiv")
    print("   - GStreamer: ✅")
    print("   - Device Manager: ✅")
    print("   - Config Manager: ✅")
    print("   - GUI: ✅")
    print("\n🔹 Drücke Ctrl+C im Terminal oder schließe das Fenster zum Beenden\n")
    
    # Event-Loop starten
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n👋 TUXRTMPilot beendet (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fataler Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

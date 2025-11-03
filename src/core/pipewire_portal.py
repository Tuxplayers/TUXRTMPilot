#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - PipeWire Portal Integration
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Inspiriert von Kooha (https://github.com/SeaDve/Kooha)
Screen Capture via org.freedesktop.portal.ScreenCast
"""

import subprocess
from typing import Optional


class PipeWirePortal:
    """
    Verwaltet PipeWire Desktop Portal Screen Capture.

    Nutzt xdg-desktop-portal für Screen/Window-Auswahl.
    Ähnlich wie Kooha, aber vereinfacht für RTMP-Streaming.
    """

    def __init__(self):
        """Initialisiert Portal."""
        self.portal_available = self._check_portal()

    def _check_portal(self) -> bool:
        """
        Prüft ob xdg-desktop-portal verfügbar ist.

        Returns:
            True wenn Portal verfügbar
        """
        try:
            result = subprocess.run(
                ['which', 'xdg-desktop-portal'],
                capture_output=True,
                timeout=2
            )
            available = result.returncode == 0

            if available:
                print("✅ xdg-desktop-portal verfügbar")
            else:
                print("⚠️ xdg-desktop-portal nicht gefunden")

            return available

        except Exception as e:
            print(f"⚠️ Portal-Check fehlgeschlagen: {e}")
            return False

    def get_screen_cast_source(self) -> Optional[str]:
        """
        Öffnet Screen-Picker-Dialog und gibt PipeWire-Source zurück.

        WICHTIG: Dies ist eine vereinfachte Version.
        Der KDE Portal-Dialog wird automatisch von pipewiresrc geöffnet,
        wenn wir 'do-timestamp=true' setzen.

        Returns:
            GStreamer pipewiresrc-String
        """
        if not self.portal_available:
            print("⚠️ Fallback: Portal nicht verfügbar, nutze Legacy-Methode")
            return "pipewiresrc"

        # GStreamer pipewiresrc öffnet automatisch den Portal-Dialog
        # wenn kein fd= Parameter gesetzt ist
        print("ℹ️ PipeWire Portal wird verwendet")
        print("ℹ️ Screen-Picker-Dialog sollte beim Stream-Start erscheinen")

        # Verwende pipewiresrc ohne fd= → öffnet automatisch Portal
        return "pipewiresrc do-timestamp=true"

    def is_available(self) -> bool:
        """
        Prüft ob Portal verfügbar ist.

        Returns:
            True wenn verfügbar
        """
        return self.portal_available


# Convenience-Funktion
def get_pipewire_source() -> str:
    """
    Holt PipeWire-Source für Screen Capture.

    Returns:
        GStreamer-Source-String für pipewiresrc
    """
    portal = PipeWirePortal()
    source = portal.get_screen_cast_source()

    if source:
        return source

    # Fallback
    return "pipewiresrc"

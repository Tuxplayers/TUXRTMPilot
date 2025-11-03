#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Configuration Manager
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Verwaltet Konfiguration und Einstellungen für TUXRTMPilot.
    
    Speichert Settings in JSON-Datei und lädt Secrets aus .env
    """
    
    DEFAULT_CONFIG = {
        "video_source": "screen",
        "audio_source": "default",
        "resolution": "1280x720",
        "bitrate": 2500,
        "fps": 30,
        "platform": "Benutzerdefiniert",
        "rtmp_url": "",
        "last_used_device": None,
    }
    
    def __init__(self, config_file: str = "tuxrtmpilot_config.json"):
        """
        Initialisiert ConfigManager.
        
        Args:
            config_file: Pfad zur Config-Datei (relativ zu Home-Dir)
        """
        self.config_dir = Path.home() / ".config" / "tuxrtmpilot"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / config_file
        self.config: Dict[str, Any] = {}
        
        # .env aus Projekt-Root laden (für Stream-Keys etc.)
        load_dotenv()
        
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Lädt Konfiguration aus JSON-Datei.
        
        Returns:
            Dictionary mit Config-Werten
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Config geladen: {self.config_file}")
            except json.JSONDecodeError as e:
                print(f"⚠️ Config-Fehler: {e}, verwende Defaults")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            print("ℹ️ Keine Config gefunden, erstelle neue mit Defaults")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Speichert aktuelle Konfiguration in JSON-Datei.
        
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Config gespeichert: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Config-Speichern fehlgeschlagen: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Config-Wert.
        
        Args:
            key: Config-Schlüssel
            default: Rückgabewert falls Key nicht existiert
            
        Returns:
            Config-Wert oder default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Setzt einen Config-Wert (wird nicht automatisch gespeichert!).
        
        Args:
            key: Config-Schlüssel
            value: Neuer Wert
        """
        self.config[key] = value
    
    def get_stream_key(self, platform: str) -> Optional[str]:
        """
        Holt Stream-Key für Plattform aus Umgebungsvariablen.
        
        SICHERHEIT: Stream-Keys werden NIEMALS in Config-Datei gespeichert!
        
        Args:
            platform: Plattform-Name (z.B. "TWITCH", "YOUTUBE")
            
        Returns:
            Stream-Key oder None
        """
        env_key = f"{platform.upper()}_STREAM_KEY"
        return os.getenv(env_key)
    
    def reset_to_defaults(self) -> None:
        """Setzt Config auf Default-Werte zurück."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        print("🔄 Config auf Defaults zurückgesetzt")


# Convenience-Funktion für schnellen Zugriff
_config_instance: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
    """
    Gibt Singleton-Instanz des ConfigManagers zurück.
    
    Returns:
        ConfigManager-Instanz
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager()
    return _config_instance

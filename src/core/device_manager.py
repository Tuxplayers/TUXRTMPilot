#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Device Manager
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class DeviceManager:
    """
    Verwaltet Video- und Audio-Geräte für Streaming.
    
    Erkennt:
    - Screen Capture (PipeWire)
    - Webcams (V4L2)
    - Audio-Quellen (PulseAudio/PipeWire)
    """
    
    def __init__(self):
        """Initialisiert DeviceManager."""
        # GStreamer muss bereits initialisiert sein (passiert in main.py)
        pass
    
    def get_video_sources(self) -> List[Dict[str, str]]:
        """
        Holt alle verfügbaren Video-Quellen.
        
        Returns:
            Liste von Dicts mit 'name' und 'device' keys
            Beispiel: [
                {'name': 'Screen Capture', 'device': 'screen'},
                {'name': 'Webcam (HD Pro C920)', 'device': '/dev/video0'}
            ]
        """
        sources = []

        # Screen Capture (PipeWire Portal) - öffnet Picker
        sources.append({
            'name': '🖥️ Screen Capture (PipeWire Portal)',
            'device': 'screen',
            'type': 'pipewire',
            'description': 'Öffnet Fenster/Screen-Auswahl-Dialog beim Stream-Start'
        })

        # Webcams erkennen (V4L2)
        webcams = self._detect_webcams()
        sources.extend(webcams)

        return sources
    
    def _detect_webcams(self) -> List[Dict[str, str]]:
        """
        Erkennt Webcams über /dev/video* und v4l2.

        Returns:
            Liste von Webcam-Dicts
        """
        webcams = []
        video_devices = Path('/dev').glob('video*')

        for device_path in sorted(video_devices):
            device_str = str(device_path)

            # Nur capture-Devices (video0, video2, ...), nicht metadata
            if not device_str[-1].isdigit():
                continue

            # Prüfe ob Device verfügbar ist
            if not self._is_device_available(device_str):
                print(f"⚠️ Device {device_str} ist belegt oder nicht verfügbar")
                continue

            # Versuche Device-Namen zu holen
            device_name = self._get_webcam_name(device_str)

            if device_name:
                webcams.append({
                    'name': f'Webcam ({device_name})',
                    'device': device_str,
                    'type': 'v4l2'
                })

        return webcams

    def _is_device_available(self, device_path: str) -> bool:
        """
        Prüft ob Device verfügbar und nicht belegt ist.

        Args:
            device_path: Pfad zum Device

        Returns:
            True wenn verfügbar
        """
        try:
            # Versuche Device zu öffnen (read-only test)
            import fcntl
            import os
            fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)
            os.close(fd)
            return True
        except (OSError, PermissionError):
            return False
    
    def _get_webcam_name(self, device_path: str) -> Optional[str]:
        """
        Holt den Namen einer Webcam über v4l2-ctl.
        
        Args:
            device_path: Pfad zum Device (z.B. /dev/video0)
            
        Returns:
            Device-Name oder None
        """
        try:
            result = subprocess.run(
                ['v4l2-ctl', '--device', device_path, '--info'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            # Parse Card-Name aus Output
            for line in result.stdout.split('\n'):
                if 'Card type' in line:
                    return line.split(':', 1)[1].strip()
            
            # Fallback: Nur Device-Nummer
            return device_path.split('/')[-1]
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # v4l2-ctl nicht installiert oder Device nicht verfügbar
            return device_path.split('/')[-1]
    
    def get_audio_sources(self) -> List[Dict[str, str]]:
        """
        Holt alle verfügbaren Audio-Quellen.
        
        Returns:
            Liste von Dicts mit 'name' und 'device' keys
            Beispiel: [
                {'name': 'Default Audio', 'device': 'default'},
                {'name': 'PulseAudio Monitor', 'device': 'pulse'}
            ]
        """
        sources = []
        
        # Default Audio-Source (autoaudiosrc in GStreamer)
        sources.append({
            'name': 'Default Audio (Mikrofon)',
            'device': 'default',
            'type': 'auto'
        })
        
        # PulseAudio/PipeWire Monitor (Desktop-Audio)
        sources.append({
            'name': 'Desktop Audio (Monitor)',
            'device': 'monitor',
            'type': 'pulse'
        })
        
        # Weitere Quellen könnten über pactl erkannt werden
        # Für Phase 1 reichen diese zwei
        
        return sources
    
    def test_video_source(self, device: str) -> bool:
        """
        Testet ob eine Video-Quelle verfügbar ist.
        
        Args:
            device: Device-String (z.B. 'screen' oder '/dev/video0')
            
        Returns:
            True wenn verfügbar, False sonst
        """
        try:
            if device == 'screen':
                # Test PipeWire Screen Capture
                pipeline_str = "pipewiresrc ! fakesink"
            else:
                # Test V4L2 Webcam
                pipeline_str = f"v4l2src device={device} ! fakesink"
            
            pipeline = Gst.parse_launch(pipeline_str)
            pipeline.set_state(Gst.State.READY)
            
            # Warte kurz und check State
            ret = pipeline.get_state(Gst.CLOCK_TIME_NONE)
            success = ret[0] == Gst.StateChangeReturn.SUCCESS
            
            pipeline.set_state(Gst.State.NULL)
            return success
            
        except Exception as e:
            print(f"⚠️ Video-Source-Test fehlgeschlagen: {e}")
            return False
    
    def test_audio_source(self, device: str) -> bool:
        """
        Testet ob eine Audio-Quelle verfügbar ist.
        
        Args:
            device: Device-String (z.B. 'default' oder 'monitor')
            
        Returns:
            True wenn verfügbar, False sonst
        """
        try:
            if device == 'default':
                pipeline_str = "autoaudiosrc ! fakesink"
            elif device == 'monitor':
                pipeline_str = "pulsesrc ! fakesink"
            else:
                pipeline_str = "autoaudiosrc ! fakesink"
            
            pipeline = Gst.parse_launch(pipeline_str)
            pipeline.set_state(Gst.State.READY)
            
            ret = pipeline.get_state(Gst.CLOCK_TIME_NONE)
            success = ret[0] == Gst.StateChangeReturn.SUCCESS
            
            pipeline.set_state(Gst.State.NULL)
            return success
            
        except Exception as e:
            print(f"⚠️ Audio-Source-Test fehlgeschlagen: {e}")
            return False
    
    def list_all_devices(self) -> None:
        """Debug-Funktion: Listet alle erkannten Geräte auf."""
        print("\n📹 Video-Quellen:")
        for source in self.get_video_sources():
            print(f"  - {source['name']} [{source['device']}]")
        
        print("\n🎤 Audio-Quellen:")
        for source in self.get_audio_sources():
            print(f"  - {source['name']} [{source['device']}]")

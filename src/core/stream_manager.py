#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUXRTMPilot - Stream Manager
Copyright (C) 2025 Heiko Schäfer <contact@tuxhs.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from typing import Optional, Dict, Any
import threading


class GStreamerThread(QThread):
    """
    Worker-Thread für GStreamer GLib.MainLoop.

    Läuft separat vom Qt Event Loop, um GStreamer-Events
    zu verarbeiten (Bus-Messages, EOS, Errors).
    """

    def __init__(self):
        """Initialisiert GStreamer-Thread."""
        super().__init__()
        self.loop: Optional[GLib.MainLoop] = None
        self._running = False

    def run(self) -> None:
        """
        Thread-Hauptfunktion - läuft GLib.MainLoop.

        Wird automatisch von QThread.start() aufgerufen.
        """
        self.loop = GLib.MainLoop()
        self._running = True
        print("🔹 GStreamer-Thread gestartet")
        self.loop.run()
        print("🔹 GStreamer-Thread beendet")

    def stop(self) -> None:
        """Stoppt den GLib.MainLoop-Thread."""
        if self.loop and self._running:
            self.loop.quit()
            self._running = False


class StreamManager(QObject):
    """
    Verwaltet GStreamer-Pipelines für RTMP-Streaming.

    Features:
    - Screen Capture (PipeWire) oder Webcam (V4L2)
    - Audio von Mikrofon oder Desktop-Monitor
    - H.264 Video-Encoding (x264enc)
    - AAC Audio-Encoding (automatische Encoder-Wahl)
    - RTMP-Streaming zu verschiedenen Plattformen

    Signals:
    - error_signal: Fehler-Nachrichten
    - status_signal: Status-Updates
    - state_changed_signal: Pipeline-State-Änderungen
    """

    # Qt Signals für Thread-sichere Kommunikation
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    state_changed_signal = pyqtSignal(str)  # "idle", "starting", "streaming", "stopping"

    def __init__(self):
        """Initialisiert StreamManager."""
        super().__init__()  # WICHTIG für QObject

        # Kombinierte Pipeline (für Preview + Stream mit tee)
        self.pipeline: Optional[Gst.Pipeline] = None
        self.gst_thread: Optional[GStreamerThread] = None

        # Status-Flags
        self.is_streaming = False
        self.is_preview_active = False
        self.preview_was_active_before_stream = False

        # Current Stream Config
        self.current_config: Dict[str, Any] = {}
        self.current_preview_config: Dict[str, Any] = {}

        # Besten verfügbaren AAC-Encoder finden
        self.aac_encoder = self._find_best_aac_encoder()
        print(f"🔹 AAC-Encoder: {self.aac_encoder}")

    def _find_best_aac_encoder(self) -> str:
        """
        Findet den besten verfügbaren AAC-Encoder.

        Priorität: fdkaacenc > voaacenc > faac > avenc_aac

        Returns:
            Name des AAC-Encoders
        """
        encoders = ['fdkaacenc', 'voaacenc', 'faac', 'avenc_aac']
        for encoder in encoders:
            if Gst.ElementFactory.find(encoder):
                return encoder

        # Fallback (sollte nie passieren nach Plugin-Check)
        return 'avenc_aac'

    def start_stream(
        self,
        video_source: str,
        audio_source: str,
        rtmp_url: str,
        stream_key: str,
        resolution: str = "1280x720",
        bitrate: int = 2500,
        fps: int = 30
    ) -> bool:
        """
        Startet den RTMP-Stream.

        Wenn Preview läuft: Stoppt Preview und startet kombinierte Pipeline (Preview + Stream).

        Args:
            video_source: Video-Quelle ('screen' oder '/dev/videoX')
            audio_source: Audio-Quelle ('default' oder 'monitor')
            rtmp_url: RTMP-Server-URL (ohne Stream-Key)
            stream_key: Stream-Schlüssel (wird sicher behandelt)
            resolution: Auflösung (z.B. "1280x720")
            bitrate: Video-Bitrate in kbps
            fps: Framerate

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if self.is_streaming:
            self.error_signal.emit("❌ Stream läuft bereits!")
            return False

        # Validierung
        if not rtmp_url or not stream_key:
            self.error_signal.emit("❌ RTMP-URL und Stream-Key erforderlich!")
            return False

        # Preview läuft? → Stoppen und kombinierte Pipeline starten
        if self.is_preview_active:
            print("🔹 Preview läuft - wechsle zu kombinierter Pipeline")
            self.preview_was_active_before_stream = True
            self._stop_preview_internal()  # Stoppe Preview ohne Signal

        # Config speichern
        self.current_config = {
            'video_source': video_source,
            'audio_source': audio_source,
            'rtmp_url': rtmp_url,
            'stream_key': stream_key,
            'resolution': resolution,
            'bitrate': bitrate,
            'fps': fps
        }

        try:
            self.state_changed_signal.emit("starting")
            self.status_signal.emit("🔄 Erstelle GStreamer-Pipeline...")

            # Pipeline erstellen (mit tee wenn Preview vorher lief)
            if self.preview_was_active_before_stream:
                pipeline_str = self._build_combined_pipeline_string()
                print("🔹 Nutze kombinierte Pipeline (Stream + Preview)")
            else:
                pipeline_str = self._build_pipeline_string()

            print(f"🔹 Pipeline: {self._sanitize_pipeline_for_log(pipeline_str)}")

            self.pipeline = Gst.parse_launch(pipeline_str)

            # Bus-Watcher für Fehler und EOS einrichten
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._on_bus_message)

            # GStreamer-Thread starten
            self.gst_thread = GStreamerThread()
            self.gst_thread.start()

            # Pipeline starten
            self.status_signal.emit("🚀 Starte Stream...")
            ret = self.pipeline.set_state(Gst.State.PLAYING)

            if ret == Gst.StateChangeReturn.FAILURE:
                self.error_signal.emit("❌ Pipeline konnte nicht gestartet werden!")
                self._cleanup_pipeline()
                return False

            self.is_streaming = True

            # Preview ist auch aktiv wenn kombinierte Pipeline
            if self.preview_was_active_before_stream:
                self.is_preview_active = True
                self.status_signal.emit("✅ Stream + Preview laufen!")
            else:
                self.status_signal.emit("✅ Stream läuft!")

            self.state_changed_signal.emit("streaming")
            return True

        except Exception as e:
            self.error_signal.emit(f"❌ Fehler beim Stream-Start: {e}")
            self._cleanup_pipeline()
            return False

    def stop_stream(self) -> bool:
        """
        Stoppt den laufenden Stream.

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not self.is_streaming:
            self.error_signal.emit("⚠️ Kein Stream aktiv!")
            return False

        try:
            self.state_changed_signal.emit("stopping")
            self.status_signal.emit("🛑 Stoppe Stream...")

            # Pipeline auf NULL setzen
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)

            # Cleanup
            self._cleanup_pipeline()

            self.is_streaming = False
            self.state_changed_signal.emit("idle")
            self.status_signal.emit("✅ Stream gestoppt")
            return True

        except Exception as e:
            self.error_signal.emit(f"❌ Fehler beim Stoppen: {e}")
            return False

    def _build_pipeline_string(self) -> str:
        """
        Baut die GStreamer-Pipeline-String zusammen (nur Stream).

        Returns:
            Pipeline-String für Gst.parse_launch()
        """
        config = self.current_config
        width, height = config['resolution'].split('x')

        # Video-Source
        if config['video_source'] == 'screen':
            video_src = "pipewiresrc media-type=video/source/screen"
        else:
            video_src = f"v4l2src device={config['video_source']}"

        # Audio-Source
        if config['audio_source'] == 'monitor':
            audio_src = "pulsesrc"
        else:
            audio_src = "autoaudiosrc"

        # RTMP-Location (URL + Key)
        rtmp_location = f"{config['rtmp_url']}/{config['stream_key']}"

        # Pipeline zusammenbauen
        pipeline = (
            # Video-Branch
            f"{video_src} ! "
            f"videoconvert ! "
            f"videoscale ! "
            f"video/x-raw,width={width},height={height},framerate={config['fps']}/1 ! "
            f"x264enc bitrate={config['bitrate']} speed-preset=ultrafast tune=zerolatency ! "
            f"video/x-h264,profile=baseline ! "
            f"queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! "
            f"mux. "

            # Audio-Branch
            f"{audio_src} ! "
            f"audioconvert ! "
            f"audioresample ! "
            f"audio/x-raw,rate=44100,channels=2 ! "
            f"{self.aac_encoder} bitrate=128000 ! "
            f"queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! "
            f"mux. "

            # Muxer & RTMP Sink
            f"flvmux name=mux streamable=true ! "
            f"rtmpsink location=\"{rtmp_location}\""
        )

        return pipeline

    def _build_combined_pipeline_string(self) -> str:
        """
        Baut kombinierte Pipeline mit tee (Preview + Stream).

        Returns:
            Pipeline-String für Gst.parse_launch()
        """
        config = self.current_config
        width, height = config['resolution'].split('x')

        # Video-Source
        if config['video_source'] == 'screen':
            video_src = "pipewiresrc do-timestamp=true"
        else:
            video_src = f"v4l2src device={config['video_source']}"

        # Audio-Source
        if config['audio_source'] == 'monitor':
            audio_src = "pulsesrc"
        else:
            audio_src = "autoaudiosrc"

        # RTMP-Location
        rtmp_location = f"{config['rtmp_url']}/{config['stream_key']}"

        # Kombinierte Pipeline mit tee
        pipeline = (
            # Video-Source → tee aufteilen
            f"{video_src} ! "
            f"videoconvert ! "
            f"videoscale ! "
            f"video/x-raw,width={width},height={height},framerate={config['fps']}/1 ! "
            f"tee name=t "

            # Preview-Zweig
            f"t. ! queue ! autovideosink "

            # Stream-Zweig
            f"t. ! queue ! "
            f"x264enc bitrate={config['bitrate']} speed-preset=ultrafast tune=zerolatency ! "
            f"video/x-h264,profile=baseline ! "
            f"queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! "
            f"mux. "

            # Audio-Branch
            f"{audio_src} ! "
            f"audioconvert ! "
            f"audioresample ! "
            f"audio/x-raw,rate=44100,channels=2 ! "
            f"{self.aac_encoder} bitrate=128000 ! "
            f"queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! "
            f"mux. "

            # Muxer & RTMP Sink
            f"flvmux name=mux streamable=true ! "
            f"rtmpsink location=\"{rtmp_location}\""
        )

        return pipeline

    def _sanitize_pipeline_for_log(self, pipeline: str) -> str:
        """
        Entfernt Stream-Key aus Pipeline-String für Logs.

        SICHERHEIT: Stream-Keys dürfen NIEMALS in Logs erscheinen!

        Args:
            pipeline: Original-Pipeline-String

        Returns:
            Pipeline-String mit verstecktem Stream-Key
        """
        if 'stream_key' in self.current_config:
            key = self.current_config['stream_key']
            return pipeline.replace(key, "***HIDDEN***")
        return pipeline

    def _on_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> bool:
        """
        Callback für GStreamer-Bus-Messages.

        Verarbeitet Fehler, Warnungen, EOS, State-Changes.

        Args:
            bus: GStreamer-Bus
            message: Bus-Message

        Returns:
            True um Watcher aktiv zu halten
        """
        msg_type = message.type

        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self.error_signal.emit(f"❌ GStreamer-Fehler: {err.message}")
            print(f"🔹 Debug: {debug}")
            self.stop_stream()

        elif msg_type == Gst.MessageType.WARNING:
            warn, debug = message.parse_warning()
            self.status_signal.emit(f"⚠️ Warnung: {warn.message}")
            print(f"🔹 Debug: {debug}")

        elif msg_type == Gst.MessageType.EOS:
            self.status_signal.emit("ℹ️ Stream beendet (EOS)")
            self.stop_stream()

        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                print(f"🔹 Pipeline: {old_state.value_nick} → {new_state.value_nick}")

        return True

    def _cleanup_pipeline(self) -> None:
        """Räumt Pipeline und Thread auf."""
        # Bus-Watcher entfernen
        if self.pipeline:
            bus = self.pipeline.get_bus()
            bus.remove_signal_watch()

        # GStreamer-Thread stoppen
        if self.gst_thread and self.gst_thread.isRunning():
            self.gst_thread.stop()
            self.gst_thread.wait(2000)  # Max 2s warten
            if self.gst_thread.isRunning():
                self.gst_thread.terminate()

        # Pipeline freigeben
        self.pipeline = None
        self.gst_thread = None

    def get_stream_stats(self) -> Dict[str, Any]:
        """
        Holt aktuelle Stream-Statistiken.

        Returns:
            Dict mit Stats (z.B. Bitrate, FPS, Uptime)
            Oder leeres Dict wenn kein Stream aktiv
        """
        if not self.is_streaming or not self.pipeline:
            return {}

        # TODO: Implementiere Stats-Extraktion aus Pipeline
        # Für Phase 2: Basis-Return
        return {
            'is_streaming': True,
            'resolution': self.current_config.get('resolution', 'unknown'),
            'bitrate': self.current_config.get('bitrate', 0),
        }

    # ==================== PREVIEW FUNKTIONEN ====================

    def start_preview(
        self,
        video_source: str,
        resolution: str = "1280x720",
        fps: int = 30
    ) -> bool:
        """
        Startet lokale Video-Preview in separatem Fenster.

        Wenn Stream läuft: Ignoriert (Preview läuft schon via kombinierte Pipeline).

        Args:
            video_source: Video-Quelle ('screen' oder '/dev/videoX')
            resolution: Ziel-Auflösung
            fps: Framerate

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if self.is_preview_active:
            self.error_signal.emit("⚠️ Preview läuft bereits!")
            return False

        # Wenn Stream läuft: Preview ist schon in kombinierter Pipeline
        if self.is_streaming:
            self.status_signal.emit("ℹ️ Preview läuft bereits im Stream!")
            self.is_preview_active = True
            return True

        # Preview-Config speichern für später
        self.current_preview_config = {
            'video_source': video_source,
            'resolution': resolution,
            'fps': fps
        }

        try:
            self.status_signal.emit("🔄 Erstelle Preview-Pipeline...")
            width, height = resolution.split('x')

            # Video-Source
            if video_source == 'screen':
                video_src = "pipewiresrc do-timestamp=true"
                print("ℹ️ PipeWire-Portal wird für Preview genutzt")
            else:
                video_src = f"v4l2src device={video_source}"

            # Preview-Pipeline → Separates Fenster
            pipeline_str = (
                f"{video_src} ! "
                f"videoconvert ! "
                f"videoscale ! "
                f"video/x-raw,width={width},height={height},framerate={fps}/1 ! "
                f"autovideosink"
            )

            print(f"🔹 Preview-Pipeline: {pipeline_str}")
            self.pipeline = Gst.parse_launch(pipeline_str)

            # Bus-Watcher
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._on_preview_bus_message)

            # Pipeline starten
            self.status_signal.emit("▶️ Starte Preview...")
            ret = self.pipeline.set_state(Gst.State.PLAYING)

            if ret == Gst.StateChangeReturn.FAILURE:
                self.error_signal.emit("❌ Preview konnte nicht gestartet werden!")
                self._cleanup_pipeline()
                return False

            self.is_preview_active = True
            self.status_signal.emit("✅ Preview aktiv (Separates Fenster)!")
            return True

        except Exception as e:
            self.error_signal.emit(f"❌ Fehler beim Preview-Start: {e}")
            self._cleanup_pipeline()
            return False

    def _stop_preview_internal(self) -> None:
        """Stoppt Preview ohne Signale (intern)."""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            bus = self.pipeline.get_bus()
            bus.remove_signal_watch()
        self.pipeline = None
        self.is_preview_active = False

    def stop_preview(self) -> bool:
        """
        Stoppt die laufende Preview.

        Wenn Stream läuft: Wird ignoriert (Preview läuft in kombinierter Pipeline).

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not self.is_preview_active:
            self.error_signal.emit("⚠️ Keine Preview aktiv!")
            return False

        # Wenn Stream läuft: Nur Flag setzen, Pipeline weiterlaufen lassen
        if self.is_streaming:
            self.is_preview_active = False
            self.preview_was_active_before_stream = False
            self.status_signal.emit("ℹ️ Preview deaktiviert (Stream läuft weiter)")
            return True

        try:
            self.status_signal.emit("⏸️ Stoppe Preview...")

            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)

            self._cleanup_pipeline()
            self.is_preview_active = False
            self.status_signal.emit("✅ Preview gestoppt")
            return True

        except Exception as e:
            self.error_signal.emit(f"❌ Fehler beim Preview-Stoppen: {e}")
            return False

    def _on_preview_bus_message(self, bus: Gst.Bus, message: Gst.Message) -> bool:
        """Callback für Preview-Pipeline-Bus-Messages (wenn nur Preview läuft)."""
        msg_type = message.type

        if msg_type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self.error_signal.emit(f"❌ Preview-Fehler: {err.message}")
            print(f"🔹 Preview Debug: {debug}")
            self.stop_preview()

        elif msg_type == Gst.MessageType.WARNING:
            warn, debug = message.parse_warning()
            self.status_signal.emit(f"⚠️ Preview-Warnung: {warn.message}")

        elif msg_type == Gst.MessageType.EOS:
            self.status_signal.emit("ℹ️ Preview beendet (EOS)")
            self.stop_preview()

        elif msg_type == Gst.MessageType.STATE_CHANGED:
            if message.src == self.pipeline:
                old_state, new_state, pending = message.parse_state_changed()
                print(f"🔹 Preview: {old_state.value_nick} → {new_state.value_nick}")

        return True

    def __del__(self):
        """Destruktor - stellt sicher dass Pipeline sauber beendet wird."""
        if self.is_streaming:
            self.stop_stream()
        elif self.is_preview_active:
            self.stop_preview()

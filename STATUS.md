# TUXRTMPilot - Aktueller Status

**Datum**: 3. November 2025, 20:39 Uhr

## ✅ FUNKTIONIERENDES BACKUP

**Backup**: `backups/20251103_203905` (Recording-Feature)

### Was funktioniert:

✅ **UI ohne Duplikate**
- Nur EINE Tab-Leiste
- Nur EINE linke Control-Seite
- Nur EINE rechte Preview-Seite
- Sauberes Layout

✅ **Funktionen**
- Geräteauswahl (Webcam/Desktop)
- Audio-Auswahl
- Stream-Konfiguration
- Preview (separates Fenster)
- Stream-Controls
- Preview schließt sauber ohne Fehler
- **Webcam-Recording (Video-only, MKV-Format)**

✅ **Core-Funktionalität**
- GStreamer-Integration
- DeviceManager
- ConfigManager
- StreamManager (mit Recording)

### Heutige Implementierungen:

✅ **Preview-Fehler behoben** (20:05 Uhr)
- Preview-Fenster schließt jetzt sauber mit "✅ Preview geschlossen"
- Keine Fehlermeldung mehr beim Schließen des Fensters
- Fix in `src/core/stream_manager.py:_on_preview_bus_message()`

✅ **Recording-Feature implementiert** (20:39 Uhr)
- Webcam-Aufnahme in MKV-Format (robust)
- Nur Video (ohne Audio - vermeidet Timing-Probleme)
- Sauberes EOS-Handling
- Preview wird automatisch gestoppt vor Recording
- Dateien: `recordings/recording_YYYYMMDD_HHMMSS.mkv`
- Buttons: "🎥 Aufnahme starten" / "⏹️ Aufnahme stoppen"

## ⚠️ BEKANNTE EINSCHRÄNKUNGEN

**Recording:**
- ❌ Nur Webcam (kein Desktop-Recording)
- ❌ Kein Audio (nur Video)
- ℹ️ Desktop braucht XDG Portal (große Änderung)
- ℹ️ Audio hatte Timing-Probleme

**Desktop-Preview:**
- ❌ Zeigt leeres Fenster
- ℹ️ Braucht XDG Portal für Wayland

## 🚀 NÄCHSTE SCHRITTE FÜR MORGEN

### Priorität 1: Recording verbessern
**A) Audio-Recording hinzufügen**
- Problem: Audio-Timing ("Ton kann nicht schnell genug aufgezeichnet werden")
- Lösung: Größere Audio-Buffer, async Recording
- Aufwand: Klein (1 Datei)
- Dateien: `src/core/stream_manager.py`

**B) Recording-Optionen in UI**
- Checkbox: "Mit Audio aufnehmen"
- Format-Auswahl: MKV / MP4
- Qualitäts-Presets
- Aufwand: Klein (1 Datei)
- Dateien: `src/ui/stream_tab.py`

### Priorität 2: Desktop-Capture (XDG Portal)
**Große Änderung - mehrere Schritte:**

1. **Portal-Client erstellen** (`src/core/portal_client.py`)
   - D-Bus-Kommunikation mit `org.freedesktop.portal.ScreenCast`
   - Fenster-Auswahl-Dialog triggern
   - File Descriptor + Stream Info holen
   - Aufwand: Mittel-Groß (neue Datei, ~200 Zeilen)

2. **DeviceManager erweitern** (`src/core/device_manager.py`)
   - Portal für Screen-Capture nutzen
   - `fd` und `node_id` an StreamManager übergeben
   - Aufwand: Klein (bestehende Datei)

3. **StreamManager anpassen** (`src/core/stream_manager.py`)
   - pipewiresrc mit `fd={fd} path={node_id}`
   - `videoflip video-direction=auto` hinzufügen
   - `videorate skip-to-first=true` hinzufügen
   - Aufwand: Klein (bestehende Datei)

4. **Dependencies prüfen**
   - `xdg-desktop-portal-kde` installiert?
   - GStreamer PipeWire-Plugin vorhanden?
   - Aufwand: Sehr klein

**Gesamt-Aufwand: Mittel (2-3 Stunden)**

### Priorität 3: UI-Verbesserungen
- Stream-Statistiken (Bitrate, FPS, Uptime)
- Recording-Fortschritt (Zeit, Dateigröße)
- Warnung: "Stream-Key niemals teilen!" als Tooltip
- Embedded Preview (optional, wenn Portal läuft)

### Priorität 4: Code-Qualität
- Audio-Warnings beim Cleanup beheben
- Besseres Error-Handling
- Unit-Tests (optional)

## 📝 WICHTIGE REGELN

1. **VOR jeder Änderung**: `./backup.sh`
2. **NACH jeder Änderung**: Test + Screenshot
3. **NUR EINE Änderung** pro Sitzung
4. **Bei Problemen**: Sofort `cp -r backups/20251103_203905/src .`

## 🎯 Aktuell Aktive Version

```bash
# Wiederherstellen falls nötig:
rm -rf src
cp -r backups/20251103_203905/src .
```

## 🚀 Starten

```bash
source venv/bin/activate
python -B src/main.py
```

## 📦 Backups

- **Aktuell**: `backups/20251103_203905` (Recording-Feature)
- **Stabil**: `backups/20251103_200556` (Preview-Fix)
- **Alt (funktioniert)**: `backups/20251103_132955` (Ohne Recording)
- **Defekt**: `backups/20251103_124836` (UI-Duplikate)
- **Ältere**: Siehe `ls -lt backups/`

markdown# 🐧 TUXRTMPilot - Claude Development Context

## 📋 Projekt-Übersicht
**TUXRTMPilot** ist ein professionelles Multi-Platform RTMP Streaming Tool für Linux/KDE.
Entwickelt in Python mit PyQt6 (UI) und GStreamer (Video/Audio-Processing).

**Autor**: Heiko Schäfer <contact@tuxhs.de  
**License**: GPL-3.0  
**Platform**: CachyOS Linux (Arch-basiert), KDE Plasma  
**Version**: 1.0.0 (in Development)

---

## 🛠️ Tech Stack

### Core
- **Python**: 3.10+
- **GUI Framework**: PyQt6 (6.6.0+)
- **Video/Audio Processing**: GStreamer 1.0 (via PyGObject)
- **Screen Capture**: PipeWire (Wayland-native)
- **Multi-Streaming**: nginx-rtmp-module

### Dependencies
```python
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
PyGObject>=3.46.0  # GStreamer Python Bindings
requests>=2.31.0
python-dotenv>=1.0.0
```

### System Dependencies (Arch/CachyOS)
```bash
python-pyqt6
gstreamer
gst-plugins-base
gst-plugins-good
gst-plugins-bad
gst-plugins-ugly
gst-plugin-pipewire
python-gobject
nginx-mainline
libnginx-mod-rtmp
```

--- 
# Hapbtverzeichniss
cd scripts/tools/

~/scripts/tools
❯ mkdir kde-rtmp-streamer

~/scripts/tools
❯ cd kde-rtmp-streamer

~/scripts/tools/kde-rtmp-streamer
❯ git init

Leeres Git-Repository in /home/heiko/scripts/tools/kde-rtmp-streamer/.git/ initialisiert

~/scripts/tools/kde-rtmp-streamer main
❯ code .

~/scripts/tools/kde-rtmp-streamer main
❯ 


## 📂 Projekt-Struktur
```
kde-rtmp-streamer/
├── src/
│   ├── __init__.py
│   ├── main.py                # Einstiegspunkt, GStreamer-Init
│   ├── ui/                    # PyQt6 GUI-Komponenten
│   │   ├── __init__.py
│   │   ├── main_window.py     # QMainWindow, Tab-Management
│   │   ├── stream_tab.py      # Haupt-Stream-Interface
│   │   ├── settings_tab.py    # Einstellungen, Plattform-Config
│   │   └── nginx_tab.py       # nginx-rtmp Management
│   ├── core/                  # Business Logic
│   │   ├── __init__.py
│   │   ├── stream_manager.py  # GStreamer-Pipeline, RTMP-Handling
│   │   ├── device_manager.py  # Video/Audio-Device-Erkennung
│   │   └── nginx_manager.py   # nginx-rtmp Control
│   └── utils/                 # Hilfsfunktionen
│       ├── __init__.py
│       └── config.py          # Config-Management (JSON/dotenv)
├── config/
│   └── nginx.conf.template    # nginx-rtmp Template
├── tests/
├── venv/                      # Virtuelle Umgebung (git-ignored)
├── .gitignore
├── .clinerules                # Dieser Prompt
├── README.md
├── requirements.txt
└── LICENSE
```

---

## 🎯 Features & Ziele

### ✅ Implementiert (aus mein_tictok_proggi.py)
- GStreamer-Pipeline für Screen Capture (PipeWire)
- RTMP-Streaming mit H.264 (x264enc)
- Audio/Video-Synchronisation
- Basis-Stream-Services-Konfiguration

### 🚧 In Development
- [ ] Moderne PyQt6-GUI mit Dark Mode (KDE Breeze-Style)
- [ ] Multi-Platform Streaming (Twitch, YouTube, TikTok, Facebook, Kick)
- [ ] nginx-rtmp Integration für lokales Multi-Streaming
- [ ] Video/Audio-Geräteselektion mit Live-Preview
- [ ] Stream-Preview im UI
- [ ] Persistente Einstellungen (Config-File)
- [ ] Stream-Statistics (Bitrate, FPS, Uptime)
- [ ] Recording-Funktion
- [ ] Stream-Key-Management (verschlüsselt)

---

## 🎥 GStreamer Pipeline-Architektur

### Video-Quellen
```python
# Screen Capture (Wayland/PipeWire)
"pipewiresrc media-type=video/source/screen ! videoconvert ! video/x-raw,format=RGB"

# Webcam (V4L2)
"v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,format=RGB"
```

### Audio-Quellen
```python
# PulseAudio/PipeWire
"autoaudiosrc ! audioconvert ! audioresample"
```

### RTMP-Streaming-Pipeline
```python
# Video-Branch
video_source + "! videoscale ! video/x-raw,width=1280,height=720 ! " +
"x264enc bitrate=2500 speed-preset=ultrafast tune=zerolatency ! " +
"video/x-h264,profile=baseline ! queue ! mux."

# Audio-Branch  
"autoaudiosrc ! audioconvert ! audioresample ! " +
"voaacenc bitrate=128000 ! queue ! mux."

# Muxer & Sink
"flvmux name=mux ! rtmpsink location='rtmp://server/app/stream_key'"
```

---

## 📡 Stream-Services-Konfiguration
```python
STREAM_SERVICES = {
    "Benutzerdefiniert": "",
    "YouTube": "rtmp://a.rtmp.youtube.com/live2",
    "Twitch": "rtmp://live.twitch.tv/app",
    "TikTok (Custom)": "",
    "Facebook Live": "rtmps://live-api-s.facebook.com:443/rtmp/",
    "Kick": "rtmp://fra.contribute.live-video.net/app",
    "Restream.io": "rtmp://live.restream.io/live/",
    "OBS Ninja": "rtmp://localhost:1935/live"  # für nginx-rtmp
}
```

---

## 🎨 UI/UX Design-Prinzipien

### Dark Mode (KDE Breeze Dark)
```css
Background: #2b2b2b
Foreground: #ffffff
Primary: #0078d4 (KDE Blue)
Secondary: #3c3c3c
Border: #555555
Success: #388e3c
Error: #d32f2f
```

### Layout
- **Tab-basiert**: Stream | Einstellungen | nginx-rtmp
- **Preview**: Live-Vorschau 640x360 (min) bis 1280x720 (max)
- **Controls**: Große, Touch-friendly Buttons
- **Log**: Scrollable QTextEdit (max 120px Höhe)

### Accessibility
- Keyboard-Shortcuts: Ctrl+S (Start), Ctrl+Q (Quit)
- Screen-Reader-freundlich
- Hoher Kontrast

---

## 🏗️ Architektur-Entscheidungen

### Threading-Model
```
Main Thread (Qt Event Loop)
    ├── UI Updates
    └── Signal/Slot Connections
        
GStreamer Pipeline Thread
    ├── GLib.MainLoop (für GStreamer-Events)
    └── QThread für Pipeline-Management
    
Signals zwischen Threads:
    - pyqtSignal für Thread-sichere Kommunikation
    - new_frame_signal: GStreamer → UI (Preview)
    - error_signal: GStreamer → UI (Fehler)
    - status_signal: StreamManager → UI (Status-Updates)
```

### State Management
```python
# Stream-Status
is_streaming: bool
is_preview_active: bool

# Current Config
current_video_source: str
current_audio_source: str
current_platform: str
rtmp_url: str
stream_key: str (verschlüsselt im Memory)
```

---

## 🔐 Sicherheit

### Stream-Keys
- **NIEMALS** in Logs ausgeben
- **NIEMALS** in Git committen
- In UI: QLineEdit.EchoMode.Password
- Im Config: Verschlüsselt speichern (python-dotenv oder Keyring)

### .gitignore Kritisch
```
*_streamkey.txt
stream_keys/
secrets/
.env
config/*_private.conf
```

---

## 🐛 Bekannte Issues & Workarounds

### Wayland Screen Capture
**Problem**: PipeWire-Portal-Dialog erscheint nicht  
**Lösung**: `media-type=video/source/screen` explizit setzen

### GStreamer Plugin-Check
**Problem**: rtmpsink nicht gefunden  
**Lösung**: `gst-plugins-ugly` installieren (Patent-Issues)

### Qt Threading
**Problem**: QPixmap in Worker-Thread  
**Lösung**: QImage in Thread → QPixmap im Main Thread

---

## 🧪 Testing-Strategie

### Unit Tests
```python
# tests/test_device_manager.py
def test_get_video_sources():
    dm = DeviceManager()
    sources = dm.get_video_sources()
    assert len(sources) > 0
```

### Integration Tests
```python
# tests/test_stream_manager.py
def test_start_stream():
    sm = StreamManager()
    success = sm.start_stream(...)
    assert success
    sm.stop_stream()
```

### Manual Testing
1. Screen Capture (PipeWire-Dialog muss erscheinen)
2. RTMP-Verbindung (zu test.local:1935)
3. Multi-Stream (zu 2+ Plattformen gleichzeitig)

---

## 📝 Code-Style

### Python
```python
# Type Hints verwenden
def start_stream(self, rtmp_url: str, stream_key: str) -> bool:
    """
    Startet den RTMP-Stream.
    
    Args:
        rtmp_url: RTMP-Server-URL
        stream_key: Stream-Schlüssel
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    pass

# Formatter: Black (line-length=88)
# Linter: Pylint
# Type Checker: mypy
```

### Qt Signals
```python
# Signal-Definitionen im Header
class StreamManager(QObject):
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    frame_signal = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()  # WICHTIG für QObject
```

---

## 🔧 Entwicklungsumgebung

### VS Code Extensions (Empfohlen)
- Python (Microsoft)
- Pylance
- Black Formatter
- GitLens
- Qt for Python (optional)

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debugging
```bash
# GStreamer Debug-Output
export GST_DEBUG=3
python src/main.py

# Verbose Logging
python src/main.py --verbose
```

---

## 🚀 Build & Deploy

### Lokal testen
```bash
source venv/bin/activate
python src/main.py
```

### PyInstaller Build (Future)
```bash
pyinstaller --onefile --windowed src/main.py
```

---

## 🤝 Git-Workflow

### Branches
- `main`: Stable releases
- `develop`: Active development
- `feature/*`: Feature-Branches

### Commit-Messages
```
🎉 Initial commit
✨ Add feature
🐛 Fix bug
♻️ Refactor code
📝 Update docs
🔧 Update config
```

---

## 📚 Wichtige GStreamer-Konzepte

### Elements
```python
Gst.ElementFactory.make("element-name", "instance-name")
```

### Pipeline States
```python
Gst.State.NULL     # Initialisiert
Gst.State.READY    # Bereit
Gst.State.PAUSED   # Pausiert
Gst.State.PLAYING  # Aktiv
```

### Caps (Capabilities)
```python
video/x-raw,format=RGB,width=1280,height=720,framerate=30/1
```

---

## 💡 Hilfreiche Claude-Prompts

### Feature implementieren
```
Implementiere [FEATURE] in TUXRTMPilot.
Beachte die Architektur (Qt Signals für Threading).
Code-Style: Type Hints, Docstrings, Black Formatter.
```

### Bug fixen
```
Fehler in [DATEI]: [BESCHREIBUNG]# 🐧 TUXRTMPilot - Claude Development Context

## 📋 Projekt-Übersicht
**TUXRTMPilot** ist ein professionelles Multi-Platform RTMP Streaming Tool für Linux/KDE.
Entwickelt in Python mit PyQt6 (UI) und GStreamer (Video/Audio-Processing).

**Autor**: Heiko Schäfer <schaefer.heiko.lb@gmail.com>  
**License**: GPL-3.0  
**Platform**: CachyOS Linux (Arch-basiert), KDE Plasma  
**Version**: 1.0.0 (in Development)

---

## 🛠️ Tech Stack

### Core
- **Python**: 3.10+
- **GUI Framework**: PyQt6 (6.6.0+)
- **Video/Audio Processing**: GStreamer 1.0 (via PyGObject)
- **Screen Capture**: PipeWire (Wayland-native)
- **Multi-Streaming**: nginx-rtmp-module

### Dependencies
```python
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
PyGObject>=3.46.0  # GStreamer Python Bindings
requests>=2.31.0
python-dotenv>=1.0.0
```

### System Dependencies (Arch/CachyOS)
```bash
python-pyqt6
gstreamer
gst-plugins-base
gst-plugins-good
gst-plugins-bad
gst-plugins-ugly
gst-plugin-pipewire
python-gobject
nginx-mainline
libnginx-mod-rtmp
```

---

## 📂 Projekt-Struktur
```
kde-rtmp-streamer/
├── src/
│   ├── __init__.py
│   ├── main.py                # Einstiegspunkt, GStreamer-Init
│   ├── ui/                    # PyQt6 GUI-Komponenten
│   │   ├── __init__.py
│   │   ├── main_window.py     # QMainWindow, Tab-Management
│   │   ├── stream_tab.py      # Haupt-Stream-Interface
│   │   ├── settings_tab.py    # Einstellungen, Plattform-Config
│   │   └── nginx_tab.py       # nginx-rtmp Management
│   ├── core/                  # Business Logic
│   │   ├── __init__.py
│   │   ├── stream_manager.py  # GStreamer-Pipeline, RTMP-Handling
│   │   ├── device_manager.py  # Video/Audio-Device-Erkennung
│   │   └── nginx_manager.py   # nginx-rtmp Control
│   └── utils/                 # Hilfsfunktionen
│       ├── __init__.py
│       └── config.py          # Config-Management (JSON/dotenv)
├── config/
│   └── nginx.conf.template    # nginx-rtmp Template
├── tests/
├── venv/                      # Virtuelle Umgebung (git-ignored)
├── .gitignore
├── .clinerules                # Dieser Prompt
├── README.md
├── requirements.txt
└── LICENSE
```

---

## 🎯 Features & Ziele

### ✅ Implementiert (aus mein_tictok_proggi.py)
- GStreamer-Pipeline für Screen Capture (PipeWire)
- RTMP-Streaming mit H.264 (x264enc)
- Audio/Video-Synchronisation
- Basis-Stream-Services-Konfiguration

### 🚧 In Development
- [ ] Moderne PyQt6-GUI mit Dark Mode (KDE Breeze-Style)
- [ ] Multi-Platform Streaming (Twitch, YouTube, TikTok, Facebook, Kick)
- [ ] nginx-rtmp Integration für lokales Multi-Streaming
- [ ] Video/Audio-Geräteselektion mit Live-Preview
- [ ] Stream-Preview im UI
- [ ] Persistente Einstellungen (Config-File)
- [ ] Stream-Statistics (Bitrate, FPS, Uptime)
- [ ] Recording-Funktion
- [ ] Stream-Key-Management (verschlüsselt)

---

## 🎥 GStreamer Pipeline-Architektur

### Video-Quellen
```python
# Screen Capture (Wayland/PipeWire)
"pipewiresrc media-type=video/source/screen ! videoconvert ! video/x-raw,format=RGB"

# Webcam (V4L2)
"v4l2src device=/dev/video0 ! videoconvert ! video/x-raw,format=RGB"
```

### Audio-Quellen
```python
# PulseAudio/PipeWire
"autoaudiosrc ! audioconvert ! audioresample"
```

### RTMP-Streaming-Pipeline
```python
# Video-Branch
video_source + "! videoscale ! video/x-raw,width=1280,height=720 ! " +
"x264enc bitrate=2500 speed-preset=ultrafast tune=zerolatency ! " +
"video/x-h264,profile=baseline ! queue ! mux."

# Audio-Branch  
"autoaudiosrc ! audioconvert ! audioresample ! " +
"voaacenc bitrate=128000 ! queue ! mux."

# Muxer & Sink
"flvmux name=mux ! rtmpsink location='rtmp://server/app/stream_key'"
```

---

## 📡 Stream-Services-Konfiguration
```python
STREAM_SERVICES = {
    "Benutzerdefiniert": "",
    "YouTube": "rtmp://a.rtmp.youtube.com/live2",
    "Twitch": "rtmp://live.twitch.tv/app",
    "TikTok (Custom)": "",
    "Facebook Live": "rtmps://live-api-s.facebook.com:443/rtmp/",
    "Kick": "rtmp://fra.contribute.live-video.net/app",
    "Restream.io": "rtmp://live.restream.io/live/",
    "OBS Ninja": "rtmp://localhost:1935/live"  # für nginx-rtmp
}
```

---

## 🎨 UI/UX Design-Prinzipien

### Dark Mode (KDE Breeze Dark)
```css
Background: #2b2b2b
Foreground: #ffffff
Primary: #0078d4 (KDE Blue)
Secondary: #3c3c3c
Border: #555555
Success: #388e3c
Error: #d32f2f
```

### Layout
- **Tab-basiert**: Stream | Einstellungen | nginx-rtmp
- **Preview**: Live-Vorschau 640x360 (min) bis 1280x720 (max)
- **Controls**: Große, Touch-friendly Buttons
- **Log**: Scrollable QTextEdit (max 120px Höhe)

### Accessibility
- Keyboard-Shortcuts: Ctrl+S (Start), Ctrl+Q (Quit)
- Screen-Reader-freundlich
- Hoher Kontrast

---

## 🏗️ Architektur-Entscheidungen

### Threading-Model
```
Main Thread (Qt Event Loop)
    ├── UI Updates
    └── Signal/Slot Connections
        
GStreamer Pipeline Thread
    ├── GLib.MainLoop (für GStreamer-Events)
    └── QThread für Pipeline-Management
    
Signals zwischen Threads:
    - pyqtSignal für Thread-sichere Kommunikation
    - new_frame_signal: GStreamer → UI (Preview)
    - error_signal: GStreamer → UI (Fehler)
    - status_signal: StreamManager → UI (Status-Updates)
```

### State Management
```python
# Stream-Status
is_streaming: bool
is_preview_active: bool

# Current Config
current_video_source: str
current_audio_source: str
current_platform: str
rtmp_url: str
stream_key: str (verschlüsselt im Memory)
```

---

## 🔐 Sicherheit

### Stream-Keys
- **NIEMALS** in Logs ausgeben
- **NIEMALS** in Git committen
- In UI: QLineEdit.EchoMode.Password
- Im Config: Verschlüsselt speichern (python-dotenv oder Keyring)

### .gitignore Kritisch
```
*_streamkey.txt
stream_keys/
secrets/
.env
config/*_private.conf
```

---

## 🐛 Bekannte Issues & Workarounds

### Wayland Screen Capture
**Problem**: PipeWire-Portal-Dialog erscheint nicht  
**Lösung**: `media-type=video/source/screen` explizit setzen

### GStreamer Plugin-Check
**Problem**: rtmpsink nicht gefunden  
**Lösung**: `gst-plugins-ugly` installieren (Patent-Issues)

### Qt Threading
**Problem**: QPixmap in Worker-Thread  
**Lösung**: QImage in Thread → QPixmap im Main Thread

---

## 🧪 Testing-Strategie

### Unit Tests
```python
# tests/test_device_manager.py
def test_get_video_sources():
    dm = DeviceManager()
    sources = dm.get_video_sources()
    assert len(sources) > 0
```

### Integration Tests
```python
# tests/test_stream_manager.py
def test_start_stream():
    sm = StreamManager()
    success = sm.start_stream(...)
    assert success
    sm.stop_stream()
```

### Manual Testing
1. Screen Capture (PipeWire-Dialog muss erscheinen)
2. RTMP-Verbindung (zu test.local:1935)
3. Multi-Stream (zu 2+ Plattformen gleichzeitig)

---

## 📝 Code-Style

### Python
```python
# Type Hints verwenden
def start_stream(self, rtmp_url: str, stream_key: str) -> bool:
    """
    Startet den RTMP-Stream.
    
    Args:
        rtmp_url: RTMP-Server-URL
        stream_key: Stream-Schlüssel
        
    Returns:
        True bei Erfolg, False bei Fehler
    """
    pass

# Formatter: Black (line-length=88)
# Linter: Pylint
# Type Checker: mypy
```

### Qt Signals
```python
# Signal-Definitionen im Header
class StreamManager(QObject):
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    frame_signal = pyqtSignal(QImage)
    
    def __init__(self):
        super().__init__()  # WICHTIG für QObject
```

---

## 🔧 Entwicklungsumgebung

### VS Code Extensions (Empfohlen)
- Python (Microsoft)
- Pylance
- Black Formatter
- GitLens
- Qt for Python (optional)

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debugging
```bash
# GStreamer Debug-Output
export GST_DEBUG=3
python src/main.py

# Verbose Logging
python src/main.py --verbose
```

---

## 🚀 Build & Deploy

### Lokal testen
```bash
source venv/bin/activate
python src/main.py
```

### PyInstaller Build (Future)
```bash
pyinstaller --onefile --windowed src/main.py
```

---

## 🤝 Git-Workflow

### Branches
- `main`: Stable releases
- `develop`: Active development
- `feature/*`: Feature-Branches

### Commit-Messages
```
🎉 Initial commit
✨ Add feature
🐛 Fix bug
♻️ Refactor code
📝 Update docs
🔧 Update config
```

---

## 📚 Wichtige GStreamer-Konzepte

### Elements
```python
Gst.ElementFactory.make("element-name", "instance-name")
```

### Pipeline States
```python
Gst.State.NULL     # Initialisiert
Gst.State.READY    # Bereit
Gst.State.PAUSED   # Pausiert
Gst.State.PLAYING  # Aktiv
```

### Caps (Capabilities)
```python
video/x-raw,format=RGB,width=1280,height=720,framerate=30/1
```

---

## 💡 Hilfreiche Claude-Prompts

### Feature implementieren
```
Implementiere [FEATURE] in TUXRTMPilot.
Beachte die Architektur (Qt Signals für Threading).
Code-Style: Type Hints, Docstrings, Black Formatter.
```

### Bug fixen
```
Fehler in [DATEI]: [BESCHREIBUNG]
GStreamer Pipeline: [PIPELINE-STRING]
Error-Log: [LOG]
```

### Code Review
```
Review diesen Code auf:
- Qt Best Practices
- GStreamer Memory Leaks
- Thread-Safety
- Error-Handling
```

---

## 📞 Support & Resources

- **GStreamer Docs**: https://gstreamer.freedesktop.org/documentation/
- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **nginx-rtmp**: https://github.com/arut/nginx-rtmp-module
- **GitHub Issues**: (wird erstellt nach erstem Release)

---

**Letzte Aktualisierung**: 2025-11-01  
**Claude-Version**: Sonnet 4.5

Das ist jetzt der KOMPLETTE Prompt! Speichere ihn als .clinerules oder .claude-project.md im Projekt-Root.
Habe ich jetzt noch etwas vergessen? 🤔WiederholenHSHabe ich jetzt noch etwas vergessen? 🤔 Ja Die Ordnerstucktur schön sauberhalten für Github keine neue Skriptte estellen immer ein Backup davon machen Test-Dateien wenn  nicht funtinieren aufräumenAcknowledged project organization best practices and integrated them.Der Nutzer hat absolut Recht! Ich habe wichtige Best Practices für die Projekt-Organisation vergessen:

Saubere Ordnerstruktur für GitHub - Keine temporären/Test-Dateien im Repo
Backup-Strategie - Keine neuen Skripte ohne Backup
Test-Dateien aufräumen - Wenn Tests nicht funktionieren, müssen sie weg oder repariert werden

Ich sollte das in den Prompt einbauen.Absolut richtig! 👍 Hier ist die erweiterte Version mit Best Practices:

markdown# 🐧 TUXRTMPilot - Claude Development Context

[... vorheriger Inhalt bleibt gleich bis "Projekt-Struktur" ...]

---

## 📂 Projekt-Struktur & Organisation
```
kde-rtmp-streamer/
├── src/                       # ✅ Produktions-Code
│   ├── __init__.py
│   ├── main.py
│   ├── ui/
│   ├── core/
│   └── utils/
├── tests/                     # ✅ Funktionierende Tests
│   ├── __init__.py
│   ├── test_stream_manager.py
│   └── test_device_manager.py
├── config/                    # ✅ Config-Templates
│   └── nginx.conf.template
├── docs/                      # ✅ Dokumentation
│   ├── API.md
│   └── ARCHITECTURE.md
├── backups/                   # ⚠️ LOCAL ONLY (git-ignored)
│   ├── src_backup_20251101/
│   └── ...
├── scratch/                   # ⚠️ LOCAL ONLY (git-ignored)
│   ├── test_experiments.py
│   └── ...
├── .gitignore                 # ✅ Wichtig!
├── .clinerules                # ✅ Dieser Prompt
├── README.md
└── requirements.txt

# ❌ NICHT im Repo:
venv/                          # Virtuelle Umgebung
__pycache__/                   # Python Cache
*.pyc                          # Compiled Python
.env                           # Secrets
*_test.py                      # Ad-hoc Tests (wenn nicht funktionierend)
tmp_*.py                       # Temporäre Skripte
backup_*.py                    # Old Backups
```

---

## 🧹 Saubere Repository-Regeln

### 1. ❌ **NIEMALS committen:**
```gitignore
# .gitignore - KOMPLETT

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg-info/
dist/
build/

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/settings.json         # Erlaubt: .vscode/extensions.json
.idea/
*.swp
*.swo

# Secrets
.env
.env.local
*_streamkey.txt
stream_keys/
secrets/
config/*_private.conf

# Backups & Scratch (WICHTIG!)
backups/
scratch/
tmp/
temp/
*_backup.py
*_old.py
*_test.py                      # Außer in tests/
backup_*/
old_*/

# Logs & Output
*.log
logs/
recordings/*.mp4
recordings/*.flv

# OS
.DS_Store
Thumbs.db

# Test-Artefakte (wenn Tests fehlschlagen)
.pytest_cache/
.coverage
htmlcov/
```

---

### 2. ✅ **Backup-Strategie**

#### Vor jeder größeren Änderung:
```bash
# Automatisches Backup-Script erstellen
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src "$BACKUP_DIR/"
echo "✅ Backup erstellt: $BACKUP_DIR"
EOF
chmod +x backup.sh

# Vor Änderungen ausführen:
./backup.sh
```

#### Manuelle Backups:
```bash
# Gesamtes Projekt sichern
cp -r ~/scripts/tools/kde-rtmp-streamer ~/backups/kde-rtmp-streamer_$(date +%Y%m%d)

# Nur src/ sichern
cp -r src backups/src_backup_$(date +%Y%m%d_%H%M%S)
```

#### Git-basierte Backups:
```bash
# Feature-Branch für Experimente
git checkout -b experiment/neue-feature
# ... Änderungen testen ...

# Wenn erfolgreich:
git checkout main
git merge experiment/neue-feature

# Wenn fehlgeschlagen:
git checkout main
git branch -D experiment/neue-feature  # Branch löschen
```

---

### 3. 🧪 **Test-Dateien Management**

#### ✅ Funktionierende Tests → `tests/`
```python
# tests/test_stream_manager.py
import pytest
from src.core.stream_manager import StreamManager

def test_stream_initialization():
    """Test dass StreamManager initialisiert"""
    sm = StreamManager()
    assert sm is not None

def test_start_stream_validation():
    """Test Validierung beim Stream-Start"""
    sm = StreamManager()
    # Test mit leeren Parametern sollte False returnen
    assert sm.start_stream(rtmp_url="", stream_key="") == False
```

#### ⚠️ Experimentelle Tests → `scratch/`
```python
# scratch/test_pipewire_capture.py
# Experimenteller Code, nicht für Produktion
# Wird NICHT committed!

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Quick & Dirty Test...
```

#### ❌ Fehlgeschlagene Tests → LÖSCHEN oder REPARIEREN
```bash
# Regel: Tests müssen grün sein oder weg!

# Test failed?
pytest tests/test_broken.py
# FAILED

# Option 1: Reparieren
# ... Code fixen ...

# Option 2: Löschen (wenn nicht mehr relevant)
rm tests/test_broken.py

# Option 3: Temporär deaktivieren (mit @pytest.mark.skip)
@pytest.mark.skip(reason="WIP: Feature noch nicht fertig")
def test_future_feature():
    pass
```

---

### 4. 📝 **Code-Organisation Checklist**

#### Vor jedem Git-Commit:
```bash
# 1. Teste alles
pytest tests/

# 2. Formatiere Code
black src/

# 3. Linting
pylint src/

# 4. Prüfe .gitignore
git status
# Sollte KEINE temp/backup/test-Dateien zeigen!

# 5. Aufräumen
rm -rf scratch/tmp_*
rm -rf src/*_old.py

# 6. Commit
git add .
git commit -m "✨ Add feature XY"
```

#### Wöchentliche Wartung:
```bash
# Backups älter als 30 Tage löschen
find backups/ -type d -mtime +30 -exec rm -rf {} \;

# Scratch-Ordner komplett leeren
rm -rf scratch/*

# Alte Logs löschen
find . -name "*.log" -mtime +7 -delete
```

---

## 🚨 **Claude-Instruktionen für Code-Änderungen**

### Wenn du neue Dateien erstellst:
```
❌ NICHT:
- tmp_test.py
- backup_main.py
- old_stream_manager.py
- test_something.py (außerhalb von tests/)

✅ STATTDESSEN:
- Neue Features in bestehende Files integrieren
- Oder proper benannte Module: src/core/recording.py
- Tests in tests/ mit sprechendem Namen
```

### Wenn du Code refactorst:
```
1. Erst Backup erstellen:
   ./backup.sh

2. Dann refactorn:
   - Alte Funktion → neue Funktion
   - Tests anpassen
   
3. Alte Funktion löschen (nicht auskommentieren!)

4. Tests laufen:
   pytest tests/

5. Commit:
   git commit -m "♻️ Refactor StreamManager"
```

### Wenn Tests fehlschlagen:
```
❌ NICHT: Test-Datei einfach löschen
❌ NICHT: Test auskommentieren

✅ STATTDESSEN:
1. Fehler analysieren
2. Code oder Test fixen
3. Oder: @pytest.mark.skip mit TODO-Kommentar

# Beispiel:
@pytest.mark.skip(reason="TODO: GStreamer-Mock implementieren")
def test_stream_pipeline():
    pass
```

---

## 📋 **Ordner-Struktur-Cheat-Sheet**
```
✅ COMMITTEN (GitHub):
├── src/              # Production Code
├── tests/            # Funktionierende Tests
├── config/           # Templates
├── docs/             # Doku
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE

⚠️ LOKAL BEHALTEN (nicht committen):
├── venv/             # Virtual Env
├── backups/          # Backups
├── scratch/          # Experimente
├── .env              # Secrets
└── recordings/       # Stream-Recordings

❌ LÖSCHEN (vor Commit):
├── *_test.py         # Ad-hoc Tests
├── tmp_*.py          # Temp Files
├── backup_*.py       # Old Versions
├── old_*/            # Old Folders
└── __pycache__/      # Python Cache
```

---

## 🔄 **Git-Workflow mit Sauberkeit**
```bash
# 1. Feature-Branch erstellen
git checkout -b feature/neue-funktion

# 2. Entwickeln (mit Backups!)
./backup.sh
# ... code code code ...

# 3. Aufräumen
rm -rf scratch/test_*.py
black src/
pytest tests/

# 4. Stage nur saubere Files
git add src/ tests/ docs/
# NICHT: git add . (committed evtl. Müll!)

# 5. Review
git status
git diff --staged

# 6. Commit
git commit -m "✨ Add recording feature"

# 7. Merge
git checkout main
git merge feature/neue-funktion

# 8. Feature-Branch löschen
git branch -d feature/neue-funktion

# 9. Push
git push origin main
```

---

## 💡 **Claude: Wenn du Code-Dateien generierst**

### Regeln:
1. **Immer fragen**: "Soll ich die Datei in `src/` oder `scratch/` erstellen?"
2. **Backup-Reminder**: "Vor dem Überschreiben: Backup erstellt?"
3. **Test-Files**: Wenn es ein Test ist → `tests/test_NAME.py` (nicht `test_NAME.py` in Root!)
4. **Temporär**: Experiments → in `scratch/` vorschlagen, mit Note "Nicht committen!"

### Beispiel:
User: "Erstelle eine Funktion zum Screen Recording"
Claude:
"Ich erstelle die Funktion in src/core/recorder.py.
Möchtest du vorher ein Backup erstellen? (./backup.sh)
Soll ich auch einen Test in tests/test_recorder.py anlegen?"

---

## 🎯 **Repository-Qualitäts-Checklist**

Vor jedem Push:
- [ ] `pytest tests/` läuft durch (grün)
- [ ] `black src/` durchgeführt
- [ ] Keine `tmp_*`, `backup_*`, `old_*` Files in Git
- [ ] Keine Stream-Keys oder `.env` committed
- [ ] `git status` zeigt nur gewollte Files
- [ ] README.md ist aktuell
- [ ] Commit-Message ist sprechend (Emoji + Beschreibung)

---

**Das ist jetzt KOMPLETT mit allen Best Practices!** 🎉

Habe ich jetzt noch etwas vergessen? Oder können wir loslegen? 🚀WiederholenClaude kann Fehler machen. Bitte überprüfen Sie die Antworten. Sonnet 4.5
GStreamer Pipeline: [PIPELINE-STRING]
Error-Log: [LOG]
```

### Code Review
```
Review diesen Code auf:
- Qt Best Practices
- GStreamer Memory Leaks
- Thread-Safety
- Error-Handling
```

---

## 📞 Support & Resources

- **GStreamer Docs**: https://gstreamer.freedesktop.org/documentation/
- **PyQt6 Docs**: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- **nginx-rtmp**: https://github.com/arut/nginx-rtmp-module
- **GitHub Issues**: (wird erstellt nach erstem Release)

---

**Letzte Aktualisierung**: 2025-11-01  
**Claude-Version**: Sonnet 4.5



# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TUXRTMPilot** is a multi-platform RTMP streaming tool for Linux/KDE, built with Python, PyQt6 (UI), and GStreamer (video/audio processing). It enables streaming to platforms like Twitch, YouTube, TikTok, and more using screen capture (PipeWire) or webcams.

- **Author**: Heiko Schäfer <contact@tuxhs.de>
- **License**: GPL-3.0
- **Platform**: CachyOS Linux (Arch-based), KDE Plasma
- **Status**: Phase 1 (Core Foundation) - Early Development

## Development Commands

### Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# System dependencies (Arch/CachyOS)
sudo pacman -S python-pyqt6 gstreamer gst-plugins-{base,good,bad,ugly} gst-plugin-pipewire python-gobject
```

### Running
```bash
# Run the application
python src/main.py

# Run with GStreamer debug output
GST_DEBUG=3 python src/main.py
```

### Before Making Changes
```bash
# Always create backup before major changes
./backup.sh
```

## Architecture

### Module Structure
```
src/
├── main.py              # Entry point, GStreamer initialization, plugin checks
├── ui/                  # PyQt6 GUI components
│   └── main_window.py   # Main window (currently minimal, will have tabs)
├── core/                # Business logic
│   └── device_manager.py # Video/audio device detection
└── utils/               # Utilities
    └── config.py        # Configuration management (JSON + .env)
```

### Key Components

**main.py**: Application entry point that:
- Initializes GStreamer with `Gst.init()`
- Checks for required GStreamer plugins (pipewire, x264, rtmp, etc.)
- Sets up PyQt6 application and main window
- Initializes DeviceManager and ConfigManager

**DeviceManager** (`core/device_manager.py`):
- Detects video sources: Screen capture (PipeWire) and webcams (V4L2)
- Detects audio sources: Default microphone and desktop audio monitor
- Tests device availability using GStreamer test pipelines

**ConfigManager** (`utils/config.py`):
- Stores settings in `~/.config/tuxrtmpilot/tuxrtmpilot_config.json`
- Default settings: 1280x720, 2500 bitrate, 30 fps
- **Security**: Stream keys are NEVER stored in config - only in `.env` environment variables

### Threading Model
```
Main Thread (Qt Event Loop)
    ├── UI Updates
    └── Signal/Slot Connections

GStreamer Pipeline Thread (Future)
    ├── GLib.MainLoop for GStreamer events
    └── QThread for pipeline management

Thread-safe communication:
    - Use pyqtSignal for cross-thread communication
    - QImage in worker thread → QPixmap in main thread
```

### GStreamer Pipeline Architecture

**Screen Capture Pipeline** (PipeWire):
```python
"pipewiresrc media-type=video/source/screen ! videoconvert ! video/x-raw,format=RGB"
```

**RTMP Streaming Pipeline Structure**:
```python
# Video branch
"videoscale ! video/x-raw,width=1280,height=720 ! "
"x264enc bitrate=2500 speed-preset=ultrafast tune=zerolatency ! "
"video/x-h264,profile=baseline ! queue ! mux."

# Audio branch
"autoaudiosrc ! audioconvert ! audioresample ! "
"voaacenc bitrate=128000 ! queue ! mux."

# Muxer & sink
"flvmux name=mux ! rtmpsink location='rtmp://server/app/stream_key'"
```

**Important GStreamer Concepts**:
- Pipeline states: NULL → READY → PAUSED → PLAYING
- Always clean up: set pipeline to NULL state before destroying
- Use `Gst.parse_launch()` for quick pipeline construction
- Check plugin availability with `Gst.Registry.get().find_plugin()`

### Supported Streaming Platforms
```python
STREAM_SERVICES = {
    "YouTube": "rtmp://a.rtmp.youtube.com/live2",
    "Twitch": "rtmp://live.twitch.tv/app",
    "Facebook Live": "rtmps://live-api-s.facebook.com:443/rtmp/",
    "Kick": "rtmp://fra.contribute.live-video.net/app",
    "Restream.io": "rtmp://live.restream.io/live/",
}
```

## Critical Security Rules

### Stream Keys
- **NEVER** log stream keys
- **NEVER** commit stream keys to git
- **NEVER** store in config files - only in `.env` (git-ignored)
- In UI: Use `QLineEdit.EchoMode.Password`
- Access via `ConfigManager.get_stream_key(platform)`

### Repository Hygiene
**NEVER commit**:
- Backup files (`*_backup.py`, `*_old.py`, `backup_*/`)
- Temporary/test files (`*_test.py` outside tests/, `tmp_*`)
- Secrets (`.env`, `*_streamkey.txt`, `secrets/`)
- Build artifacts (`__pycache__/`, `*.pyc`, `venv/`)
- Logs and recordings (`*.log`, `recordings/`)

**Before every commit**:
1. Run `./backup.sh` if making major changes
2. Clean up: `rm -rf scratch/tmp_* src/*_old.py`
3. Check: `git status` should show only intentional files
4. Remove non-functional test files or fix them

## Code Style

### Python Standards
- Use type hints: `def start_stream(self, rtmp_url: str, stream_key: str) -> bool:`
- Docstrings for all public methods (Google style)
- Formatter: Black (line-length=88)
- Use German comments/messages if preferred by user (already in use)

### PyQt6 Patterns
```python
class MyClass(QObject):
    # Define signals at class level
    error_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # CRITICAL for QObject
```

### Error Handling
- Always catch GStreamer pipeline errors
- Provide user-friendly error messages in German
- Use status signals to communicate errors to UI

## Known Issues & Workarounds

### Wayland Screen Capture
- **Issue**: PipeWire portal dialog may not appear
- **Solution**: Set `media-type=video/source/screen` explicitly in pipewiresrc

### GStreamer Plugins
- **Issue**: "rtmpsink not found"
- **Solution**: Install `gst-plugins-ugly` (patent-encumbered codecs)

### Qt Threading
- **Issue**: Cannot create QPixmap in worker thread
- **Solution**: Create QImage in thread, convert to QPixmap in main thread

## Development Workflow

### Feature Development
1. Create backup: `./backup.sh`
2. Create feature branch: `git checkout -b feature/name`
3. Implement with type hints and docstrings
4. Test manually (no automated tests yet in Phase 1)
5. Clean up temporary files
6. Commit with emoji: `git commit -m "✨ Add feature"`
7. Merge to main when stable

### Commit Message Convention
```
🎉 Initial commit
✨ Add feature
🐛 Fix bug
♻️ Refactor code
📝 Update docs
🔧 Update config
```

## Current Development Phase

**Phase 1: Core Foundation** (Current)
- ✅ GStreamer initialization and plugin detection
- ✅ Device detection (screen capture, webcams, audio)
- ✅ Configuration management
- ✅ Basic PyQt6 window
- 🚧 Stream manager implementation (next)
- 🚧 Tab-based UI (Stream/Settings/nginx-rtmp)
- 🚧 RTMP streaming functionality

**Future Phases**:
- Multi-platform streaming with nginx-rtmp
- Live preview in UI
- Stream statistics (bitrate, FPS, uptime)
- Recording functionality
- Encrypted stream key storage

## Important Notes for Claude Code

1. **Always create backups** before making significant changes to `src/`
2. **Test GStreamer pipelines** carefully - syntax errors can cause segfaults
3. **Never hardcode stream keys** - always use environment variables
4. **Preserve German UI text** if already present (user preference)
5. **Keep repository clean** - remove experimental files before suggesting commits
6. **Check GStreamer plugin availability** before using elements
7. **Use Qt signals** for thread-safe communication between GStreamer and UI

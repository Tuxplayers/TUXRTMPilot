#!/bin/bash
# TUXRTMPilot Backup Script
# Erstellt automatisches Backup des src/ Ordners

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r src "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup erstellt: $BACKUP_DIR"

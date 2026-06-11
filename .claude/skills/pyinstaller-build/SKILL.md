# PyInstaller Build Skill

Package the AI Check application as a standalone executable.

## Trigger

Use this skill when:
- Building the application for distribution
- Creating installer packages
- Debugging packaging issues

## Instructions

### Prerequisites

```bash
pip install pyinstaller
```

### Configuration

#### Basic spec file (ai_check.spec)

```python
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Project root
root = Path(SPECPATH)

a = Analysis(
    ['ai_check/main.py'],
    pathex=[str(root)],
    binaries=[],
    datas=[
        # Include config files
        ('ai_check/config/default_config.yaml', 'ai_check/config'),
        # Include resources if any
        # ('ai_check/app/resources/*', 'ai_check/app/resources'),
    ],
    hiddenimports=[
        # Explicit imports that might be missed
        'onnxruntime',
        'cv2',
        'numpy',
        'PIL',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'loguru',
        'yaml',
        'imagehash',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AICheck',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Use UPX compression if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon (if available)
    # icon='resources/icon.ico',
)
```

### Build Commands

#### Development Build

```bash
# Quick build (debug mode, console enabled)
pyinstaller ai_check/main.py --name AICheck --windowed --onedir
```

#### Production Build

```bash
# Using spec file
pyinstaller ai_check.spec --clean

# Or command line
pyinstaller ai_check/main.py \
    --name AICheck \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --add-data "ai_check/config/default_config.yaml;ai_check/config" \
    --hidden-import onnxruntime \
    --hidden-import cv2 \
    --exclude-module tkinter \
    --exclude-module matplotlib
```

#### Single File Build

```bash
# Creates a single exe (slower startup)
pyinstaller ai_check/main.py \
    --name AICheck \
    --windowed \
    --onefile \
    --clean
```

### Handling Issues

#### Missing Modules

If you get "ModuleNotFoundError" at runtime:

```python
# Add to hiddenimports in spec file
hiddenimports=[
    'missing_module',
    'missing_module.submodule',
],
```

#### Missing Data Files

```python
# Add to datas in spec file
datas=[
    ('path/to/data/file', 'destination/in/package'),
],
```

#### ONNX Model Issues

ONNX models should be loaded at runtime from user data directory:

```python
# Don't bundle models - let users download them
# Or include in datas:
datas=[
    ('models/*.onnx', 'models'),
],
```

#### OpenCV Issues

```python
# Add OpenCV data files
import cv2
cv2_data = cv2.__path__[0]
datas=[
    (f'{cv2_data}/qt/plugins/*', 'cv2/qt/plugins'),
],
```

### Testing the Build

```bash
# Run the built executable
./dist/AICheck/AICheck.exe

# Or on Linux/macOS
./dist/AICheck/AICheck
```

### Distribution

#### Windows

```bash
# Create installer with NSIS or Inno Setup
# Or use:
pip install pynsist
```

#### macOS

```bash
# Create .app bundle
pyinstaller ai_check.spec --target-arch macosx

# Create DMG
hdiutil create -volname "AICheck" -srcfolder dist/AICheck.app dist/AICheck.dmg
```

#### Linux

```bash
# Create AppImage
# Or just distribute the dist/ folder as tar.gz
tar -czvf aicheck-linux.tar.gz -C dist AICheck
```

### Size Optimization

```python
# In spec file, exclude more:
excludes=[
    'tkinter', 'matplotlib', 'IPython', 'jupyter',
    'pytest', 'sphinx', 'black', 'isort', 'mypy',
    'torch.distributions',  # If not used
    'transformers.models.*',  # If only using specific models
],
```

## Example Usage

```
Build AICheck for Windows:
1. Create the spec file
2. Include all necessary hidden imports
3. Exclude development dependencies
4. Test the executable
5. Report the final size
```

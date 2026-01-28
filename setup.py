"""
Setup script for building Caesar Cipher App as macOS application using py2app.

Usage:
    python setup.py py2app          # Build production app
    python setup.py py2app -A       # Build in alias mode (for testing)
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,  # Don't emulate command line arguments
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'Caesar Cipher',
        'CFBundleDisplayName': 'Caesar Cipher',
        'CFBundleGetInfoString': 'Decrypt and analyze classical ciphers',
        'CFBundleIdentifier': 'com.evanbushnell.caesarcipher',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2026 Evan Bushnell',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra or later
    },
    'packages': [
        'tkinter',
    ],
    'includes': [
        'app',
        'cipher',
        'theme',
        'widgets',
        'analysis_panel',
        'vigenere_detect',
        'substitution_helper',
        'config',
        'utils',
        'samples',
        'scoring',
    ],
    'excludes': [
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
        'setuptools',
        'pip',
        'wheel',
    ],
}

setup(
    name='Caesar Cipher',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# --- Collect Data Files ---
added_files = [
    ('assets', 'assets'),          
    ('styles', 'styles'),          
    ('fonts', 'fonts'),            
    ('config.json', '.')           
]

# --- Analysis Configuration ---
a = Analysis(
    ['main.py'],                   
    pathex=[],                     
    binaries=[],                  
    datas=added_files,             
    hiddenimports=[                
        'PyQt6.sip',
        'PyQt6.QtMultimedia',
        'asyncio',                 
        'queue',                   
        'pydub.utils',             
        'pydub.scipy_effects',
        'pydub.effects',
    ],
    hookspath=[],                  
    runtime_hooks=[],              
    excludes=['PyQt5', 'tkinter', 'matplotlib', 'IPython', 'pytest'],  # Explicitly exclude PyQt5 and other unnecessary packages
    win_no_prefer_redirects=False, 
    win_private_assemblies=False,  
    cipher=block_cipher,           
    noarchive=False                
)

# --- PYZ Archive ---
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

# --- EXE Creation ---
exe = EXE(
    pyz,
    a.scripts,
    [],                            
    exclude_binaries=True,         
    name='ChunTTS',                
    debug=True,                   
    bootloader_ignore_signals=False,
    strip=False,                   
    upx=True,                      
    upx_dir='C:\\upx-4.2.4-win64',  
    runtime_tmpdir=None,           
    console=False,                 
    windowed=True,                 
    icon='assets\\logo\\favicon.ico'
)

# --- Collect Files for Distribution ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ChunTTS'                
)
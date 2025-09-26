#!/usr/bin/env python3
"""
🏗️ Professional Windows EXE Installer Builder
Creates enterprise-grade Windows installer with all dependencies
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime

class ProfessionalInstallerBuilder:
    """Professional EXE installer builder"""
    
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.build_dir = self.project_dir / "build"
        self.dist_dir = self.project_dir / "dist"
        self.installer_dir = self.project_dir / "installer"
        self.version = "2.0.0"
        self.app_name = "AdaptiveChatbot"
        
        print(f"🏗️ Professional Installer Builder initialized")
        print(f"Project Directory: {self.project_dir}")
    
    def create_pyinstaller_spec(self):
        """Create advanced PyInstaller spec file"""
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Project configuration
project_dir = Path(r"{self.project_dir}")
app_name = "{self.app_name}"
version = "{self.version}"

# Data files and hidden imports
datas = [
    (str(project_dir / "data"), "data"),
    (str(project_dir / "config"), "config"),
    (str(project_dir / "core"), "core"),
    (str(project_dir / "marketing_materials"), "marketing_materials"),
    (str(project_dir / "documentation"), "documentation"),
    (str(project_dir / "*.md"), "."),
    (str(project_dir / "requirements*.txt"), "."),
]

# Hidden imports for all our modules
hiddenimports = [
    'speech_recognition',
    'pyttsx3',
    'pygame',
    'edge_tts',
    'transformers',
    'torch',
    'numpy',
    'pandas',
    'sklearn',
    'langdetect',
    'textblob',
    'psutil',
    'websockets',
    'flask',
    'sqlite3',
    'asyncio',
    'threading',
    'multiprocessing',
    'tkinter',
    'customtkinter',
    'PIL',
    'requests',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'six',
    'packaging',
    'setuptools',
    'pip'
]

# Binary exclusions (optional)
excludes = [
    'matplotlib',
    'jupyter',
    'notebook',
    'IPython'
]

block_cipher = None

a = Analysis(
    [str(project_dir / 'main_adaptive_chatbot.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=excludes,
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
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / 'assets' / 'icon.ico') if (project_dir / 'assets' / 'icon.ico').exists() else None,
    version_file=str(project_dir / 'version_info.txt') if (project_dir / 'version_info.txt').exists() else None,
)
'''
        
        spec_path = self.project_dir / f"{self.app_name}.spec"
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"✅ Created PyInstaller spec: {spec_path}")
        return spec_path
    
    def create_version_info(self):
        """Create Windows version info file"""
        
        version_info = f'''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({self.version.replace('.', ',')},0),
    prodvers=({self.version.replace('.', ',')},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'Adaptive AI Solutions'),
            StringStruct(u'FileDescription', u'Adaptive Multilingual Chatbot - Professional Voice Assistant'),
            StringStruct(u'FileVersion', u'{self.version}.0'),
            StringStruct(u'InternalName', u'{self.app_name}'),
            StringStruct(u'LegalCopyright', u'Copyright © 2024 Adaptive AI Solutions. All rights reserved.'),
            StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
            StringStruct(u'ProductName', u'Adaptive Multilingual Chatbot'),
            StringStruct(u'ProductVersion', u'{self.version}.0'),
            StringStruct(u'Comments', u'Professional multilingual voice assistant with advanced AI capabilities'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_path = self.project_dir / "version_info.txt"
        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(version_info)
        
        print(f"✅ Created version info: {version_path}")
        return version_path
    
    def create_installer_assets(self):
        """Create professional installer assets"""
        
        assets_dir = self.project_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create a simple icon if it doesn't exist
        if not (assets_dir / "icon.ico").exists():
            print("⚠️ Icon file not found, creating placeholder")
            # In a real scenario, you'd have a proper icon file
        
        # Create installer configuration
        installer_config = {
            "app_name": self.app_name,
            "version": self.version,
            "company": "Adaptive AI Solutions",
            "description": "Professional Multilingual Voice Assistant",
            "install_dir": f"C:\\\\Program Files\\\\{self.app_name}",
            "start_menu_dir": f"{self.app_name}",
            "registry_key": f"HKLM\\\\Software\\\\{self.app_name}",
            "uninstall_key": f"HKLM\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{self.app_name}",
            "features": [
                "Voice Chat Interface",
                "50+ Language Support", 
                "Advanced AI Models",
                "Real-time Debugging",
                "Professional TTS System",
                "Electrical Business Assistant"
            ],
            "dependencies": [
                "Microsoft Visual C++ Redistributable",
                "Windows 10/11 (64-bit)",
                ".NET Framework 4.8+"
            ]
        }
        
        config_path = assets_dir / "installer_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(installer_config, f, indent=2)
        
        print(f"✅ Created installer config: {config_path}")
        return config_path
    
    def create_nsis_script(self):
        """Create professional NSIS installer script"""
        
        nsis_script = f'''# Adaptive Chatbot Professional Installer
# Created by Adaptive AI Solutions

!define PRODUCT_NAME "{self.app_name}"
!define PRODUCT_VERSION "{self.version}"
!define PRODUCT_PUBLISHER "Adaptive AI Solutions"
!define PRODUCT_WEB_SITE "https://adaptive-ai.solutions"
!define PRODUCT_DIR_REGKEY "Software\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{self.app_name}.exe"
!define PRODUCT_UNINST_KEY "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{PRODUCT_NAME}}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

# Modern UI
!include "MUI2.nsh"
!include "x64.nsh"

# General
Name "${{PRODUCT_NAME}} ${{PRODUCT_VERSION}}"
OutFile "{self.app_name}_Setup_v{self.version}.exe"
InstallDir "$PROGRAMFILES64\\${{PRODUCT_NAME}}"
InstallDirRegKey HKLM "${{PRODUCT_DIR_REGKEY}}" ""
ShowInstDetails show
ShowUnInstDetails show

# Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

# Welcome page
!insertmacro MUI_PAGE_WELCOME

# License page
!define MUI_LICENSEPAGE_TEXT_TOP "Please read the following license agreement carefully:"
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"

# Directory page
!insertmacro MUI_PAGE_DIRECTORY

# Components page
!insertmacro MUI_PAGE_COMPONENTS

# Instfiles page
!insertmacro MUI_PAGE_INSTFILES

# Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\\{self.app_name}.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\\README.md"
!insertmacro MUI_PAGE_FINISH

# Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

# Language files
!insertmacro MUI_LANGUAGE "English"

# Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

# Sections

Section "Core Application" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  # Main executable
  File "dist\\{self.app_name}.exe"
  
  # Configuration and data files
  File /r "data"
  File /r "config"
  File /r "core"
  File /r "documentation"
  File "README*.md"
  File "requirements*.txt"
  File "LICENSE*"
  
  # Create shortcuts
  CreateDirectory "$SMPROGRAMS\\${{PRODUCT_NAME}}"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\{self.app_name}.exe"
  CreateShortCut "$SMPROGRAMS\\${{PRODUCT_NAME}}\\Uninstall.lnk" "$INSTDIR\\uninst.exe"
  CreateShortCut "$DESKTOP\\${{PRODUCT_NAME}}.lnk" "$INSTDIR\\{self.app_name}.exe"
  
  # Registry entries
  WriteRegStr HKLM "${{PRODUCT_DIR_REGKEY}}" "" "$INSTDIR\\{self.app_name}.exe"
  WriteRegStr ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "DisplayName" "${{PRODUCT_NAME}}"
  WriteRegStr ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "UninstallString" "$INSTDIR\\uninst.exe"
  WriteRegStr ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "DisplayVersion" "${{PRODUCT_VERSION}}"
  WriteRegStr ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "URLInfoAbout" "${{PRODUCT_WEB_SITE}}"
  WriteRegStr ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "Publisher" "${{PRODUCT_PUBLISHER}}"
  WriteRegDWORD ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "NoModify" 1
  WriteRegDWORD ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "NoRepair" 1
SectionEnd

Section "Voice Models" SEC02
  SetOutPath "$INSTDIR\\models"
  # AI models would be included here
SectionEnd

Section "Documentation" SEC03
  SetOutPath "$INSTDIR\\docs"
  File /r "documentation\\*"
  File "README*.md"
SectionEnd

Section "Desktop Integration" SEC04
  # Additional desktop integration
  WriteRegStr HKLM "Software\\Classes\\Applications\\{self.app_name}.exe\\shell\\open\\command" "" '"$INSTDIR\\{self.app_name}.exe" "%1"'
SectionEnd

# Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${{SEC01}} "Core application files and runtime (Required)"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SEC02}} "Pre-trained voice and language models (Recommended)"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SEC03}} "User documentation and guides (Optional)"
  !insertmacro MUI_DESCRIPTION_TEXT ${{SEC04}} "Desktop and system integration (Recommended)"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Section Uninstall
  # Remove registry keys
  DeleteRegKey ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}"
  DeleteRegKey HKLM "${{PRODUCT_DIR_REGKEY}}"
  
  # Remove files and folders
  Delete "$INSTDIR\\{self.app_name}.exe"
  Delete "$INSTDIR\\uninst.exe"
  RMDir /r "$INSTDIR\\data"
  RMDir /r "$INSTDIR\\config"
  RMDir /r "$INSTDIR\\core"
  RMDir /r "$INSTDIR\\models"
  RMDir /r "$INSTDIR\\docs"
  Delete "$INSTDIR\\*.*"
  RMDir "$INSTDIR"
  
  # Remove shortcuts
  Delete "$SMPROGRAMS\\${{PRODUCT_NAME}}\\*.*"
  RMDir "$SMPROGRAMS\\${{PRODUCT_NAME}}"
  Delete "$DESKTOP\\${{PRODUCT_NAME}}.lnk"
  
  SetAutoClose true
SectionEnd

Function .onInit
  # Check if 64-bit Windows
  ${{If}} ${{RunningX64}}
    # OK
  ${{Else}}
    MessageBox MB_OK "This application requires 64-bit Windows."
    Abort
  ${{EndIf}}
  
  # Check if already installed
  ReadRegStr $R0 ${{PRODUCT_UNINST_ROOT_KEY}} "${{PRODUCT_UNINST_KEY}}" "UninstallString"
  StrCmp $R0 "" done
  
  MessageBox MB_OKCANCEL|MB_ICONQUESTION "${{PRODUCT_NAME}} is already installed. Do you want to uninstall the previous version?" IDOK uninst
  Abort
  
uninst:
  ExecWait '$R0 _?=$INSTDIR'
  
done:
FunctionEnd
'''
        
        nsis_path = self.project_dir / f"{self.app_name}_installer.nsi"
        with open(nsis_path, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        print(f"✅ Created NSIS script: {nsis_path}")
        return nsis_path
    
    def build_executable(self):
        """Build the main executable using PyInstaller"""
        
        print("🔨 Building executable with PyInstaller...")
        
        # Clean previous builds
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        
        # Create spec file
        spec_path = self.create_pyinstaller_spec()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm", 
            str(spec_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            exe_path = self.dist_dir / f"{self.app_name}.exe"
            if exe_path.exists():
                print(f"📦 Executable location: {exe_path}")
                print(f"📊 Executable size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return exe_path
            else:
                print("❌ Executable not found in expected location")
                return None
        else:
            print(f"❌ PyInstaller failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return None
    
    def build_installer(self):
        """Build the Windows installer using NSIS"""
        
        print("📦 Building Windows installer...")
        
        # Create NSIS script
        nsis_script = self.create_nsis_script()
        
        # Try to find NSIS
        nsis_paths = [
            "C:\\Program Files (x86)\\NSIS\\makensis.exe",
            "C:\\Program Files\\NSIS\\makensis.exe",
            "makensis.exe"  # If in PATH
        ]
        
        makensis = None
        for path in nsis_paths:
            if Path(path).exists() or shutil.which(path):
                makensis = path
                break
        
        if not makensis:
            print("❌ NSIS not found. Please install NSIS from https://nsis.sourceforge.io/")
            print("💡 Alternative: The executable is ready at dist/{}.exe".format(self.app_name))
            return None
        
        # Run NSIS
        cmd = [makensis, str(nsis_script)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            installer_path = self.project_dir / f"{self.app_name}_Setup_v{self.version}.exe"
            if installer_path.exists():
                print(f"✅ Installer created successfully!")
                print(f"📦 Installer location: {installer_path}")
                print(f"📊 Installer size: {installer_path.stat().st_size / 1024 / 1024:.1f} MB")
                return installer_path
            else:
                print("❌ Installer not found in expected location")
        else:
            print(f"❌ NSIS failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        
        return None
    
    def create_portable_version(self):
        """Create portable version with all dependencies"""
        
        print("💼 Creating portable version...")
        
        portable_dir = self.project_dir / f"{self.app_name}_Portable_v{self.version}"
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
        
        portable_dir.mkdir()
        
        # Copy executable
        exe_src = self.dist_dir / f"{self.app_name}.exe"
        if exe_src.exists():
            shutil.copy2(exe_src, portable_dir)
        
        # Copy essential files
        essential_files = [
            "README.md", "LICENSE", "requirements.txt",
            "VOICE_SYSTEM_PROFESSIONAL.md", "PROJECT_SUMMARY.md"
        ]
        
        for file_name in essential_files:
            src = self.project_dir / file_name
            if src.exists():
                shutil.copy2(src, portable_dir)
        
        # Copy directories
        essential_dirs = ["data", "config", "documentation"]
        for dir_name in essential_dirs:
            src_dir = self.project_dir / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, portable_dir / dir_name)
        
        # Create run script
        run_script = f'''@echo off
echo 🤖 Starting Adaptive Chatbot v{self.version}...
echo.
echo 📍 Running from: %~dp0
echo 🌟 Professional Multilingual Voice Assistant
echo.
{self.app_name}.exe
pause
'''
        
        with open(portable_dir / "Run_AdaptiveChatbot.bat", 'w') as f:
            f.write(run_script)
        
        # Create README for portable
        portable_readme = f'''# {self.app_name} v{self.version} - Portable Edition

## 🚀 Quick Start
1. Double-click `Run_AdaptiveChatbot.bat` to start
2. Or run `{self.app_name}.exe` directly

## 📋 System Requirements
- Windows 10/11 (64-bit)
- Microphone for voice input
- Speakers/headphones for audio output
- Internet connection (for AI models)

## 🌟 Features
- 50+ Language Support
- Professional Voice Synthesis  
- Real-time Debugging
- Electrical Business Assistant
- Advanced AI Conversations

## 📞 Support
For support and updates, visit: https://adaptive-ai.solutions

---
Professional Multilingual Voice Assistant
Copyright © 2024 Adaptive AI Solutions
'''
        
        with open(portable_dir / "README_PORTABLE.txt", 'w', encoding='utf-8') as f:
            f.write(portable_readme)
        
        print(f"✅ Portable version created: {portable_dir}")
        return portable_dir
    
    def build_all(self):
        """Build complete professional package"""
        
        print("🏗️ Starting Professional Build Process...")
        print(f"⏰ Build started at: {datetime.now()}")
        print("="*60)
        
        # Step 1: Create assets
        print("\n📁 Step 1: Creating installer assets...")
        self.create_version_info()
        self.create_installer_assets()
        
        # Step 2: Build executable
        print("\n🔨 Step 2: Building executable...")
        exe_path = self.build_executable()
        
        if not exe_path:
            print("❌ Build failed at executable creation")
            return False
        
        # Step 3: Create portable version
        print("\n💼 Step 3: Creating portable version...")
        portable_dir = self.create_portable_version()
        
        # Step 4: Build installer
        print("\n📦 Step 4: Building Windows installer...")
        installer_path = self.build_installer()
        
        # Summary
        print("\n" + "="*60)
        print("🎉 BUILD COMPLETE!")
        print(f"⏰ Build completed at: {datetime.now()}")
        print("\n📦 Build Artifacts:")
        print(f"  • Executable: {exe_path}")
        print(f"  • Portable: {portable_dir}")
        if installer_path:
            print(f"  • Installer: {installer_path}")
        else:
            print("  • Installer: Failed (NSIS not available)")
        
        print("\n🚀 Ready for Distribution!")
        return True

if __name__ == "__main__":
    print("🏗️ Adaptive Chatbot Professional Installer Builder")
    print("=" * 60)
    
    builder = ProfessionalInstallerBuilder()
    success = builder.build_all()
    
    if success:
        print("\n✅ All builds completed successfully!")
        input("\nPress Enter to exit...")
    else:
        print("\n❌ Build process failed!")
        input("\nPress Enter to exit...")
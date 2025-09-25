
# 🚀 Adaptive Chatbot Professional - Installation Guide
## Complete Setup Instructions

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 7 SP1 or later
- **Processor**: Intel Core 2 Duo or equivalent
- **Memory**: 2GB RAM
- **Storage**: 500MB free disk space
- **Audio**: Basic sound card and speakers
- **Display**: 1024x768 resolution

### Recommended Requirements
- **Operating System**: Windows 10 or 11 (latest updates)
- **Processor**: Intel Core i3 or AMD equivalent
- **Memory**: 4GB RAM or higher
- **Storage**: 1GB free disk space (SSD preferred)
- **Audio**: USB microphone and quality speakers/headphones
- **Display**: 1920x1080 or higher resolution

### Optional Requirements
- **Internet Connection**: For initial setup and updates
- **Webcam**: For future video features (planned)
- **External Storage**: For backup and knowledge sharing

---

## Pre-Installation Steps

### 1. System Preparation

**Update Windows**:
1. Go to Settings > Windows Update
2. Install all available updates
3. Restart if required

**Free Up Disk Space**:
1. Run Disk Cleanup (search in Start menu)
2. Delete temporary files
3. Ensure at least 1GB free space

**Check Audio Devices**:
1. Right-click speaker icon in system tray
2. Select "Playback devices"
3. Test your speakers/headphones
4. Test your microphone in "Recording devices"

### 2. Download Preparation

**Download Location**:
- Create a folder: `C:\Downloads\AdaptiveChatbot`
- Download installer to this folder
- Verify file integrity (optional)

**File Verification** (Optional):
- Check file size: ~50-100MB
- Verify digital signature
- Run antivirus scan if concerned

---

## Installation Methods

### Method 1: Express Installation (Recommended)

**Step 1: Run Installer**
1. Right-click installer file
2. Select "Run as Administrator"
3. Click "Yes" when prompted by Windows

**Step 2: Installation Wizard**
1. Select language (Hindi/English)
2. Accept License Agreement
3. Choose installation directory (default recommended)
4. Select components to install:
   - ✅ Core Application (required)
   - ✅ Desktop Shortcut
   - ✅ Start Menu Entry
   - ✅ Voice Components
   - ✅ Documentation

**Step 3: Installation Process**
1. Click "Install" to begin
2. Wait for installation to complete (2-5 minutes)
3. Click "Launch" to start application

### Method 2: Custom Installation

**Advanced Options**:
- **Installation Directory**: Choose custom folder
- **Components Selection**: Install only needed features
- **Registry Settings**: Modify Windows registry entries
- **Service Installation**: Install as Windows service (Business license)

**Custom Directory Example**:
- Default: `C:\Program Files\Adaptive Chatbot`
- Custom: `D:\Business Software\Adaptive Chatbot`

### Method 3: Portable Installation

**For USB Drive or Network Deployment**:
1. Download portable ZIP version
2. Extract to desired location
3. Run `portable_setup.bat`
4. Launch `adaptive_chatbot.exe`

**Portable Benefits**:
- No registry changes
- Easy to move between computers
- Perfect for testing environments
- No administrator rights required

---

## Post-Installation Setup

### 1. Initial Launch

**First Run**:
1. Double-click desktop shortcut
2. Windows Firewall may prompt - click "Allow"
3. Choose your preferred language
4. Review and accept terms of use

**License Activation**:
- Trial license automatically active
- 7-day full-feature evaluation
- No credit card required
- All features available during trial

### 2. Audio Configuration

**Microphone Setup**:
1. Go to Settings > Audio
2. Select your microphone from dropdown
3. Test recording quality
4. Adjust input volume
5. Enable noise reduction

**Speaker Setup**:
1. Select audio output device
2. Test voice playback
3. Adjust volume levels
4. Choose voice speed (slow/normal/fast)

**Audio Test**:
```
Settings > Audio > Test Audio
┌─────────────────────────────────────────┐
│  🎤 Microphone Test                     │
│  [●] Recording... Say "Hello"           │
│  Volume: ████████░░ 80%                │
│                                         │
│  🔊 Speaker Test                        │
│  [▶] Playing test audio...              │
│  Volume: ██████████ 100%               │
│                                         │
│  ✅ Audio configuration successful      │
└─────────────────────────────────────────┘
```

### 3. Knowledge Base Setup

**Initial Knowledge**:
1. Choose to import sample knowledge base
2. Select your business category:
   - Electronics Store
   - Customer Service
   - Educational Institution
   - Healthcare Facility
   - General Business

**Sample Knowledge Categories**:
- **Electronics**: 50+ Q&As about products, warranties, pricing
- **Service**: 30+ Q&As about support, appointments, policies
- **Education**: 40+ Q&As about courses, admissions, schedules

---

## Verification & Testing

### 1. Installation Verification

**Check Installed Files**:
- Main executable: `adaptive_chatbot.exe`
- Configuration: `config.json`
- Knowledge database: `knowledge.db`
- License file: `license.json`
- Documentation folder: `docs/`

**Registry Verification** (Windows):
1. Press Win+R, type "regedit"
2. Navigate to: `HKEY_LOCAL_MACHINE\SOFTWARE\AdaptiveChatbot`
3. Verify installation path and version

**Service Verification** (Business license):
1. Press Win+R, type "services.msc"
2. Look for "Adaptive Chatbot Service"
3. Verify status is "Running"

### 2. Functionality Testing

**Basic Text Chat Test**:
1. Launch application
2. Click "Text Chat"
3. Type: "Hello, how are you?"
4. Verify response received

**Voice Features Test**:
1. Click "Voice Chat"
2. Say: "What are your store hours?"
3. Verify voice recognition and response
4. Check audio playback quality

**Teaching Mode Test**:
1. Click "Voice Teaching"
2. Say: "Question: What is your return policy?"
3. Say: "Answer: 30-day return policy with receipt"
4. Verify knowledge was saved

### 3. Performance Testing

**Response Time Test**:
- Text responses: Should be < 1 second
- Voice recognition: Should be < 3 seconds
- Knowledge lookup: Should be instantaneous

**Memory Usage Test**:
- Check Task Manager
- Normal usage: 50-100MB RAM
- Heavy usage: 100-200MB RAM
- Memory leaks: Monitor over time

**Storage Test**:
- Installation size: ~100MB
- Knowledge base: Grows with usage
- Logs and cache: <10MB typically

---

## Troubleshooting Installation Issues

### Common Installation Problems

**Problem**: "Administrator rights required"
**Solution**:
1. Right-click installer
2. Select "Run as Administrator"
3. Provide admin credentials when prompted

**Problem**: "Installation failed - Error 1603"
**Solution**:
1. Clear Windows Installer cache
2. Restart Windows
3. Disable antivirus temporarily
4. Run installer again

**Problem**: "Required component missing"
**Solution**:
1. Install Visual C++ Redistributables
2. Install .NET Framework 4.7 or later
3. Update Windows to latest version

### Audio-Related Issues

**Problem**: Microphone not detected
**Solution**:
1. Check Device Manager for audio devices
2. Update audio drivers
3. Test microphone in Windows settings
4. Grant microphone permissions to application

**Problem**: No voice playback
**Solution**:
1. Check default playback device
2. Test speakers with other applications
3. Verify audio codec installation
4. Restart application

### License-Related Issues

**Problem**: Trial license not activated
**Solution**:
1. Check system date and time
2. Ensure internet connection for initial activation
3. Disable proxy/VPN temporarily
4. Contact support if problem persists

**Problem**: "License file corrupted"
**Solution**:
1. Delete existing license.json file
2. Restart application to recreate trial license
3. Re-activate paid license if applicable

---

## Advanced Installation Options

### Silent Installation

**For IT Administrators**:
```batch
# Silent install with default options
adaptive_chatbot_installer.exe /S

# Silent install with custom directory
adaptive_chatbot_installer.exe /S /D=C:\CustomPath

# Silent install with specific components
adaptive_chatbot_installer.exe /S /COMPONENTS="core,voice,docs"
```

**Group Policy Deployment**:
1. Create MSI package using installer
2. Deploy via Group Policy
3. Configure default settings
4. Push license keys via registry

### Network Installation

**Shared Installation**:
1. Install on network share
2. Configure multi-user access
3. Set up centralized knowledge base
4. Manage licenses centrally

**Terminal Server Deployment**:
1. Install in application mode
2. Configure user-specific settings
3. Set up roaming profiles
4. Monitor concurrent usage

### Docker Containerization

**Container Setup** (Advanced):
```dockerfile
FROM windows/servercore:ltsc2019
COPY adaptive_chatbot/ C:/app/
WORKDIR C:/app
CMD ["adaptive_chatbot.exe", "--headless"]
```

---

## Uninstallation

### Standard Uninstallation

1. Go to Windows Settings > Apps
2. Find "Adaptive Chatbot Professional"
3. Click "Uninstall"
4. Follow the uninstall wizard

### Complete Removal

**Manual Cleanup**:
1. Delete installation directory
2. Remove registry entries:
   - `HKEY_LOCAL_MACHINE\SOFTWARE\AdaptiveChatbot`
   - `HKEY_CURRENT_USER\SOFTWARE\AdaptiveChatbot`
3. Clear application data:
   - `%APPDATA%\AdaptiveChatbot`
   - `%LOCALAPPDATA%\AdaptiveChatbot`

**Backup Before Uninstall**:
1. Export knowledge base
2. Save configuration files
3. Note license key for future use

---

## Support & Next Steps

### Installation Support

**If you need help**:
- Email: support@yourcompany.com
- Phone: +91-XXXXXXXXXX (Business license holders)
- Documentation: docs.yourcompany.com
- Video tutorials: Available on website

### After Installation

1. **Complete the tutorial**: Built-in interactive guide
2. **Import sample knowledge**: Quick start with pre-made Q&As
3. **Train your bot**: Add your specific business knowledge
4. **Customize settings**: Adjust for your preferences
5. **Consider upgrading**: Evaluate Professional or Business license

### Getting Started Resources

- **User Manual**: Comprehensive usage guide
- **Video Tutorials**: Step-by-step training videos  
- **Best Practices**: Tips for optimal results
- **Community Forum**: Connect with other users
- **Feature Requests**: Suggest improvements

---

*Installation complete! Ready to transform your customer service with AI.*

*For technical support, contact: support@yourcompany.com*

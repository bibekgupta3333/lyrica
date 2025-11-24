# Mobile App Setup Guide

Complete setup guide for the React Native mobile app.

## 📱 Prerequisites

### Common Requirements
- Node.js 20+
- pnpm 8+
- Watchman (recommended)

### iOS Development (macOS only)
- macOS 12+
- Xcode 14+
- CocoaPods
- iOS Simulator or physical iOS device

### Android Development
- JDK 17+
- Android Studio
- Android SDK (API 34+)
- Android Emulator or physical Android device

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
cd lyrica-mobile
pnpm install
```

### 2. Platform-Specific Setup

#### iOS Setup (macOS only)

```bash
# Install CocoaPods (if not installed)
sudo gem install cocoapods

# Install iOS dependencies
cd ios
pod install
cd ..

# Run on iOS
pnpm ios

# Or run on specific simulator
pnpm ios --simulator="iPhone 15 Pro"
```

#### Android Setup

1. **Install Android Studio**: https://developer.android.com/studio

2. **Set up Android SDK**:
   - Open Android Studio
   - Go to Settings → Appearance & Behavior → System Settings → Android SDK
   - Install Android 14.0 (API 34)
   - Install Android SDK Build-Tools

3. **Configure Environment Variables** (add to `~/.zshrc` or `~/.bash_profile`):

```bash
export ANDROID_HOME=$HOME/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

4. **Create Android Emulator** (or connect physical device):
   - Open Android Studio
   - Go to Tools → Device Manager
   - Create a new Virtual Device (e.g., Pixel 6)

5. **Run on Android**:

```bash
# Start emulator first (or connect device)
# Then run:
pnpm android
```

## 🏃 Running the App

### Start Metro Bundler

```bash
cd lyrica-mobile
pnpm start
```

This starts the Metro bundler on port 8081.

### Run on iOS (in another terminal)

```bash
pnpm ios
```

### Run on Android (in another terminal)

```bash
pnpm android
```

## 🔧 Development

### Hot Reload
- Press `r` in Metro terminal to reload
- Press `d` to open developer menu
- Shake device to open developer menu (on physical device)

### Developer Menu
- **iOS Simulator**: Cmd + D
- **Android Emulator**: Cmd + M (macOS) or Ctrl + M (Windows/Linux)

### Debug Mode
1. Open Developer Menu
2. Select "Debug"
3. Chrome DevTools will open

### Clear Cache

```bash
# Clear Metro cache
pnpm start --reset-cache

# Clear all caches
rm -rf node_modules
rm -rf ios/Pods
rm -rf android/.gradle
pnpm install
cd ios && pod install && cd ..
```

## 🐛 Troubleshooting

### Metro Bundler Port in Use

```bash
# Kill process on port 8081
lsof -ti:8081 | xargs kill -9

# Or use
pnpm start --port 8082
```

### iOS Build Fails

```bash
# Clean iOS build
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*
pod deintegrate
pod install
cd ..

# Rebuild
pnpm ios
```

### Android Build Fails

```bash
# Clean Android build
cd android
./gradlew clean
cd ..

# Clear gradle cache
rm -rf ~/.gradle/caches/

# Rebuild
pnpm android
```

### Cannot Connect to Metro Bundler (Android)

```bash
# Reverse the port
adb reverse tcp:8081 tcp:8081

# Check if device is connected
adb devices
```

### App Crashes on Startup

```bash
# Uninstall app
# iOS
xcrun simctl uninstall booted com.lyrica

# Android
adb uninstall com.lyrica

# Clear everything and reinstall
rm -rf node_modules
pnpm install
pnpm ios  # or pnpm android
```

### Watchman Issues (macOS)

```bash
# Reinstall watchman
brew uninstall watchman
brew install watchman
watchman watch-del-all
```

## 📂 Project Structure

```
lyrica-mobile/
├── android/              # Android native code
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/lyrica/
│   │   │   ├── res/      # Resources
│   │   │   └── AndroidManifest.xml
│   │   └── build.gradle
│   └── build.gradle
├── ios/                  # iOS native code
│   ├── Lyrica/
│   ├── Lyrica.xcodeproj/
│   ├── Lyrica.xcworkspace/
│   └── Podfile
├── src/
│   ├── screens/          # Screen components
│   ├── components/       # Reusable components
│   ├── services/         # API services
│   ├── navigation/       # Navigation setup
│   └── App.tsx           # Root component
├── index.js              # Entry point
└── package.json
```

## 🌐 Connecting to Backend

The mobile app connects to the backend API at `http://localhost:8000`.

### On Physical Device

You'll need to update the API URL to your machine's IP address:

1. Find your local IP:
   ```bash
   # macOS
   ipconfig getifaddr en0
   
   # Linux
   hostname -I
   ```

2. Update API URL in app code or use environment variable

3. Make sure your device is on the same network

## 📚 Resources

- [React Native Docs](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [Android Developer Guide](https://developer.android.com/)
- [iOS Developer Guide](https://developer.apple.com/ios/)

## 💡 Tips

1. **Use Real Device for Testing**: Physical devices provide better performance testing
2. **Keep Metro Running**: Faster reload times
3. **Use Flipper**: Great debugging tool (install separately)
4. **Check Logs**:
   - iOS: `xcrun simctl spawn booted log stream --level debug`
   - Android: `adb logcat`

---

Happy coding! 📱✨


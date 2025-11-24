# Lyrica Mobile - React Native

React Native mobile application for the Lyrica lyrics generator.

## 🚀 Quick Start

### Prerequisites

- Node.js 20+
- Watchman (for macOS)
- Xcode 14+ (for iOS development)
- Android Studio (for Android development)
- CocoaPods (for iOS dependencies)

### Installation

```bash
# Install dependencies
pnpm install

# iOS only: Install pods
cd ios && pod install && cd ..
```

### Running the App

#### iOS

```bash
# Start Metro bundler
pnpm start

# In another terminal, run iOS
pnpm ios

# Or run on specific simulator
pnpm ios --simulator="iPhone 15 Pro"
```

#### Android

```bash
# Start Metro bundler
pnpm start

# In another terminal, run Android
pnpm android

# Or run on specific emulator
pnpm android --deviceId=emulator-5554
```

### Development

```bash
# Start Metro bundler with cache reset
pnpm start --reset-cache

# Run on device
pnpm ios --device
pnpm android --deviceId=<device-id>

# Lint
pnpm lint

# Format code
pnpm format

# Run tests
pnpm test
```

## 📁 Project Structure

```
lyrica-mobile/
├── src/
│   ├── screens/          # Screen components
│   │   └── HomeScreen.tsx
│   ├── components/       # Reusable components
│   ├── services/         # API services
│   ├── navigation/       # Navigation setup
│   ├── utils/            # Utilities
│   └── App.tsx           # Root component
├── android/              # Android native code
├── ios/                  # iOS native code
├── index.js              # Entry point
└── package.json
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
API_URL=http://localhost:8000/api/v1
WS_URL=ws://localhost:8000/ws
```

### iOS Setup

1. Install Xcode from App Store
2. Install CocoaPods:
   ```bash
   sudo gem install cocoapods
   ```
3. Install pods:
   ```bash
   cd ios && pod install
   ```

### Android Setup

1. Install Android Studio
2. Install Android SDK (API 34+)
3. Configure environment variables:
   ```bash
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/emulator
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   ```

## 🎯 Features

- **Native Performance**: Built with React Native CLI
- **Modern Navigation**: React Navigation 6
- **TypeScript**: Full type safety
- **Dark Mode**: Automatic theme detection
- **API Integration**: Axios for backend communication
- **Offline Support**: Coming soon

## 📱 Screens

- **Home**: Main screen with features overview
- **Generate**: Lyrics generation interface (coming soon)
- **History**: View past generations (coming soon)
- **Settings**: App configuration (coming soon)

## 🐛 Troubleshooting

### Metro Bundler Issues

```bash
# Clear Metro cache
pnpm start --reset-cache

# Clear watchman
watchman watch-del-all
```

### iOS Build Issues

```bash
# Clean build
cd ios
xcodebuild clean
rm -rf ~/Library/Developer/Xcode/DerivedData/*
pod deintegrate
pod install
cd ..
```

### Android Build Issues

```bash
# Clean build
cd android
./gradlew clean
cd ..

# Reset app data
adb uninstall com.lyrica
```

### Port Already in Use

```bash
# Kill process on port 8081
lsof -ti:8081 | xargs kill -9
```

## 📚 Resources

- [React Native Docs](https://reactnative.dev/)
- [React Navigation](https://reactnavigation.org/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run linting and tests
4. Submit a pull request

---

Built with React Native ⚛️


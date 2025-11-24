# Figma Design Prompt for Lyrica Web App

## 🎯 Project Overview

**Project Name**: Lyrica - AI-Powered Complete Song Generator  
**Platform**: Web Application (Next.js)  
**Design System**: Component-based, scalable, responsive  
**Target Users**: Music creators, songwriters, hobbyists, content creators

### Core Functionality
Lyrica is an AI-powered platform that generates complete songs including:
- 🎵 Song lyrics (AI-generated with multiple agents)
- 🎤 Vocal synthesis (customizable voice and pitch)
- 🎹 Instrumental music (genre-matched composition)
- 🎼 Professional mixing and mastering

---

## 🎨 Design System & Color Palette

### Primary Color Palette (Music Industry Standard)

#### Base Colors
```
Primary Brand Color (Purple - Creativity & Music):
- Primary 900: #1E0A3C (Deep Purple - Headers, CTAs)
- Primary 700: #4C1D95 (Purple - Active states)
- Primary 500: #8B5CF6 (Vibrant Purple - Main actions)
- Primary 300: #C4B5FD (Light Purple - Hover states)
- Primary 100: #EDE9FE (Very Light Purple - Backgrounds)

Secondary Color (Teal - Technology & Innovation):
- Secondary 700: #0F766E (Dark Teal - Secondary CTAs)
- Secondary 500: #14B8A6 (Teal - Accents)
- Secondary 300: #5EEAD4 (Light Teal - Highlights)
- Secondary 100: #CCFBF1 (Very Light Teal - Info backgrounds)

Accent Color (Pink/Magenta - Audio/Sound):
- Accent 600: #DB2777 (Hot Pink - Important actions)
- Accent 400: #F472B6 (Pink - Visual feedback)
- Accent 200: #FBCFE8 (Light Pink - Subtle highlights)
```

#### Neutral Colors
```
Neutrals (Gray scale):
- Gray 900: #111827 (Almost Black - Text)
- Gray 800: #1F2937 (Dark Gray - Secondary text)
- Gray 700: #374151 (Medium Gray - Tertiary text)
- Gray 500: #6B7280 (Mid Gray - Disabled states)
- Gray 300: #D1D5DB (Light Gray - Borders)
- Gray 100: #F3F4F6 (Very Light Gray - Backgrounds)
- Gray 50: #F9FAFB (Almost White - Cards)
- White: #FFFFFF (Pure White - Backgrounds)
```

#### Semantic Colors
```
Success (Green):
- Success 700: #15803D
- Success 500: #22C55E
- Success 100: #DCFCE7

Warning (Amber):
- Warning 700: #B45309
- Warning 500: #F59E0B
- Warning 100: #FEF3C7

Error (Red):
- Error 700: #B91C1C
- Error 500: #EF4444
- Error 100: #FEE2E2

Info (Blue):
- Info 700: #1D4ED8
- Info 500: #3B82F6
- Info 100: #DBEAFE
```

#### Audio-Specific Colors
```
Waveform Colors:
- Primary Waveform: #8B5CF6 (Purple)
- Secondary Waveform: #14B8A6 (Teal)
- Progress: #DB2777 (Pink)
- Background: #1F2937 (Dark Gray)

Track Colors (Multi-track interface):
- Vocal Track: #F472B6 (Pink)
- Music Track: #8B5CF6 (Purple)
- Bass Track: #14B8A6 (Teal)
- Drums Track: #F59E0B (Amber)
```

### Dark Mode Palette
```
Dark Background:
- BG Primary: #0F172A (Navy Black)
- BG Secondary: #1E293B (Slate)
- BG Tertiary: #334155 (Medium Slate)

Dark Text:
- Text Primary: #F1F5F9
- Text Secondary: #CBD5E1
- Text Tertiary: #94A3B8
```

---

## 📱 Screens to Design

### 1. Landing Page / Home
**Purpose**: First impression, value proposition, conversion

**Sections**:
- Hero Section
  - Headline: "Create Complete Songs with AI"
  - Subheadline: "From lyrics to vocals to music - in minutes"
  - Primary CTA: "Start Creating" (Large button)
  - Secondary CTA: "Listen to Examples"
  - Hero visual: Animated waveform or song generation preview
  
- Features Grid (3 columns)
  - 🎤 Voice Synthesis
  - 🎹 Music Generation
  - 🎼 Professional Mixing
  - Each with icon, title, description
  
- How It Works (Step-by-step)
  - Step 1: Enter your idea
  - Step 2: AI generates lyrics
  - Step 3: Choose voice and music style
  - Step 4: Download your song
  - Visual flow diagram with icons
  
- Example Songs Showcase
  - Horizontal scrolling cards
  - Each card: thumbnail, title, genre, play button
  - Audio player embedded
  
- Pricing/Plans (Optional)
  - Free, Pro, Enterprise tiers
  - Feature comparison
  
- Footer
  - Links, social media, newsletter signup

**Components Needed**:
- `Hero` component
- `FeatureCard` component
- `StepItem` component
- `SongCard` component
- `Footer` component
- `Navbar` component (sticky)

---

### 2. Authentication Pages

#### Login Page
**Layout**: Split screen or centered card

**Elements**:
- Logo
- "Welcome Back" heading
- Email input
- Password input
- "Remember me" checkbox
- "Forgot password?" link
- Login button (primary)
- Social login options (Google, GitHub)
- "Don't have an account? Sign up" link

#### Sign Up Page
**Layout**: Similar to login

**Elements**:
- Logo
- "Create Account" heading
- Full name input
- Email input
- Password input
- Confirm password input
- Terms & conditions checkbox
- Sign up button (primary)
- Social signup options
- "Already have an account? Login" link

**Components**:
- `AuthLayout` component
- `Input` component (with validation states)
- `Button` component (primary, secondary, social)
- `Checkbox` component
- `Link` component

---

### 3. Dashboard / Home Screen (After Login)

**Layout**: Sidebar navigation + main content area

**Sidebar**:
- Logo
- Navigation items:
  - 🏠 Dashboard
  - 🎵 Generate Song
  - 📚 My Library
  - 🎤 Voice Gallery
  - ⚙️ Settings
  - 👤 Profile
- User profile section at bottom

**Main Content**:
- Welcome message with user name
- Quick stats cards (4 cards):
  - Total Songs Created
  - Songs This Month
  - Favorite Genre
  - Total Listen Time
  
- Quick Actions (Large buttons):
  - "Generate New Song" (primary, prominent)
  - "Continue Last Project"
  - "Explore Voice Profiles"
  
- Recent Songs (Grid or List)
  - Song cards with:
    - Album art / waveform thumbnail
    - Title
    - Date created
    - Duration
    - Play button (overlay on hover)
    - Options menu (edit, download, delete)
  
- Activity Feed / History
  - Timeline of recent actions

**Components**:
- `Sidebar` component
- `NavItem` component
- `StatCard` component
- `ActionButton` component
- `SongCard` component
- `ActivityItem` component

---

### 4. Song Generation Page

**Layout**: Multi-step wizard or single page form

**Step 1: Lyrics Input**
- Heading: "Let's Create Your Song"
- Input options:
  - Text area: "Describe your song idea" (large)
  - Genre dropdown (Pop, Rock, Hip-Hop, Country, etc.)
  - Mood dropdown (Happy, Sad, Energetic, Calm, etc.)
  - Theme/Topic input (optional)
  - BPM slider (40-220)
  - Key selector (C, D, E, F, G, A, B with major/minor)
  
- Advanced options (collapsible):
  - Song structure selector (Verse-Chorus-Verse, AABA, etc.)
  - Target duration (2-5 minutes)
  - Language selector
  
- "Generate Lyrics" button (primary)

**Step 2: Lyrics Review & Edit**
- Generated lyrics display (editable)
- Section labels (Verse 1, Chorus, Verse 2, Bridge, etc.)
- Quality scores (badges):
  - Rhyme Score: 0.87
  - Creativity: 0.92
  - Coherence: 0.89
  
- Actions:
  - "Regenerate All" button
  - "Regenerate Section" (per section)
  - "Edit Manually" (inline editing)
  - "Continue to Voice" button (primary)

**Step 3: Voice Selection**
- Voice profile gallery (grid of cards)
- Each card:
  - Avatar/icon
  - Voice name
  - Gender, age range, accent info
  - Sample play button
  - Rating stars
  - "Select" button
  
- Voice settings panel:
  - Pitch adjustment slider (-12 to +12 semitones)
  - Tempo control slider
  - Vocal effects toggles:
    - Reverb (with intensity slider)
    - Echo
    - Compression
    - Warmth
  
- Preview button: "Preview with this voice" (plays sample)
- "Continue to Music" button (primary)

**Step 4: Music Selection**
- Music style selector (visual cards):
  - Each card: genre image, name, description
  - Pop, Rock, Hip-Hop, Electronic, Jazz, Classical, etc.
  
- Music parameters:
  - Instrumental intensity slider (minimal to full band)
  - Music mood slider
  - Instrumentation checkboxes:
    - Guitar, Piano, Drums, Bass, Strings, Synth, etc.
  
- Preview button: "Preview instrumental" (plays sample)
- "Generate Song" button (large, primary)

**Step 5: Generation Progress**
- Full-screen progress modal
- Progress bar with percentage (0-100%)
- Current stage indicator:
  - ✓ Lyrics Generated
  - ⏳ Generating Vocals... (animated)
  - ⏹ Generating Music...
  - ⏹ Mixing Tracks...
  - ⏹ Mastering Audio...
  
- Live preview (if possible):
  - Waveform animation
  - Estimated time remaining
  
- "Cancel" button (secondary)

**Step 6: Song Result**
- Full-screen player interface
- Large waveform visualizer (animated during playback)
- Song metadata display:
  - Title (editable)
  - Duration
  - Genre, mood, BPM, key
  
- Playback controls:
  - Play/Pause (large button)
  - Progress bar (seekable)
  - Time display (current / total)
  - Volume slider
  - Loop button
  
- Quality scores display:
  - Audio Quality: 0.94
  - Mixing Quality: 0.89
  
- Action buttons:
  - "Download" (with format selector: MP3, WAV, OGG)
  - "Save to Library"
  - "Share"
  - "Regenerate Vocals"
  - "Regenerate Music"
  - "Remix"
  - "Edit Settings"
  
- Track breakdown (expandable):
  - Vocal track waveform (mute/solo)
  - Instrumental track waveform (mute/solo)
  - Each with volume slider

**Components**:
- `WizardStep` component
- `TextArea` component
- `Dropdown` component
- `Slider` component
- `VoiceCard` component
- `MusicStyleCard` component
- `ProgressModal` component
- `AudioPlayer` component (complex)
- `Waveform` component
- `PlaybackControls` component
- `TrackControl` component

---

### 5. Song Library Page

**Layout**: Grid or list view toggle

**Header**:
- "My Library" heading
- View toggle (grid/list icons)
- Sort dropdown (Recent, Oldest, Most Played, Title A-Z)
- Filter dropdowns (Genre, Mood, Date Range)
- Search bar (with icon)

**Content Area**:
- Song cards (in grid or list)
- Each card:
  - Album art / waveform thumbnail
  - Title
  - Date created
  - Duration
  - Genre tag
  - Play count
  - Like button (heart icon)
  - Play button (primary, on hover)
  - Options menu (3 dots):
    - Edit
    - Download
    - Share
    - Add to Playlist
    - Delete
    
- Pagination or infinite scroll

**Empty State** (if no songs):
- Illustration
- "No songs yet"
- "Create your first song" button

**Components**:
- `ViewToggle` component
- `FilterBar` component
- `SongCard` (grid version)
- `SongListItem` (list version)
- `OptionsMenu` component
- `EmptyState` component
- `Pagination` component

---

### 6. Voice Gallery Page

**Layout**: Gallery grid with filters

**Header**:
- "Voice Gallery" heading
- Search bar
- Filters:
  - Gender (Male, Female, Neutral)
  - Age Range (Child, Teen, Young Adult, Adult, Senior)
  - Accent (American, British, Australian, etc.)
  - Language
  - Premium toggle

**Content**:
- Voice profile cards (grid, 3-4 columns)
- Each card:
  - Avatar/icon (illustrated or abstract)
  - Voice name
  - Description (short)
  - Characteristics tags (gender, age, accent)
  - Sample waveform mini-visualization
  - Play sample button
  - Rating (stars)
  - Usage count
  - "Premium" badge (if applicable)
  - "Select Voice" button

**Side Panel** (when voice selected):
- Voice details:
  - Full description
  - Technical specs (base pitch, range)
  - Sample audio player (longer sample)
  - User reviews/ratings
  - "Use This Voice" button (primary)

**Components**:
- `VoiceCard` component
- `FilterBar` component
- `VoiceDetailPanel` component
- `AudioSamplePlayer` component
- `RatingDisplay` component
- `Badge` component

---

### 7. Music Studio / Mixing Page

**Layout**: Professional DAW-inspired interface

**Top Bar**:
- Song title
- Save button
- Export button
- Back to library link

**Main Area**:
- Timeline view (horizontal)
- Multiple tracks (vertical):
  - Vocal Track
  - Instrumental Track
  - Bass Track
  - Drums Track (if separate)
  
- Each track:
  - Track name
  - Waveform visualization
  - Mute button
  - Solo button
  - Volume fader (vertical)
  - Pan knob
  - Effects button
  
- Playhead (vertical line that moves)
- Timeline markers (verse, chorus indicators)

**Bottom Player Bar**:
- Play/Pause
- Stop
- Record (optional)
- Loop section
- Tempo display
- Time signature
- Master volume

**Right Panel** (Inspector):
- Selected track settings:
  - EQ controls (Low, Mid, High)
  - Compressor
  - Reverb
  - Delay
  - Custom effects chain
  
- Master controls:
  - Master volume
  - Master EQ
  - Master compression
  - Limiter

**Components**:
- `Timeline` component
- `Track` component
- `WaveformTrack` component
- `Fader` component
- `Knob` component
- `EffectPanel` component
- `TransportControls` component

---

### 8. Settings Page

**Layout**: Two-column (sidebar menu + content)

**Sidebar Menu**:
- Account
- Audio Preferences
- Privacy & Security
- Notifications
- Billing (if applicable)
- Help & Support

**Content Sections**:

#### Account Settings
- Profile photo upload
- Full name input
- Email input
- Username input
- Bio textarea
- "Save Changes" button

#### Audio Preferences
- Default audio format (dropdown)
- Default audio quality (Low, Medium, High)
- Default BPM (slider)
- Default genre (dropdown)
- Auto-save toggle
- Download location

#### Privacy & Security
- Change password section
- Two-factor authentication toggle
- Session management (active sessions list)
- Data export button
- Delete account button (danger)

#### Notifications
- Email notifications toggle
- Push notifications toggle
- Notification preferences:
  - Song generation complete
  - New features
  - Tips & tutorials
  - Marketing emails

**Components**:
- `SettingsLayout` component
- `SettingsSidebar` component
- `SettingsSection` component
- `ProfilePhotoUpload` component
- `Toggle` component
- `DangerZone` component

---

### 9. User Profile Page

**Layout**: Profile header + content tabs

**Header Section**:
- Cover photo (optional)
- Profile photo
- User name
- Username (@handle)
- Bio
- Stats:
  - Total Songs
  - Followers
  - Following
- "Edit Profile" button (if own profile)
- "Follow" button (if other user)

**Tabs**:
- Songs (grid of user's public songs)
- Playlists
- Liked Songs
- Activity

**Components**:
- `ProfileHeader` component
- `StatItem` component
- `TabNav` component
- `SongGrid` component

---

### 10. Search Results Page

**Layout**: Search bar + filters + results

**Header**:
- Search bar (with query)
- Result count: "142 results for 'pop music'"

**Filters** (left sidebar):
- Content type:
  - Songs
  - Users
  - Playlists
  - Voice Profiles
- Genre
- Mood
- Date range

**Results Area**:
- Mixed results or categorized
- Songs section
- Users section
- Voice profiles section
- "Show more" buttons

**Components**:
- `SearchBar` component
- `FilterSidebar` component
- `SearchResultCard` component
- `UserCard` component

---

## 🎨 Component Library

### Core Components

#### Buttons
```
Variants:
- Primary (filled, purple gradient)
- Secondary (outlined, purple border)
- Tertiary (ghost, no border)
- Danger (filled, red)
- Success (filled, green)

Sizes:
- xs (24px height)
- sm (32px height)
- md (40px height)
- lg (48px height)
- xl (56px height)

States:
- Default
- Hover
- Active/Pressed
- Disabled
- Loading (with spinner)

Icons:
- Icon only
- Icon left
- Icon right
```

#### Inputs
```
Types:
- Text input
- Email input
- Password input (with show/hide)
- Number input
- Search input (with icon)
- Textarea

States:
- Default
- Focus
- Error (with error message)
- Disabled
- Success

Variants:
- Outlined
- Filled
```

#### Dropdowns / Selects
```
- Single select
- Multi-select
- Searchable dropdown
- Grouped options
- Custom option renderer
```

#### Sliders
```
- Single value slider
- Range slider
- With value display
- With markers/ticks
- Vertical slider (for volume)
```

#### Cards
```
- Song card (with thumbnail, title, actions)
- Voice card (with avatar, sample player)
- Stat card (with icon, number, label)
- Feature card (with icon, title, description)
- Info card (with dismiss)
```

#### Modals / Dialogs
```
- Confirmation modal
- Info modal
- Full-screen modal
- Bottom sheet (mobile)
- Sizes: sm, md, lg, full
```

#### Navigation
```
- Top navbar (with logo, links, user menu)
- Sidebar navigation (collapsible)
- Tab navigation (horizontal)
- Breadcrumbs
- Pagination
```

#### Feedback Components
```
- Toast notifications (success, error, warning, info)
- Alert banners
- Progress bar
- Loading spinner
- Skeleton loaders
```

#### Audio Components
```
- Audio player (with controls)
- Waveform visualizer
- Spectrum analyzer
- Volume meter
- Track control (with fader)
- Playback controls (play, pause, skip)
```

#### Data Display
```
- Tables (sortable, filterable)
- Lists (with icons, actions)
- Badges (for tags, status)
- Avatars (user, default)
- Rating stars
- Chips (removable tags)
```

---

## 📐 Layout & Spacing

### Grid System
```
- 12-column grid
- Breakpoints:
  - xs: 0-640px
  - sm: 640-768px
  - md: 768-1024px
  - lg: 1024-1280px
  - xl: 1280-1536px
  - 2xl: 1536px+

- Container max-width: 1440px
- Gutter: 24px
```

### Spacing Scale
```
- 4px (0.25rem) - xs
- 8px (0.5rem) - sm
- 12px (0.75rem) - md-sm
- 16px (1rem) - md
- 24px (1.5rem) - lg
- 32px (2rem) - xl
- 48px (3rem) - 2xl
- 64px (4rem) - 3xl
- 96px (6rem) - 4xl
```

### Border Radius
```
- 4px - sm (buttons, inputs)
- 8px - md (cards)
- 12px - lg (modals)
- 16px - xl (large cards)
- 9999px - full (pills, avatars)
```

---

## 🔤 Typography

### Font Family
```
Primary Font: Inter or DM Sans (modern, clean)
Monospace Font: JetBrains Mono (for technical data)
```

### Font Sizes
```
- text-xs: 12px / 1rem
- text-sm: 14px / 1.25rem
- text-base: 16px / 1.5rem (body text)
- text-lg: 18px / 1.75rem
- text-xl: 20px / 2rem
- text-2xl: 24px / 2.5rem
- text-3xl: 30px / 3rem (page headings)
- text-4xl: 36px / 3.5rem
- text-5xl: 48px / 4rem (hero headings)
- text-6xl: 60px / 1 (extra large)
```

### Font Weights
```
- light: 300
- normal: 400
- medium: 500
- semibold: 600
- bold: 700
- extrabold: 800
```

### Line Heights
```
- tight: 1.25
- normal: 1.5
- relaxed: 1.75
- loose: 2
```

---

## 🎭 Animations & Interactions

### Micro-interactions
```
- Button hover: scale(1.02) + shadow increase
- Card hover: scale(1.03) + shadow increase
- Play button: pulse animation
- Waveform: animated bars
- Progress bar: smooth transition
- Loading: spinner rotation
- Success: checkmark animation
- Error: shake animation
```

### Transitions
```
- Duration: 150ms (fast), 300ms (normal), 500ms (slow)
- Easing: ease-in-out, cubic-bezier
```

### Page Transitions
```
- Fade in/out
- Slide in from right (for modals)
- Scale up (for dialogs)
```

---

## ♿ Accessibility Requirements

### Contrast Ratios
```
- Normal text: minimum 4.5:1
- Large text: minimum 3:1
- UI components: minimum 3:1
```

### Focus States
```
- All interactive elements must have visible focus indicators
- Focus ring: 2px solid color with offset
```

### ARIA Labels
```
- All icon buttons must have aria-label
- Form inputs must have labels
- Complex components need proper ARIA attributes
```

### Keyboard Navigation
```
- Tab order must be logical
- All actions accessible via keyboard
- Escape closes modals
- Arrow keys for sliders
```

---

## 📱 Responsive Design

### Mobile (320px - 767px)
```
- Single column layout
- Hamburger menu
- Stack all components vertically
- Full-width buttons
- Simplified navigation
- Bottom tab bar for main actions
```

### Tablet (768px - 1023px)
```
- Two-column layout where appropriate
- Sidebar can be collapsible
- Larger touch targets
```

### Desktop (1024px+)
```
- Multi-column layouts
- Sidebar always visible
- Hover states
- Larger components
```

---

## 🎯 Design Priorities

1. **Audio-First Design**: Waveforms, visualizers, and audio controls should be prominent and beautiful
2. **Clarity**: Complex features (mixing, generation) should be intuitive
3. **Speed**: Perception of speed with loading states and progress indicators
4. **Delight**: Micro-animations and smooth transitions
5. **Accessibility**: WCAG 2.1 AA compliance minimum
6. **Consistency**: Use design system components throughout
7. **Scalability**: Components should work at any scale

---

## 📦 Deliverables

### Required Figma Files

1. **Design System File**
   - Color palette (all shades)
   - Typography scale
   - Component library (all variants)
   - Icons library
   - Spacing system
   - Grid system

2. **Screens File**
   - All 10+ screens designed
   - Desktop versions (1440px)
   - Tablet versions (768px)
   - Mobile versions (375px)
   - Dark mode versions
   - All states (empty, loading, error, success)

3. **Prototypes**
   - User flow for song generation (end-to-end)
   - Login/signup flow
   - Song playback interactions
   - Navigation between screens

4. **Developer Handoff**
   - All components with specs
   - Spacing measurements
   - Color codes (HEX, RGB)
   - Font specifications
   - Export assets (icons, images)

---

## 🚀 Implementation Notes

### Component Naming Convention
```
Use BEM or similar:
- Block: .song-card
- Element: .song-card__title
- Modifier: .song-card--featured
```

### CSS Framework Recommendation
```
Tailwind CSS (for utility-first approach)
or
Styled Components (for component-scoped styles)
```

### Icon Library
```
Heroicons, Lucide Icons, or Phosphor Icons
(Modern, consistent, open source)
```

---

## 💡 Inspiration References

### Similar Apps (for reference)
- Spotify (music player, library)
- Suno AI (AI music generation)
- Soundtrap (online DAW)
- FL Studio / Ableton (mixing interface)
- Synthesia (AI voice)

### Design Systems
- Vercel Design System
- Stripe Design System
- Tailwind UI Components
- Material Design (for interaction patterns)

---

## ✅ Design Checklist

Before finalizing designs, ensure:

- [ ] All screens designed for desktop, tablet, mobile
- [ ] Dark mode versions completed
- [ ] All interactive states defined (hover, active, disabled)
- [ ] Loading and error states for all async operations
- [ ] Empty states for all list/grid views
- [ ] Accessibility contrast ratios checked
- [ ] All components in design system
- [ ] Prototype flows created for main journeys
- [ ] Design tokens documented (colors, spacing, typography)
- [ ] Icon set complete and consistent
- [ ] All text styles defined and named
- [ ] Export assets prepared for developers

---

## 🎨 Final Notes

**Design Philosophy**: 
- **Modern & Professional**: Clean, contemporary design that feels professional
- **Audio-Centric**: Waveforms, visualizers, and music elements are visual highlights
- **Intuitive**: Complex AI features made simple through clear UI
- **Delightful**: Smooth animations and satisfying interactions
- **Accessible**: Usable by everyone, regardless of ability

**Color Strategy**:
- Purple = Brand, creativity, music
- Teal = Technology, AI, innovation
- Pink/Magenta = Audio, sound, energy
- Neutrals = Professional, clean, readable

**Success Metrics**:
- Users can generate a song in < 5 minutes
- All features discoverable without tutorials
- High user satisfaction with visual design
- Fast perceived performance with loading states

---

**Ready to design? Start with the Design System, then move to high-priority screens (Landing, Song Generation, Dashboard).**

Good luck! 🎨🎵

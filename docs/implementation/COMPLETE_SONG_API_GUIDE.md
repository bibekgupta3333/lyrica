# Complete Song Generation API Guide

> **Complete REST API for end-to-end song generation with lyrics, vocals, and music**

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Endpoints](#api-endpoints)
  - [Generate Complete Songs](#generate-complete-songs)
  - [Retrieve & Download](#retrieve--download)
  - [Regenerate Components](#regenerate-components)
  - [Manage Songs](#manage-songs)
  - [Metadata & Discovery](#metadata--discovery)
- [Data Models](#data-models)
- [Workflows](#workflows)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Complete Song Generation API (`/api/v1/songs/`) provides a unified interface for creating, managing, and distributing complete AI-generated songs. It orchestrates the entire pipeline from lyric generation to final mastered audio.

### Key Features

- **🎵 End-to-End Generation**: Create complete songs from a single API call
- **🎤 Voice Synthesis**: Multiple voice profiles with pitch/effects control
- **🎹 AI Music Composition**: Genre-based instrumental generation
- **🎧 Professional Production**: Mixing and mastering pipeline
- **📥 Multi-Format Export**: WAV, MP3, OGG, FLAC, M4A
- **🔄 Component Regeneration**: Independently regenerate vocals or music
- **🎛️ Remixing**: Create variations with different settings
- **📊 Database Persistence**: Full CRUD operations on songs
- **📈 Analytics**: Play counts, downloads, engagement metrics

### Technologies

- **Backend**: FastAPI + SQLAlchemy (async)
- **Database**: PostgreSQL (Song + SongGenerationHistory models)
- **AI Agents**: LangGraph (lyrics generation)
- **Voice Synthesis**: Bark/Coqui TTS + pitch/effects
- **Music Generation**: MusicGen/AudioCraft
- **Audio Processing**: pydub + librosa

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  Complete Song Generation API                   │
│                     /api/v1/songs/*                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
     ┌───────────┼───────────┬───────────────┬────────────┐
     │           │           │               │            │
     v           v           v               v            v
┌─────────┐ ┌────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐
│ Lyrics  │ │ Voice  │ │  Music   │ │Production │ │ Database │
│ Agents  │ │  TTS   │ │ MusicGen │ │  Mixing   │ │   CRUD   │
│(LangGrp)│ │ +Pitch │ │ +Chords  │ │ Mastering │ │(Song tbl)│
└─────────┘ └────────┘ └──────────┘ └───────────┘ └──────────┘
```

### Complete Song Generation Pipeline

1. **Lyrics Generation** (30-60s)
   - Planning Agent → designs structure
   - Generation Agent → creates lyrics (RAG-enhanced)
   - Refinement Agent → improves quality
   - Evaluation Agent → scores output

2. **Voice Synthesis** (10-30s)
   - TTS generation from lyrics
   - Pitch adjustment (±12 semitones)
   - Vocal effects (reverb, EQ, compression)

3. **Music Composition** (30-90s)
   - Genre-based instrumental generation
   - Chord progression generation
   - BPM/key control
   - Structured sections (intro, verse, chorus, outro)

4. **Production** (10-20s)
   - Multi-track mixing (vocals + music)
   - Volume balancing
   - Crossfade effects
   - Final mastering (loudness normalization, EQ)

5. **Export** (5-10s)
   - Multi-format conversion
   - Preview generation (30s)
   - File storage + database persistence

**Total Time**: ~90-210 seconds (1.5-3.5 minutes) for a complete song

---

## API Endpoints

### Generate Complete Songs

#### POST `/api/v1/songs/generate`

**Generate a complete song from scratch** (WBS 2.14.1)

Orchestrates the entire pipeline: lyrics → vocals → music → mixing → mastering.

**Request Body**:
```json
{
  "lyrics_prompt": "Write a sad song about lost love",
  "genre": "pop",
  "mood": "melancholic",
  "theme": "heartbreak",
  "title": "Fading Memories",
  "artist_name": "AI Singer",
  "voice_profile_id": "female_singer_1",
  "vocal_pitch_shift": -2,
  "vocal_effects": {
    "reverb": {"room_size": 0.5, "wet_level": 0.3},
    "eq": {"low": 0, "mid": 2, "high": 1}
  },
  "bpm": 80,
  "key": "C minor",
  "music_style": "piano ballad",
  "duration_seconds": 180,
  "use_rag": true,
  "llm_provider": "ollama",
  "is_public": false
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "...",
  "title": "Fading Memories",
  "genre": "pop",
  "mood": "melancholic",
  "bpm": 80,
  "key": "C minor",
  "duration_seconds": 183.45,
  "file_info": {
    "final_audio_path": "audio_files/songs/.../song.wav",
    "vocal_track_path": "audio_files/songs/.../vocals.wav",
    "instrumental_track_path": "audio_files/songs/.../music.wav",
    "preview_path": "audio_files/songs/.../preview.wav",
    "file_size_bytes": 32145600,
    "duration_seconds": 183.45
  },
  "generation_status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:33:15Z"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/songs/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "lyrics_prompt": "Write an upbeat song about summer",
    "genre": "pop",
    "voice_profile_id": "female_singer_1",
    "bpm": 120,
    "duration_seconds": 180
  }'
```

---

#### POST `/api/v1/songs/generate-quick`

**Quick song generation** with minimal parameters (simplified interface).

**Request Body**:
```json
{
  "prompt": "A happy song about sunshine",
  "voice": "female_singer_1",
  "genre": "pop",
  "duration": 120
}
```

---

### Retrieve & Download

#### GET `/api/v1/songs/{song_id}`

**Retrieve song by ID** (WBS 2.14.5)

Get complete song information including metadata, file paths, and statistics.

**Response** (200 OK):
```json
{
  "id": "550e8400-...",
  "title": "My Song",
  "genre": "pop",
  "file_info": { ... },
  "statistics": {
    "play_count": 45,
    "download_count": 12,
    "share_count": 8,
    "like_count": 23
  },
  "generation_status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### GET `/api/v1/songs/{song_id}/download?format=mp3`

**Download song file** (WBS 2.14.6)

Download the final song in specified format.

**Query Parameters**:
- `format` (optional): `wav`, `mp3`, `ogg`, `flac`, `m4a` (default: `wav`)

**Response** (200 OK): Binary audio file

**Example**:
```bash
# Download as MP3
curl "http://localhost:8000/api/v1/songs/{song_id}/download?format=mp3" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "my_song.mp3"

# Download as WAV (default)
curl "http://localhost:8000/api/v1/songs/{song_id}/download" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o "my_song.wav"
```

---

#### GET `/api/v1/songs/{song_id}/stream`

**Stream song audio** (WBS 2.14.7)

Stream the song for playback (increments play count).

**Response** (200 OK): Audio stream (chunked transfer)

**Example**:
```html
<audio controls>
  <source src="http://localhost:8000/api/v1/songs/{song_id}/stream" type="audio/wav">
</audio>
```

---

### Regenerate Components

#### POST `/api/v1/songs/{song_id}/regenerate-vocals`

**Regenerate vocals** with new voice or settings (WBS 2.14.8)

Re-synthesize vocals keeping the same lyrics but with different voice/effects.

**Request Body**:
```json
{
  "voice_profile_id": "male_singer_1",
  "vocal_pitch_shift": 3,
  "vocal_effects": {
    "reverb": {"room_size": 0.7, "wet_level": 0.4}
  }
}
```

**Response** (200 OK): Updated `SongResponse`

---

#### POST `/api/v1/songs/{song_id}/regenerate-music`

**Regenerate music** with new genre/settings (WBS 2.14.9)

Re-generate instrumental keeping the same vocals.

**Request Body**:
```json
{
  "genre": "rock",
  "bpm": 140,
  "key": "E major",
  "music_style": "electric guitar driven"
}
```

**Response** (200 OK): Updated `SongResponse`

---

### Manage Songs

#### PUT `/api/v1/songs/{song_id}/settings`

**Update song settings** (WBS 2.14.10)

Update metadata and configuration without regenerating audio.

**Request Body**:
```json
{
  "title": "New Title",
  "artist_name": "Updated Artist",
  "genre": "indie",
  "is_public": true
}
```

---

#### POST `/api/v1/songs/{song_id}/remix`

**Remix existing song** (WBS 2.14.13)

Create a variation with different vocals, music, or mixing settings.

**Request Body**:
```json
{
  "voice_profile_id": "male_singer_2",
  "vocal_pitch_shift": -4,
  "genre": "electronic",
  "bpm": 128,
  "vocals_volume_db": 2.0,
  "music_volume_db": -3.0
}
```

**Use Cases**:
- Create radio edit with different mixing
- Change genre (e.g., pop → electronic)
- Try different voice profiles
- Experiment with pitch variations

---

#### DELETE `/api/v1/songs/{song_id}`

**Delete song** and all associated files.

**Response** (204 No Content)

---

### List & Discovery

#### GET `/api/v1/songs?skip=0&limit=20&status=completed&genre=pop`

**List user songs** with pagination and filtering.

**Query Parameters**:
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Max results (1-100, default: 20)
- `status` (string): Filter by status (`pending`, `completed`, `failed`)
- `genre` (string): Filter by genre

**Response** (200 OK):
```json
{
  "songs": [ ... ],
  "total": 45,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

#### GET `/api/v1/songs/public/trending?limit=10`

**Get trending public songs**

Returns popular public songs based on engagement metrics.

---

### Metadata & Discovery

#### GET `/api/v1/songs/metadata/voices`

**List available voice profiles** (WBS 2.14.11)

**Response** (200 OK):
```json
[
  {
    "id": "female_singer_1",
    "name": "Female Pop Singer 1",
    "gender": "female",
    "language": "en",
    "description": "Clear female pop vocals",
    "style": "singing"
  },
  ...
]
```

---

#### GET `/api/v1/songs/metadata/genres`

**List available music genres** (WBS 2.14.12)

**Response** (200 OK):
```json
[
  {
    "id": "pop",
    "name": "Pop",
    "description": "Pop music style",
    "typical_bpm_range": "100-130 BPM",
    "common_keys": ["C major", "G major", "D major", ...],
    "typical_instruments": ["piano", "drums", "bass", ...]
  },
  ...
]
```

**Available Genres** (15 total):
- Pop, Rock, Hip-Hop, Electronic, Jazz
- Classical, Country, R&B, Indie, Folk
- Metal, Blues, Reggae, Latin, Ambient

---

## Data Models

### Song (Database Model)

```python
class Song:
    id: UUID
    user_id: UUID
    lyrics_id: Optional[UUID]
    
    # Metadata
    title: str
    artist_name: Optional[str]
    genre: Optional[str]
    mood: Optional[str]
    bpm: Optional[int]
    key: Optional[str]
    duration_seconds: Optional[float]
    
    # Generation settings
    voice_profile_id: Optional[UUID]
    music_style: Optional[str]
    vocal_pitch_shift: int = 0
    vocal_effects: dict = {}
    music_params: dict = {}
    
    # File references
    final_audio_file_id: Optional[UUID]
    vocal_track_file_id: Optional[UUID]
    instrumental_track_file_id: Optional[UUID]
    
    # Quality metrics
    audio_quality_score: Optional[float]
    mixing_quality_score: Optional[float]
    overall_rating: Optional[float]
    
    # Statistics
    play_count: int = 0
    download_count: int = 0
    share_count: int = 0
    like_count: int = 0
    
    # Status
    generation_status: str  # pending, processing, completed, failed
    is_public: bool = False
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    published_at: Optional[datetime]
```

---

## Workflows

### Workflow 1: Generate Song from Scratch

```python
import httpx

async def generate_song():
    async with httpx.AsyncClient() as client:
        # Step 1: Generate complete song
        response = await client.post(
            "http://localhost:8000/api/v1/songs/generate",
            json={
                "lyrics_prompt": "A happy song about coding",
                "genre": "electronic",
                "voice_profile_id": "female_singer_1",
                "bpm": 128,
                "duration_seconds": 180
            }
        )
        song = response.json()
        song_id = song["id"]
        
        # Step 2: Download as MP3
        mp3_response = await client.get(
            f"http://localhost:8000/api/v1/songs/{song_id}/download?format=mp3"
        )
        with open("my_song.mp3", "wb") as f:
            f.write(mp3_response.content)
        
        print(f"Song generated: {song['title']}")
        print(f"Duration: {song['duration_seconds']}s")
        print(f"Downloaded to: my_song.mp3")
```

---

### Workflow 2: Experiment with Variations

```python
# Generate original
original = await client.post("/api/v1/songs/generate", json={...})
song_id = original.json()["id"]

# Try different voice
variation_1 = await client.post(
    f"/api/v1/songs/{song_id}/regenerate-vocals",
    json={"voice_profile_id": "male_singer_1"}
)

# Try different genre
variation_2 = await client.post(
    f"/api/v1/songs/{song_id}/regenerate-music",
    json={"genre": "jazz", "bpm": 100}
)

# Create remix
remix = await client.post(
    f"/api/v1/songs/{song_id}/remix",
    json={
        "voice_profile_id": "male_singer_2",
        "genre": "rock",
        "bpm": 140,
        "vocals_volume_db": 3.0
    }
)
```

---

### Workflow 3: Build a Song Library

```python
# List all user songs
response = await client.get("/api/v1/songs?limit=100")
songs = response.json()["songs"]

# Filter completed songs
completed = [s for s in songs if s["generation_status"] == "completed"]

# Download all as MP3
for song in completed:
    mp3 = await client.get(f"/api/v1/songs/{song['id']}/download?format=mp3")
    filename = f"{song['title'].replace(' ', '_')}.mp3"
    with open(filename, "wb") as f:
        f.write(mp3.content)
```

---

## Best Practices

### 1. **Generation Parameters**

```python
# ✅ Good: Clear, specific prompt
{
  "lyrics_prompt": "Write an uplifting pop song about overcoming challenges",
  "genre": "pop",
  "mood": "inspirational",
  "bpm": 120
}

# ❌ Avoid: Vague prompt
{
  "lyrics_prompt": "Make a song",
  "genre": None
}
```

### 2. **Voice Selection**

Match voice to genre:
- **Pop/Rock**: `female_singer_1`, `male_singer_1`
- **Jazz/Blues**: `female_jazzy_1`
- **Rap/Hip-Hop**: `male_rapper_1`

### 3. **BPM Guidelines**

- **Ballad**: 60-80 BPM
- **Pop**: 100-130 BPM
- **Rock**: 110-140 BPM
- **Electronic**: 120-140 BPM
- **Hip-Hop**: 80-110 BPM

### 4. **Vocal Effects**

```python
# Subtle (professional)
"vocal_effects": {
  "reverb": {"room_size": 0.3, "wet_level": 0.2},
  "eq": {"low": 0, "mid": 1, "high": 2}
}

# Heavy (stylized)
"vocal_effects": {
  "reverb": {"room_size": 0.8, "wet_level": 0.5},
  "echo": {"delay_ms": 500, "decay": 0.5}
}
```

### 5. **Error Handling**

```python
try:
    song = await client.post("/api/v1/songs/generate", json={...})
except httpx.HTTPStatusError as e:
    if e.response.status_code == 500:
        print("Generation failed, retry with simpler params")
    elif e.response.status_code == 429:
        print("Rate limit exceeded, wait before retry")
```

---

## Troubleshooting

### Generation Takes Too Long

**Problem**: Song generation exceeds 5 minutes

**Solutions**:
1. Reduce `duration_seconds` (try 120s instead of 180s)
2. Use simpler prompt (fewer words)
3. Disable RAG: `"use_rag": false`
4. Check system resources (GPU, memory)

---

### Poor Audio Quality

**Problem**: Final song sounds distorted or unclear

**Solutions**:
1. **Lower mixing volumes**:
   ```json
   {
     "vocals_volume_db": 0,
     "music_volume_db": -6
   }
   ```

2. **Try different voice**: Some voices work better for certain genres

3. **Adjust BPM**: Match genre conventions

4. **Regenerate music**: First generation may not be optimal

---

### Vocals Don't Match Music

**Problem**: Timing or style mismatch between vocals and instrumental

**Solutions**:
1. **Regenerate music** with explicit style:
   ```json
   {
     "music_style": "slow piano ballad matching emotional vocals"
   }
   ```

2. **Use structured generation**: Specify section timings

3. **Try remix** with adjusted mixing levels

---

### File Not Found Errors

**Problem**: 404 when downloading or streaming

**Solutions**:
1. Check `generation_status`: Must be "completed"
2. Verify song ID is correct
3. Ensure user has access (owned or public song)
4. Check `file_info.final_audio_path` exists

---

## Advanced Features

### Batch Generation

```python
prompts = [
    "A happy song about summer",
    "A sad song about rain",
    "An energetic song about dancing"
]

tasks = [
    client.post("/api/v1/songs/generate", json={
        "lyrics_prompt": prompt,
        "voice_profile_id": "female_singer_1",
        "genre": "pop"
    })
    for prompt in prompts
]

songs = await asyncio.gather(*tasks)
```

### A/B Testing Voices

```python
song_id = "..."
voices = ["female_singer_1", "female_singer_2", "male_singer_1"]

for voice in voices:
    variant = await client.post(
        f"/api/v1/songs/{song_id}/regenerate-vocals",
        json={"voice_profile_id": voice}
    )
    # User listens and rates each variant
```

### Analytics Dashboard

```python
# Get all songs with stats
songs = await client.get("/api/v1/songs?limit=100")

# Calculate metrics
total_plays = sum(s["statistics"]["play_count"] for s in songs)
total_downloads = sum(s["statistics"]["download_count"] for s in songs)
avg_duration = sum(s["duration_seconds"] for s in songs) / len(songs)

print(f"Total plays: {total_plays}")
print(f"Total downloads: {total_downloads}")
print(f"Average song length: {avg_duration:.1f}s")
```

---

## Integration Examples

### Next.js Frontend

```typescript
// app/generate/page.tsx
'use client';

export default function GeneratePage() {
  const [loading, setLoading] = useState(false);
  
  const generateSong = async (prompt: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/songs/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lyrics_prompt: prompt,
          genre: 'pop',
          voice_profile_id: 'female_singer_1',
          duration_seconds: 180
        })
      });
      
      const song = await response.json();
      router.push(`/songs/${song.id}`);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <input
        type="text"
        placeholder="What song do you want?"
        onSubmit={(e) => generateSong(e.target.value)}
      />
      {loading && <p>Generating your song...</p>}
    </div>
  );
}
```

### React Native Mobile

```typescript
// screens/PlayerScreen.tsx
import { Audio } from 'expo-av';

export function PlayerScreen({ songId }) {
  const [sound, setSound] = useState<Audio.Sound>();
  
  async function playSound() {
    const { sound } = await Audio.Sound.createAsync(
      { uri: `${API_URL}/songs/${songId}/stream` }
    );
    setSound(sound);
    await sound.playAsync();
  }
  
  return (
    <View>
      <Button title="Play" onPress={playSound} />
    </View>
  );
}
```

---

## Performance

### Expected Latencies

| Operation | Typical Time | Max Time |
|-----------|-------------|----------|
| Complete song generation | 90-210s | 300s |
| Lyrics generation | 30-60s | 120s |
| Voice synthesis | 10-30s | 60s |
| Music generation | 30-90s | 180s |
| Mixing & mastering | 10-20s | 40s |
| Download (MP3, 3min song) | 1-3s | 10s |
| Streaming (buffered) | <1s | 5s |

### Optimization Tips

1. **Use caching**: Store frequently used voice profiles
2. **Async processing**: Don't block on song generation
3. **CDN for downloads**: Serve files from CDN
4. **Compression**: Use MP3 (smaller) vs WAV (larger)
5. **Lazy loading**: Load song list incrementally

---

## Security & Permissions

### Access Control

- **Owned songs**: User can perform all operations
- **Public songs**: Anyone can read, download, stream
- **Private songs**: Only owner can access

### Rate Limiting

- **Generation**: 10 songs/hour per user
- **Downloads**: 100/hour per user
- **Streaming**: Unlimited

---

## Conclusion

The Complete Song Generation API provides a powerful, flexible interface for creating AI-generated music. By combining lyrics, voice synthesis, and music composition into a single unified workflow, it enables rapid experimentation and iteration on musical ideas.

For more details, see:
- [Voice Synthesis Guide](./VOICE_SYNTHESIS_GUIDE.md)
- [Music Generation Guide](./MUSIC_GENERATION_GUIDE.md)
- [API Reference](./API_REFERENCE.md)

---

**Last Updated**: 2024-01-15
**API Version**: v1
**Backend**: FastAPI + PostgreSQL + MusicGen + TTS

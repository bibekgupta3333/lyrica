"""
API Endpoints for Song Styles and Music Genres.

This module provides endpoints for discovering available
music genres, moods, themes, and style references.
"""

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# ============================================================================
# Response Models
# ============================================================================


class Genre(BaseModel):
    """Music genre model."""

    name: str
    description: str
    examples: List[str]


class Mood(BaseModel):
    """Mood model."""

    name: str
    description: str
    keywords: List[str]


class Theme(BaseModel):
    """Theme model."""

    name: str
    description: str
    examples: List[str]


class StyleReference(BaseModel):
    """Style reference (artist/song) model."""

    name: str
    type: str  # "artist" or "song"
    genre: str
    description: str


class AvailableStyles(BaseModel):
    """All available styles response."""

    genres: List[Genre]
    moods: List[Mood]
    themes: List[Theme]
    style_references: List[StyleReference]


# ============================================================================
# Data
# ============================================================================

GENRES = [
    Genre(
        name="pop",
        description="Contemporary popular music with catchy melodies",
        examples=["Taylor Swift - Shake It Off", "Ed Sheeran - Shape of You"],
    ),
    Genre(
        name="rock",
        description="Guitar-driven music with strong rhythms",
        examples=["Queen - Bohemian Rhapsody", "Led Zeppelin - Stairway to Heaven"],
    ),
    Genre(
        name="hip-hop",
        description="Rhythmic music with rap vocals and beats",
        examples=["Kendrick Lamar - HUMBLE.", "Drake - God's Plan"],
    ),
    Genre(
        name="r&b",
        description="Rhythm and blues with soulful vocals",
        examples=["The Weeknd - Blinding Lights", "SZA - Good Days"],
    ),
    Genre(
        name="country",
        description="American roots music with storytelling",
        examples=["Johnny Cash - Ring of Fire", "Dolly Parton - Jolene"],
    ),
    Genre(
        name="jazz",
        description="Improvisational music with complex harmonies",
        examples=["Miles Davis - So What", "Ella Fitzgerald - Summertime"],
    ),
    Genre(
        name="electronic",
        description="Synthesizer and computer-generated sounds",
        examples=["Daft Punk - One More Time", "Avicii - Wake Me Up"],
    ),
    Genre(
        name="folk",
        description="Traditional acoustic music with storytelling",
        examples=["Bob Dylan - Blowin' in the Wind", "Simon & Garfunkel - The Sound of Silence"],
    ),
    Genre(
        name="indie",
        description="Independent alternative rock with artistic expression",
        examples=["Arctic Monkeys - Do I Wanna Know?", "Tame Impala - The Less I Know The Better"],
    ),
    Genre(
        name="ballad",
        description="Slow romantic songs with emotional vocals",
        examples=["Adele - Someone Like You", "Sam Smith - Stay With Me"],
    ),
    Genre(
        name="blues",
        description="Emotional music with blues scale and guitar",
        examples=["B.B. King - The Thrill Is Gone", "Etta James - At Last"],
    ),
    Genre(
        name="metal",
        description="Heavy distorted guitars with powerful vocals",
        examples=["Metallica - Enter Sandman", "Black Sabbath - Paranoid"],
    ),
]

MOODS = [
    Mood(
        name="happy",
        description="Upbeat, joyful, and positive",
        keywords=["cheerful", "energetic", "uplifting", "bright"],
    ),
    Mood(
        name="sad",
        description="Melancholic, sorrowful, and emotional",
        keywords=["melancholic", "emotional", "heartbroken", "tearful"],
    ),
    Mood(
        name="romantic",
        description="Loving, passionate, and intimate",
        keywords=["loving", "passionate", "tender", "sweet"],
    ),
    Mood(
        name="angry",
        description="Intense, aggressive, and powerful",
        keywords=["intense", "aggressive", "furious", "rebellious"],
    ),
    Mood(
        name="calm",
        description="Peaceful, relaxing, and serene",
        keywords=["peaceful", "soothing", "tranquil", "mellow"],
    ),
    Mood(
        name="energetic",
        description="High-energy, dynamic, and exciting",
        keywords=["dynamic", "vigorous", "lively", "exciting"],
    ),
    Mood(
        name="mysterious",
        description="Enigmatic, dark, and intriguing",
        keywords=["dark", "enigmatic", "suspenseful", "haunting"],
    ),
    Mood(
        name="nostalgic",
        description="Reflective, wistful, and reminiscent",
        keywords=["reflective", "wistful", "bittersweet", "longing"],
    ),
    Mood(
        name="empowering",
        description="Motivational, confident, and strong",
        keywords=["motivational", "confident", "triumphant", "bold"],
    ),
    Mood(
        name="dreamy",
        description="Ethereal, atmospheric, and surreal",
        keywords=["ethereal", "atmospheric", "floating", "hypnotic"],
    ),
]

THEMES = [
    Theme(
        name="love",
        description="Romantic relationships and affection",
        examples=["falling in love", "heartbreak", "long-distance love"],
    ),
    Theme(
        name="loss",
        description="Grief, separation, and missing someone",
        examples=["losing a loved one", "goodbye", "remembering the past"],
    ),
    Theme(
        name="freedom",
        description="Independence, liberation, and breaking free",
        examples=["escaping constraints", "finding yourself", "living freely"],
    ),
    Theme(
        name="hope",
        description="Optimism, dreams, and better futures",
        examples=["overcoming adversity", "new beginnings", "believing in tomorrow"],
    ),
    Theme(
        name="nostalgia",
        description="Memories, past times, and reflections",
        examples=["childhood memories", "old friends", "simpler times"],
    ),
    Theme(
        name="adventure",
        description="Exploration, journey, and discovery",
        examples=["traveling the world", "chasing dreams", "new experiences"],
    ),
    Theme(
        name="identity",
        description="Self-discovery and personal growth",
        examples=["finding yourself", "being authentic", "self-acceptance"],
    ),
    Theme(
        name="social issues",
        description="Commentary on society and politics",
        examples=["equality", "justice", "environmental concerns"],
    ),
    Theme(
        name="celebration",
        description="Joy, parties, and good times",
        examples=["having fun", "dancing all night", "living in the moment"],
    ),
    Theme(
        name="resilience",
        description="Overcoming challenges and perseverance",
        examples=["rising from failure", "staying strong", "never giving up"],
    ),
]

STYLE_REFERENCES = [
    StyleReference(
        name="Taylor Swift",
        type="artist",
        genre="pop",
        description="Storytelling lyrics with catchy pop melodies",
    ),
    StyleReference(
        name="Ed Sheeran",
        type="artist",
        genre="pop",
        description="Intimate acoustic pop with personal narratives",
    ),
    StyleReference(
        name="Adele",
        type="artist",
        genre="ballad",
        description="Powerful emotional vocals with soulful ballads",
    ),
    StyleReference(
        name="The Weeknd",
        type="artist",
        genre="r&b",
        description="Dark R&B with atmospheric production",
    ),
    StyleReference(
        name="Kendrick Lamar",
        type="artist",
        genre="hip-hop",
        description="Conscious hip-hop with complex wordplay",
    ),
    StyleReference(
        name="Coldplay",
        type="artist",
        genre="rock",
        description="Anthemic alternative rock with introspective lyrics",
    ),
    StyleReference(
        name="Billie Eilish",
        type="artist",
        genre="pop",
        description="Dark pop with minimalist production and whispered vocals",
    ),
    StyleReference(
        name="Sam Smith",
        type="artist",
        genre="ballad",
        description="Emotional ballads with gospel influences",
    ),
    StyleReference(
        name="Drake",
        type="artist",
        genre="hip-hop",
        description="Melodic rap with emotional vulnerability",
    ),
    StyleReference(
        name="Queen",
        type="artist",
        genre="rock",
        description="Theatrical rock with complex arrangements",
    ),
]


# ============================================================================
# Endpoints
# ============================================================================


@router.get(
    "/",
    response_model=AvailableStyles,
    summary="Get all available styles",
    description="Get all available genres, moods, themes, and style references",
)
async def get_all_styles():
    """
    Get all available styles for song generation.

    Returns:
    - **Genres**: Music genres (pop, rock, hip-hop, etc.)
    - **Moods**: Emotional tones (happy, sad, energetic, etc.)
    - **Themes**: Song themes (love, loss, freedom, etc.)
    - **Style References**: Artist and song references for style inspiration
    """
    return AvailableStyles(
        genres=GENRES,
        moods=MOODS,
        themes=THEMES,
        style_references=STYLE_REFERENCES,
    )


@router.get(
    "/genres",
    response_model=List[Genre],
    summary="Get available genres",
    description="Get list of available music genres",
)
async def get_genres():
    """Get list of available music genres."""
    return GENRES


@router.get(
    "/moods",
    response_model=List[Mood],
    summary="Get available moods",
    description="Get list of available moods",
)
async def get_moods():
    """Get list of available moods."""
    return MOODS


@router.get(
    "/themes",
    response_model=List[Theme],
    summary="Get available themes",
    description="Get list of available song themes",
)
async def get_themes():
    """Get list of available song themes."""
    return THEMES


@router.get(
    "/references",
    response_model=List[StyleReference],
    summary="Get style references",
    description="Get list of artist and song style references",
)
async def get_style_references():
    """Get list of artist and song style references."""
    return STYLE_REFERENCES

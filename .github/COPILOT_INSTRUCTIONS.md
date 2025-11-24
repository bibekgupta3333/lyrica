# GitHub Copilot Instructions for Lyrica

This file provides context to GitHub Copilot for the Lyrica project.

## Project Context

Lyrica is an agentic song lyrics generator using:

- **Backend**: FastAPI + PostgreSQL + ChromaDB + LangGraph + Ollama
- **Frontend**: Next.js 16 (web) + React Native CLI 0.76 (mobile)
- **Monorepo**: TurboRepo with pnpm workspaces

## Code Style

### Python (Backend)

- Use async/await for all database operations
- Type hints required for all functions
- Line length: 100 characters
- Format with Black and isort
- Docstrings in Google style

### TypeScript (Frontend)

- Strict TypeScript, avoid `any`
- 2-space indentation
- Single quotes, semicolons
- React functional components with hooks
- Use React Query for API calls

## Key Patterns

### Backend API Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

@router.post("/lyrics/", response_model=schemas.LyricsResponse)
async def create_lyrics(
    lyrics: schemas.LyricsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.LyricsResponse:
    """Create new lyrics entry."""
    db_lyrics = await crud.lyrics.create(db, obj_in=lyrics, user_id=current_user.id)
    return db_lyrics
```

### Frontend Component

```typescript
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';

interface Props {
  onSuccess?: (data: Lyrics) => void;
}

export const LyricsGenerator: React.FC<Props> = ({ onSuccess }) => {
  const [prompt, setPrompt] = useState('');

  const { mutate, isLoading } = useMutation({
    mutationFn: (data: GenerateRequest) => generateLyrics(data),
    onSuccess: (data) => {
      onSuccess?.(data);
    },
  });

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      mutate({ prompt });
    }}>
      {/* Form content */}
    </form>
  );
};
```

## File Structure

- Backend: `lyrica-backend/app/`
  - Models: `models/entity_name.py`
  - API: `api/v1/endpoints/resource.py`
  - Schemas: `schemas/entity_name.py`
- Frontend Web: `lyrica-web/src/`
  - Components: `components/ComponentName.tsx`
  - Pages: `app/route/page.tsx`
  - Hooks: `hooks/useSomething.ts`

- Mobile: `lyrica-mobile/src/`
  - Screens: `screens/ScreenName.tsx`
  - Components: `components/ComponentName.tsx`

## Common Tasks

### Add New Model

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Create CRUD in `app/crud/`
4. Add to `app/models/__init__.py`
5. Create migration: `alembic revision --autogenerate`

### Add New API Endpoint

1. Define schema in `app/schemas/`
2. Add endpoint in `app/api/v1/endpoints/`
3. Register router in `app/api/v1/api.py`
4. Add tests in `tests/`

### Add New Component

1. Create component file with proper naming
2. Define TypeScript interfaces
3. Use appropriate hooks (useState, useEffect, React Query)
4. Add to exports if needed

## Testing

- Backend: Use `pytest` with async support
- Frontend: Use Jest + React Testing Library
- Always test error cases
- Mock external dependencies

## Documentation

- Add docstrings to all public functions
- Update README when adding features
- Keep inline comments minimal and meaningful
- Document complex algorithms

For full guidelines, see `.cursorrules` in the project root.

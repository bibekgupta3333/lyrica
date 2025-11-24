# AI Assistant Setup Guide

This guide explains how to use AI coding assistants (Cursor, GitHub Copilot, etc.) effectively with the Lyrica project.

## 📝 Configuration Files

The project includes several configuration files to guide AI assistants:

```
lyrica/
├── .cursorrules              # Main AI assistant rules (all assistants)
├── .aidigestignore           # Files to exclude from AI context
└── .github/
    └── COPILOT_INSTRUCTIONS.md  # GitHub Copilot specific
```

## 🎯 What's Configured

### .cursorrules
Comprehensive rules covering:
- ✅ Project overview and tech stack
- ✅ Code style guidelines (Python, TypeScript)
- ✅ File structure and naming conventions
- ✅ Architecture patterns
- ✅ Testing requirements
- ✅ Security best practices
- ✅ Performance optimization
- ✅ Error handling patterns
- ✅ API design principles
- ✅ Common examples and anti-patterns

### .github/COPILOT_INSTRUCTIONS.md
GitHub Copilot specific instructions:
- ✅ Quick reference for common patterns
- ✅ File structure guidance
- ✅ Code examples
- ✅ Common tasks

### .aidigestignore
Excludes from AI context:
- ✅ Dependencies (node_modules, venv)
- ✅ Build outputs
- ✅ Lock files
- ✅ Generated files
- ✅ Large documentation files

## 🚀 Using with Different AI Assistants

### Cursor AI

Cursor automatically reads `.cursorrules` from the project root.

**Tips:**
1. Use `Cmd/Ctrl + K` for inline generation with rules
2. Use `Cmd/Ctrl + L` for chat with full context
3. Reference specific files with `@filename`
4. Ask about patterns: "How should I create a new API endpoint?"

**Example Prompts:**
```
"Create a new FastAPI endpoint for lyrics search following project conventions"

"Generate a React component for displaying lyrics with proper TypeScript types"

"Add a SQLAlchemy model for user preferences following project patterns"
```

### GitHub Copilot

Copilot reads `.github/COPILOT_INSTRUCTIONS.md` automatically.

**Tips:**
1. Start typing to get inline suggestions
2. Use comments to guide generation
3. Tab to accept, `Alt/Opt + ]` for next suggestion
4. Use Copilot Chat for complex questions

**Example Comments for Better Suggestions:**
```python
# Create async endpoint to generate lyrics with LangGraph agents
# POST /api/v1/lyrics/generate
# Request: LyricsGenerateRequest schema
# Response: LyricsResponse schema
# Auth: requires current_user
```

```typescript
// React component for lyrics generation form
// Props: onSuccess callback
// Uses React Query for API calls
// Includes loading states and error handling
```

### Other AI Assistants

Most AI assistants respect:
- ✅ `.cursorrules` (primary configuration)
- ✅ Comments in code
- ✅ Existing code patterns
- ✅ File structure

## 📋 Best Practices

### 1. Be Specific in Prompts
❌ Bad: "Create an API endpoint"
✅ Good: "Create a POST endpoint for lyrics generation at /api/v1/lyrics/generate with async SQLAlchemy"

### 2. Reference Existing Patterns
```
"Create a model similar to User but for LyricsStyle"
"Follow the pattern in health.py endpoints"
```

### 3. Ask for Explanations
```
"Explain how the LangGraph agent system should work in this project"
"Show me the best way to handle streaming responses in FastAPI"
```

### 4. Request Tests
```
"Generate pytest tests for this endpoint"
"Add test cases for error scenarios"
```

### 5. Check Consistency
```
"Does this follow the project's code style?"
"Is this the correct way to handle database transactions here?"
```

## 🎓 Common Patterns

### Creating New Backend Feature

**Prompt:**
```
Create a new backend feature for saving user preferences:
1. SQLAlchemy model in app/models/user_preferences.py
2. Pydantic schemas in app/schemas/user_preferences.py
3. CRUD operations in app/crud/user_preferences.py
4. API endpoints in app/api/v1/endpoints/preferences.py
5. Include tests

Follow project conventions for async, types, and documentation.
```

### Creating New Frontend Component

**Prompt:**
```
Create a React component for lyrics editor:
- TypeScript with proper interfaces
- Uses React Query for saving
- Includes loading and error states
- Tailwind CSS styling
- Follows project component structure

Component should be in components/LyricsEditor.tsx
```

### Adding Database Migration

**Prompt:**
```
Help me create an Alembic migration to add a 'favorite' boolean column 
to the lyrics table with default False. Show the command and expected result.
```

## 🔍 Troubleshooting

### AI Suggests Wrong Pattern

**Solution:** Reference the rules explicitly:
```
"According to .cursorrules, how should I structure this component?"
"The project uses async SQLAlchemy, not sync. Can you update the code?"
```

### Generated Code Doesn't Match Style

**Solution:** 
1. Run formatters: `pnpm format` or `make format`
2. Ask AI to fix: "Format this following Black/Prettier rules"
3. Check `.editorconfig` is working

### AI Hallucinates Imports

**Solution:**
```
"Use only these imports that exist in the project: [list imports]"
"Check what's actually available in app/core/config.py"
```

### Context is Too Large

**Solution:**
1. Use `.aidigestignore` to exclude files
2. Focus on specific directories: `@lyrica-backend/app/api/`
3. Ask for smaller chunks: "First show me just the model"

## 💡 Pro Tips

### 1. Use Project References
```
"Look at app/api/v1/endpoints/health.py for the pattern"
"Follow the same structure as app/models/user.py"
```

### 2. Iterate on Suggestions
```
First prompt: "Create basic lyrics model"
Then: "Add genre and mood fields"
Then: "Add relationship to user"
Then: "Add created_at and updated_at timestamps"
```

### 3. Ask for Multiple Options
```
"Show me 3 different ways to implement caching for this endpoint"
"What are the pros and cons of each approach?"
```

### 4. Validate Against Rules
```
"Review this code against .cursorrules and suggest improvements"
"Does this follow all the project conventions?"
```

### 5. Learn Patterns
```
"Explain the agent orchestration pattern used in this project"
"Why do we use async/await everywhere in the backend?"
```

## 🎨 Example Workflows

### Adding New API Endpoint

1. **Ask for model:**
   ```
   "Create SQLAlchemy model for LyricsTemplate with title, content, genre"
   ```

2. **Ask for schemas:**
   ```
   "Create Pydantic schemas for the LyricsTemplate model (Create, Update, Response)"
   ```

3. **Ask for CRUD:**
   ```
   "Create CRUD operations for LyricsTemplate following the base CRUD pattern"
   ```

4. **Ask for endpoint:**
   ```
   "Create REST endpoints for LyricsTemplate CRUD operations with auth"
   ```

5. **Ask for tests:**
   ```
   "Generate pytest tests for the LyricsTemplate endpoints"
   ```

### Building Frontend Feature

1. **Ask for types:**
   ```
   "Create TypeScript interfaces for lyrics API responses"
   ```

2. **Ask for API hook:**
   ```
   "Create React Query hooks for fetching and generating lyrics"
   ```

3. **Ask for component:**
   ```
   "Create LyricsCard component to display lyrics with edit/delete actions"
   ```

4. **Ask for page:**
   ```
   "Create page that lists all lyrics using the LyricsCard component"
   ```

## 📊 Quality Checks

After AI generates code, verify:

- [ ] Follows project code style (Black/Prettier)
- [ ] Has proper type hints/types
- [ ] Includes error handling
- [ ] Has appropriate logging
- [ ] Follows security best practices
- [ ] Uses async where appropriate (backend)
- [ ] Includes tests (or ask AI to add them)
- [ ] Documentation/docstrings added
- [ ] Imports are correct and exist
- [ ] Matches existing patterns

Run these commands:
```bash
# Format
pnpm format

# Lint
pnpm lint

# Test
pnpm test

# Type check
cd lyrica-backend && mypy app/
cd lyrica-web && npm run type-check
```

## 🔗 Resources

- Main Rules: [.cursorrules](../../.cursorrules)
- Copilot Guide: [.github/COPILOT_INSTRUCTIONS.md](../../.github/COPILOT_INSTRUCTIONS.md)
- Code Style: [EDITOR_SETUP.md](./EDITOR_SETUP.md)
- Project Status: [PROJECT_STATUS.md](../PROJECT_STATUS.md)

---

**With these configurations, AI assistants will generate consistent, high-quality code that matches project conventions!** 🤖✨

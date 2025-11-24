# Editor Configuration Guide

This guide explains the editor configuration files in the Lyrica monorepo and how to use them.

## 📝 Overview

The monorepo includes configuration files to ensure consistent code style across all editors and team members:

```
lyrica/
├── .editorconfig           # Universal editor config
├── .prettierrc.js          # Prettier formatting rules
├── .prettierignore         # Prettier ignore patterns
└── .vscode/                # VSCode-specific settings
    ├── settings.json       # Editor settings
    └── extensions.json     # Recommended extensions
```

## 🎯 EditorConfig (.editorconfig)

EditorConfig works with most modern editors (VSCode, IntelliJ, Sublime, Vim, etc.).

### Key Settings

| File Type | Indent Style | Indent Size | Max Line Length |
|-----------|-------------|-------------|-----------------|
| Python (.py) | Spaces | 4 | 100 |
| JS/TS (.js, .ts, .tsx) | Spaces | 2 | 100 |
| JSON (.json) | Spaces | 2 | - |
| YAML (.yml) | Spaces | 2 | - |
| Makefile | Tabs | 4 | - |
| Markdown (.md) | Spaces | 2 | - |

### Universal Settings

All files get:
- ✅ UTF-8 encoding
- ✅ LF line endings (Unix style)
- ✅ Final newline
- ✅ Trailing whitespace trimmed

## 🎨 Prettier Configuration

Prettier handles formatting for JavaScript, TypeScript, JSON, YAML, Markdown, and more.

### Settings

```javascript
{
  printWidth: 100,        // Max line length
  tabWidth: 2,            // Tab width
  useTabs: false,         // Use spaces
  semi: true,             // Add semicolons
  singleQuote: true,      // Use single quotes
  trailingComma: 'es5',   // Trailing commas where valid in ES5
  arrowParens: 'avoid',   // Omit parens when possible
}
```

### Usage

```bash
# Format all files
pnpm format

# Format specific workspace
pnpm --filter lyrica-web format
pnpm --filter lyrica-mobile format

# Format specific files
npx prettier --write "src/**/*.{ts,tsx,js,jsx}"
```

## 💻 VSCode Configuration

### Automatic Setup

VSCode will automatically:
1. Use correct indentation per file type
2. Format on save
3. Organize imports on save
4. Trim trailing whitespace
5. Insert final newline

### Required Extensions

Install these for the best experience:

**Python:**
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Black Formatter (ms-python.black-formatter)
- isort (ms-python.isort)
- Flake8 (ms-python.flake8)

**JavaScript/TypeScript:**
- ESLint (dbaeumer.vscode-eslint)
- Prettier (esbenp.prettier-vscode)

**React/Next.js:**
- ES7+ React/Redux snippets (dsznajder.es7-react-js-snippets)
- Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)

**General:**
- EditorConfig (editorconfig.editorconfig)
- GitLens (eamodio.gitlens)
- Docker (ms-azuretools.vscode-docker)
- Error Lens (usernamehw.errorlens)

### Install All Extensions

```bash
# VSCode will prompt to install recommended extensions
# Or install via command palette: "Extensions: Show Recommended Extensions"
```

## 🔧 IDE-Specific Setup

### PyCharm / IntelliJ IDEA

1. **Enable EditorConfig:**
   - Settings → Editor → Code Style
   - ✅ Enable EditorConfig support

2. **Python Formatting:**
   - Settings → Tools → Black
   - Configure Black: `--line-length 100`

3. **JavaScript/TypeScript:**
   - Settings → Languages & Frameworks → JavaScript → Prettier
   - ✅ Run on save

### Sublime Text

1. Install EditorConfig plugin via Package Control
2. Install Prettier plugin
3. Settings will be applied automatically

### Vim / Neovim

1. Install `editorconfig-vim` plugin
2. Install `ale` or `coc-prettier` for Prettier support
3. Configuration is automatic

## 📐 Code Style Rules

### Python

```python
# Line length: 100 characters
# Indentation: 4 spaces
# Quotes: Double quotes (Black default)

def example_function(param1: str, param2: int) -> dict:
    """Function with proper formatting."""
    result = {
        "key1": "value1",
        "key2": "value2",
    }
    return result
```

### TypeScript/JavaScript

```typescript
// Line length: 100 characters
// Indentation: 2 spaces
// Quotes: Single quotes
// Semicolons: Yes

const exampleFunction = (param1: string, param2: number): object => {
  const result = {
    key1: 'value1',
    key2: 'value2',
  };
  return result;
};
```

### JSON

```json
{
  "name": "example",
  "version": "1.0.0",
  "indent": "2 spaces"
}
```

### YAML

```yaml
# Indentation: 2 spaces
services:
  backend:
    image: python:3.12
    ports:
      - "8000:8000"
```

## 🚀 Quick Commands

### Format Everything

```bash
# From root
pnpm format              # Format all workspaces

# Individual workspaces
cd lyrica-backend && make format
cd lyrica-web && pnpm format
cd lyrica-mobile && pnpm format
```

### Lint Everything

```bash
# From root
pnpm lint                # Lint all workspaces

# Individual workspaces
cd lyrica-backend && make lint
cd lyrica-web && pnpm lint
cd lyrica-mobile && pnpm lint
```

### Check Formatting

```bash
# Check without making changes
npx prettier --check "**/*.{js,ts,tsx,json,md}"
```

## ⚙️ Customization

### Per-Workspace Overrides

Each workspace can have its own prettier config:

```javascript
// lyrica-web/.prettierrc.js
module.exports = {
  ...require('../.prettierrc.js'),
  // Override specific settings
  printWidth: 120,
};
```

### Backend-Specific Python Settings

Backend uses `pyproject.toml` for tool configuration:

```toml
[tool.black]
line-length = 100
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 100
```

## 🔍 Troubleshooting

### EditorConfig Not Working

1. Check if EditorConfig plugin is installed
2. Verify `.editorconfig` is in root directory
3. Restart your editor

### Prettier Not Formatting on Save

1. VSCode: Check `editor.formatOnSave` is `true`
2. Verify Prettier is the default formatter
3. Check file is not in `.prettierignore`

### Conflicting Settings

Priority order (highest to lowest):
1. Workspace settings (`.vscode/settings.json`)
2. EditorConfig (`.editorconfig`)
3. Prettier config (`.prettierrc.js`)
4. Editor defaults

### Mixed Indentation

If you see mixed tabs/spaces:

```bash
# Fix automatically
npx prettier --write "**/*.{js,ts,tsx,py,json,md}"

# Or per workspace
cd lyrica-backend && black . && isort .
cd lyrica-web && prettier --write "src/**/*"
```

## 📊 Configuration Summary

| Setting | Python | JS/TS | JSON | YAML | Markdown |
|---------|--------|-------|------|------|----------|
| Indent Style | Spaces | Spaces | Spaces | Spaces | Spaces |
| Indent Size | 4 | 2 | 2 | 2 | 2 |
| Max Line | 100 | 100 | 80 | - | 80 |
| Quotes | Double | Single | Double | Single | - |
| Semicolons | N/A | Yes | N/A | N/A | N/A |
| Trailing Comma | Yes | ES5 | No | Yes | N/A |

## 💡 Best Practices

1. **Always format before committing:**
   ```bash
   pnpm format && pnpm lint
   ```

2. **Enable format on save** in your editor

3. **Run linters locally** before pushing:
   ```bash
   pnpm lint && pnpm test
   ```

4. **Use pre-commit hooks** (already configured in backend):
   ```bash
   cd lyrica-backend
   pre-commit install
   ```

5. **Keep configs in sync** across team members

## 📚 Resources

- [EditorConfig](https://editorconfig.org/)
- [Prettier](https://prettier.io/)
- [Black](https://black.readthedocs.io/)
- [ESLint](https://eslint.org/)
- [Flake8](https://flake8.pycqa.org/)

---

**Consistent code style = Happy developers!** ✨

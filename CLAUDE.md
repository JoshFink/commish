# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Fantasy Football AI Commissioner application built with Streamlit that generates creative weekly recaps and power rankings using OpenAI models. The app integrates with ESPN, Sleeper, and Yahoo fantasy leagues to transform league data into entertaining character-driven narratives.

## Development Commands

### Running the Application
```bash
streamlit run app.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Docker Deployment
```bash
# Using Docker Compose (recommended)
docker-compose build
docker-compose up -d
docker-compose logs -f fantasy-commish

# Or direct Docker commands
docker build -t fantasy-commish .
docker run -d --name fantasy-commish -p 8501:8501 -v $(pwd)/.streamlit:/app/.streamlit fantasy-commish
```

## Architecture & Code Organization

### Core Application Structure
- **`app.py`** - Main Streamlit application with authentication, UI components, and routing
- **`utils/`** - Modular utility packages for specific functionalities:
  - `summary_generator.py` - OpenAI integration and streaming response handling
  - `power_ranking_generator.py` - Statistical power rankings with multiple algorithms
  - `model_config.py` - OpenAI model definitions, pricing, and cost calculations
  - `espn_helper.py`, `sleeper_helper.py`, `yahoo_helper.py` - Fantasy platform API integrations
  - `pdf_generator.py` - PDF export functionality for summaries
  - `helper.py` - General utilities and week calculations

### Authentication System
The app uses password-based authentication with 24-hour session persistence:
- Password stored in Streamlit secrets as `APP_PASSWORD`
- Session management via `check_authentication()` function in `app.py`
- Automatic logout after 24 hours

### Fantasy League Integration
- **ESPN**: Requires League ID, SWID, and ESPN_S2 tokens
- **Sleeper**: Only requires League ID
- **Yahoo**: Legacy support (backend only)

Each platform has dedicated helper modules that abstract API calls and data formatting.

## Configuration & Secrets

### Required Secrets (`.streamlit/secrets.toml`)
```toml
[default]
APP_PASSWORD = "your_secure_password_here"
OPENAI_ORG_ID = "your_openai_org_id"
OPENAI_API_PROJECT_ID = "your_project_id"
OPENAI_COMMISH_API_KEY = "your_api_key"
```

### Streamlit Configuration
- Custom theme defined in `.streamlit/config.toml`
- Uses dark theme with cyan primary color
- Logger level set to 'info'

## Key Technical Details

### OpenAI Integration
- Lazy client initialization in `get_openai_client()` to avoid startup conflicts
- Custom HTTP client configuration with timeout and connection limits
- Streaming response support for real-time summary generation
- Content moderation via `moderate_text()` function
- Cost tracking and model recommendations

### Power Rankings System
The `PowerRankingCalculator` class implements multiple ranking algorithms:
- **Comprehensive Power Score**: Weighted combination of win%, scoring, differential, form, consistency
- **Oberon Mt. Power Rating**: 60% avg score + 20% high/low average + 20% win%
- **Team Value Index**: (Points For / Points Against) × Win Percentage

### Data Handling
- Week calculation logic handles NFL season scheduling
- Player data cached in `players_data.json`
- Pandas used for statistical calculations and data manipulation

### Error Handling & Logging
- `suppress_warnings.py` imported first to manage library warnings
- Streamlit logger used throughout (`LOGGER = get_logger(__name__)`)
- Graceful fallbacks for API failures and missing data

## Development Notes

- No formal testing framework setup - relies on manual testing
- No linting/formatting configuration files present
- Authentication testing logic included in `AUTHENTICATION_SETUP.md`
- Uses latest versions of fantasy API libraries (ESPN 0.45.1, Sleeper 1.1.0)
- OpenAI client version 1.107.0 with httpx 0.28.1 for HTTP handling

## Common Tasks

When working with fantasy league APIs, always check the helper modules first - they contain platform-specific logic for data extraction and formatting. When adding new OpenAI models, update both `OPENAI_MODELS` and `MODEL_PRICING` dictionaries in `model_config.py`.
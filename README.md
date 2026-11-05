# 🍎 AI-Powered Nutrition Coach

An intelligent nutrition assistant that helps you track meals and get healthy meal suggestions using Groq API.

## Features

- **Log Meals**: Submit what you ate and get estimated calories
- **Smart Suggestions**: AI-powered healthy meal recommendations using Groq LLM
- **Target Daily Calories**: Suggestions consider your target daily calorie intake
- **Meal History**: Track your food intake over time
- **Modern UI**: Built with FastAPI + Streamlit

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (Streamlit Frontend)                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │    Web       │  │   Logger     │  │    Meal      │  │
│  │   Search     │  │    Agent     │  │  Suggester   │  │
│  │   Agent      │  │   (CSV File) │  │   (Groq)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## User Flow

1. **User submits meal** (e.g., "chicken salad with olive oil dressing")
2. **Web Search Agent** estimates calories
3. **Logger Agent** records entry to CSV file (user name + timestamp)
4. **Meal Suggester Agent** suggests a healthy follow-up meal with recipe, considering the target daily calorie intake

## Quick Start

### Prerequisites

- Python 3.10+
- uv (recommended) or pip

### Installation

Using uv (recommended):
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize and install
cd nutrition-coach
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### Configuration

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Add your Groq API key in `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key at: https://console.groq.com/

The application uses CSV file logging by default. Google Sheets configuration is optional and not required for basic functionality.

### Running the Application

Start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

In a new terminal, start Streamlit:
```bash
streamlit run app/streamlit_app.py
```

Access the app at:
- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nutrition/log` | Log a meal and get calories |
| GET | `/api/nutrition/history/{user_name}` | Get user's meal history |
| POST | `/api/nutrition/suggest` | Get meal suggestion |
| GET | `/api/nutrition/health` | Health check |

## Project Structure

```
nutrition-coach/
├── config/
│   └── settings.py          # Environment configuration
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── streamlit_app.py     # Streamlit frontend
│   ├── routers/
│   │   └── nutrition.py     # API endpoints
│   ├── services/
│   │   ├── web_search.py    # Web search agent
│   │   ├── logger.py        # CSV file logger agent
│   │   └── meal_suggester.py # Meal suggestion agent (Groq LLM)
│   └── models/
│       └── nutrition.py     # Pydantic models
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Nutrition Coach" |
| `DEBUG` | Enable debug mode | True |
| `HOST` | Server host | "0.0.0.0" |
| `PORT` | Server port | 8000 |
| `GROQ_API_KEY` | Groq API key | "" |
| `GOOGLE_SHEETS_SPREADSHEET_ID` | Google Sheets spreadsheet ID (not used - CSV logging) | "" |
| `TARGET_DAILY_CALORIES` | Target daily calorie intake for suggestions | 2000 |
| `GOOGLE_SHEETS_SHEET_NAME` | Sheet name for logging (not used - CSV logging) | "MealLog" |

## License

MIT
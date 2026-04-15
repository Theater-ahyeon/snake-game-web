# Snake Game Pro - Backend

Flask backend for the Snake Game Pro web version.

## Features

- **User Authentication**: Register, login, logout
- **Game Saves**: Save and load game progress
- **Leaderboards**: Global leaderboards by game mode
- **Endless Mode Tracking**: Track endless mode statistics
- **Level System**: 8 levels with unlock requirements
- **User Progress**: Track total score, games played, achievements

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/profile` | GET | Get user profile |

### Game Saves

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/saves` | GET | Get all user saves |
| `/api/saves` | POST | Create new save |
| `/api/saves/<id>` | GET | Load a save |
| `/api/saves/<id>` | PUT | Update a save |
| `/api/saves/<id>` | DELETE | Delete a save |

### Leaderboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/leaderboard` | GET | Get leaderboard (query: game_mode) |
| `/api/leaderboard` | POST | Submit score |

### Endless Mode

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/endless` | POST | Submit endless record |
| `/api/endless/stats` | GET | Get endless stats |

### Levels

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/levels` | GET | Get all levels |
| `/api/levels/<id>/unlock` | POST | Check level unlock |

### Statistics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Get user statistics |
| `/api/achievements` | GET | Get all achievements |
| `/api/achievements/unlock` | POST | Unlock achievement |

## Database

SQLite database `snake_game.db` is automatically created on first run.

### Tables

- **users**: User accounts
- **game_saves**: Saved game states
- **user_progress**: User statistics
- **leaderboard**: High scores
- **endless_records**: Endless mode records

## Frontend Connection

The frontend connects to the backend at `http://localhost:5000/api`.

To run the frontend, simply open `index.html` in a browser.

For production, update `API_BASE` in `index.html` to point to your server.

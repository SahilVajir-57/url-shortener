# URL Shortener API

A high-performance URL shortener API with Redis caching and analytics.

## Features

- **URL Shortening**: Convert long URLs to short, shareable links
- **Custom Codes**: Create custom short codes (e.g., `short.ly/my-brand`)
- **Redis Caching**: Fast redirects with minimal database hits
- **Click Analytics**: Track clicks, referrers, and daily statistics
- **Rate Limiting**: Prevent abuse with Redis-based rate limiting
- **URL Expiration**: Set optional expiration dates

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache**: Redis
- **ORM**: SQLAlchemy (async)
- **Testing**: pytest
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/url-shortener.git
cd url-shortener
```

2. Create environment file:

```bash
cp .env.example .env
```

3. Start the application:

```bash
docker-compose up --build
```

4. Access the API:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                  | Description              |
| ------ | ------------------------- | ------------------------ |
| POST   | `/shorten`                | Create a short URL       |
| GET    | `/{short_code}`           | Redirect to original URL |
| GET    | `/{short_code}/stats`     | Get basic URL stats      |
| GET    | `/{short_code}/analytics` | Get detailed analytics   |
| DELETE | `/{short_code}`           | Deactivate a URL         |

## Usage Examples

### Shorten a URL

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

Response:

```json
{
  "short_code": "aB3xY9k",
  "short_url": "http://localhost:8000/aB3xY9k",
  "original_url": "https://www.example.com/very/long/url",
  "clicks": 0,
  "is_active": true,
  "expires_at": null,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Custom Short Code

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com", "custom_code": "gh"}'
```

### Get Analytics

```bash
curl http://localhost:8000/aB3xY9k/analytics
```

Response:

```json
{
  "short_code": "aB3xY9k",
  "original_url": "https://www.example.com/very/long/url",
  "total_clicks": 150,
  "daily_clicks": [
    { "date": "2024-01-01", "clicks": 50 },
    { "date": "2024-01-02", "clicks": 100 }
  ],
  "top_referrers": [
    { "referrer": "https://twitter.com", "count": 80 },
    { "referrer": "https://facebook.com", "count": 40 }
  ]
}
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI   │────▶│    Redis    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           │ Cache Miss        │ Cache Hit
                           ▼                   │
                    ┌─────────────┐            │
                    │ PostgreSQL  │◀───────────┘
                    └─────────────┘
```

## Rate Limiting

- **URL Creation**: 5 requests per minute per IP
- **Redirects**: 10 requests per minute per IP

## Running Tests

```bash
docker-compose exec web pytest -v
```

## Project Structure

```
url-shortener/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API endpoints
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   │   ├── shortener.py # URL shortening
│   │   ├── cache.py     # Redis caching
│   │   ├── analytics.py # Click tracking
│   │   └── rate_limiter.py
│   ├── utils/           # Utilities
│   │   └── base62.py    # Encoding
│   ├── config.py
│   ├── database.py
│   └── main.py
├── tests/
├── alembic/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Environment Variables

| Variable       | Description                  | Default               |
| -------------- | ---------------------------- | --------------------- |
| `DATABASE_URL` | PostgreSQL connection string | -                     |
| `REDIS_URL`    | Redis connection string      | -                     |
| `BASE_URL`     | Base URL for short links     | http://localhost:8000 |

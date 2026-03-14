# Stock Screener Backend

This is a Django REST Framework (DRF) backend application designed for screening stocks based on end-of-day price data and specific technical candlestick patterns.

## Features

- **Stock Price Processing:** Fetches and stores historical end-of-day stock prices and delivery data.
- **Delivery Analysis:** Calculates average 30-day delivery percentages and compares them against the latest delivery percentages.
- **Candlestick Pattern Detection:** Identifies the following daily candlestick patterns:
  - Hammer
  - Inverted Hammer
  - Bullish Engulfing
  - Bearish Engulfing
  - Doji
  - Bullish Kicker
  - Bearish Kicker
  - Pro Gap Positive
  - Pro Gap Negative
- **Index Filtering:** Allows filtering stock screens by major indices like NIFTY 50, NIFTY NEXT 50, NIFTY 100, NIFTY 200, and NIFTY 500.
- **RESTful API:** Provides well-structured JSON API endpoints.
- **API Documentation:** Integrated Swagger UI and ReDoc for comprehensive endpoint documentation.

## Tech Stack

- **Python** (3.x)
- **Django** (6.0.3)
- **Django REST Framework** (3.16.1)
- **PostgreSQL** (Database)
- **drf-yasg** (Swagger/ReDoc API Documentation)

## Setup Instructions

### 1. Prerequisites
- Python 3.10+ installed
- PostgreSQL installed and running

### 2. Environment Setup

Clone the repository and set up a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configuration

Create a `.env` file in the root directory and add your PostgreSQL database credentials:

```env
POSTGRES_DB=your_db_name
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

*(Note: Change these values to match your local PostgreSQL setup).*

### 5. Database Migrations

Apply the database migrations to set up the schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The backend should now be running locally at `http://127.0.0.1:8000/`.

## API Documentation

You can explore the available API endpoints using the automatically generated documentation directly in your browser:

- **Swagger UI:** `http://127.0.0.1:8000/swagger/`
- **ReDoc:** `http://127.0.0.1:8000/redoc/`

## Key API Endpoints

- **Create/Update Stock Prices:**
  - `POST /create-stock-prices/` - Fetches and stores NSE stock price data and computes technical patterns.

- **Candlestick Patterns (GET):**
  *(Supports `?index=nifty_50` query parameter filtering)*
  - `/patterns/hammer/`
  - `/patterns/inverted-hammer/`
  - `/patterns/bullish-engulfing/`
  - `/patterns/bearish-engulfing/`
  - `/patterns/doji/`
  - `/patterns/bullish-kicker/`
  - `/patterns/bearish-kicker/`
  - `/patterns/pro-gap-positive/`
  - `/patterns/pro-gap-negative/`

- **Delivery Data Analysis:**
  - `GET /delivery-data/` - Returns the latest delivery percentage vs. 30-day average. Supports `?index=nifty_50` and `?only_greater=true` query parameters.

## Logging

Application logs are stored in the automatically created `stock_screener_logs` directory at the project root.

# Influencer Affiliate Sales & Payment Tracking Platform

A full-stack web application for tracking influencer-driven affiliate sales, managing payments, and providing AI-powered analytics.

## Features

### Core Features
- **User Roles**: Admin, Influencer, Finance Team
- **Affiliate Tracking**: Unique referral codes, click tracking, conversion tracking
- **Payment Management**: Commission calculation, payment statuses, history tracking
- **Visual Dashboard**: Charts (Recharts), sales analytics, performance metrics
- **Export Reports**: CSV and PDF export functionality

### AI-Powered Features
- **Sales Prediction**: ML-based forecasting of next 7/30 days sales using historical data
- **Influencer Performance Insights**: AI-generated recommendations and performance scoring
- **Fraud Detection**: Automatic detection of suspicious click patterns

## Tech Stack

### Backend
- **Django** + Django REST Framework
- **PostgreSQL** (or SQLite for development)
- **JWT Authentication** (djangorestframework-simplejwt)
- **Groq API** for AI insights
- **scikit-learn** for ML predictions
- **Celery + Redis** for async tasks
- **ReportLab** for PDF generation

### Frontend
- **React 18**
- **React Router** for navigation
- **Recharts** for data visualization
- **Tailwind CSS** for styling
- **Lucide React** for icons

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL (optional, SQLite works for development)

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The app will be available at `http://localhost:3000`

### Environment Variables

Create a `.env` file in the backend directory:

```
SECRET_KEY=your-secret-key
DEBUG=True
USE_SQLITE=true
DB_NAME=influencer_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=your-groq-api-key
```

## API Endpoints

### Authentication
- `POST /api/auth/login/` - JWT login
- `POST /api/auth/refresh/` - Token refresh
- `POST /api/auth/register/` - User registration
- `GET /api/auth/me/` - Current user info

### Core
- `GET /api/influencers/` - List influencers
- `POST /api/influencers/` - Create influencer
- `GET /api/sales/` - List sales
- `POST /api/sales/` - Create sale (webhook)
- `PATCH /api/sales/<id>/` - Update sale status
- `GET /api/track/<referral_code>/` - Track click
- `GET /api/dashboard/stats/` - Dashboard statistics

### Analytics (AI Features)
- `GET /api/analytics/predictions/` - Sales predictions
- `GET /api/analytics/insights/` - Performance insights
- `GET /api/analytics/fraud-detection/` - Fraud alerts
- `GET /api/analytics/top-influencers/` - Top performers

### Payments
- `GET /api/payments/` - List payments
- `POST /api/payments/` - Create payment
- `GET /api/payments/summary/` - Payment summary
- `GET /api/payments/export/csv/` - Export CSV
- `GET /api/payments/export/pdf/` - Export PDF

## Database Schema

### Users
- id, email, username, role (admin/influencer/finance)
- password, phone, is_active, created_at

### Influencers
- id, user_id (FK), referral_code, commission_rate
- bio, social_handle, total_earnings, pending_amount
- is_active, created_at

### Sales
- id, influencer_id (FK), order_id, amount, commission
- status (pending/approved/rejected/paid), customer_email
- created_at, updated_at

### Clicks
- id, influencer_id (FK), ip_address, user_agent
- referrer, converted (boolean), created_at

### Payments
- id, influencer_id (FK), amount, status
- payment_method, transaction_id, created_at, completed_at

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Influencer | influencer@example.com | inf123 |
| Finance | finance@example.com | fin123 |

## AI Features Details

### Sales Prediction
Uses Linear Regression to predict future sales based on:
- Historical daily sales data (last 90 days)
- Trend analysis
- Confidence scoring

### Performance Insights
Analyzes:
- Conversion rates by day of week
- Click-to-sale ratios
- Average order values
- Performance scoring (0-100)
- Personalized recommendations

### Fraud Detection
Detects:
- Multiple clicks from same IP (>50/hour)
- Abnormally high conversion rates (>80%)
- Bot-like click patterns

## Project Structure

```
.
├── backend/
│   ├── influencer_platform/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── core/
│   │   ├── models.py (User, Influencer, Sale, Click, Campaign)
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── analytics/
│   │   ├── views.py (AI features)
│   │   └── urls.py
│   ├── payments/
│   │   ├── models.py (Payment, BankAccount)
│   │   ├── views.py
│   │   └── urls.py
│   └── manage.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── services/
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── requirements.txt
└── README.md
```

## Deployment

### Backend (Heroku/Railway)
```bash
gunicorn influencer_platform.wsgi:application
```

### Frontend (Netlify/Vercel)
```bash
npm run build
# Deploy build/ folder
```

## License
MIT

## Support
For issues and feature requests, please open an issue on GitHub.

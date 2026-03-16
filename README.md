# RailBusAtithi 🚌🚂

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

A full-stack **Flask** travel booking website that helps travelers find and book hotels near railway stations and bus stands across India. Perfect for short stays and transit accommodations.

## 🚀 Features

- **Smart Hotel Search**: Filter by city, near railway stations or bus stands
- **Multi-Role System**: Passengers, Hotel Owners, Admin dashboard
- **Passenger**: Book rooms, manage bookings, rate/review hotels, favorites
- **Hotel Owner**: Add hotels, manage bookings & availability, analytics
- **Admin**: Approve hotels, user management, system analytics, ads
- **Password Reset**: Secure email-based reset (mock console output)
- **Responsive UI**: Modern travel-themed design, mobile-friendly

## 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Flask, Flask-SQLAlchemy |
| **Database** | SQLite (dev), PostgreSQL compatible |
| **Frontend** | HTML5, CSS3, Vanilla JS |
| **Security** | Werkzeug, itsdangerous (signed tokens) |
| **Deployment** | Vercel/Render/Heroku ready |

## 📁 Project Structure

```
RailBusAtithi/
├── app.py                 # Main Flask app
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignores
├── LICENSE               # MIT License
├── instance/             # DB & config (ignored)
│   └── database.db
├── static/               # CSS/JS/Images
│   ├── css/
│   ├── js/
│   └── uploads/          # User uploads (ignored)
├── templates/            # HTML templates
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Setup

```bash
git clone <your-repo> RailBusAtithi
cd RailBusAtithi
```

### 2. Environment Setup

```bash
# Copy example
cp .env.example .env

# Edit .env with your SECRET_KEY (generate: python -c "import secrets; print(secrets.token_urlsafe(50))")
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Development Server

```bash
python app.py
```

**Visit**: [http://localhost:5101](http://localhost:5101)

## 🔐 Demo Accounts (Auto-created)

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@railbusatithi.com | admin123 |
| **Hotel Owner** | rahul@hotel.com | owner123 |
| **Passenger** | amit@email.com | passenger123 |

## 🛠 Development Workflow

1. **Local Dev**: Uses SQLite (`instance/database.db`)
2. **Sample Data**: Auto-populates on first run (users/hotels/bookings)
3. **File Uploads**: Photos to `static/uploads/` (ignored in git)
4. **Password Reset**: Console logs mock URLs for dev

## ☁️ Deployment

### Vercel (Serverless)
1. Push to GitHub
2. Import in Vercel
3. Add env vars: `SECRET_KEY`, `DATABASE_URL` (use Vercel Postgres)
4. Build: Auto (Python runtime)

### Render/Heroku
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret
```

**Note**: Update `app.py` DB path for prod DB.

## 📱 Screenshots

*(Add screenshots of home, dashboard, search)*

## 🤝 Contributing

1. Fork repo
2. Create feature branch
3. PR to `main`

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

**Made with ❤️ for travelers** | Questions? Open an issue!

"# Railbus-Atithi" 
"# Railbus-Atithi" 

# eSociety — Society Management Portal

A full-stack web application built with Django for managing residential society operations. eSociety provides role-based access control, gate management, AI-powered insights, and a complaint tracking system — all in one unified platform.

---

## 🔗 Live Demo

> Coming soon — deployment in progress

---

## 📸 Screenshots

### Admin Dashboard
![Admin Dashboard](screenshots/admin_dashboard.png)

### Security Dashboard
![Security Dashboard](screenshots/security_dashboard.png)

### Member Dashboard
![Member Dashboard](screenshots/member_dashboard.png)

### Visitor List
![Visitor List](screenshots/visitor_list.png)

### Complaint System
![Complaints](screenshots/complaints.png)

### AI Dashboard
![AI Dashboard](screenshots/ai_dashboard.png)
---

## 🚀 Features

### Gate Management
- **Visitor Management** — Log, approve, and reject visitor requests with role-based control
- **Delivery Management** — Track incoming deliveries and collection status
- **Entry Logs** — Visitor, delivery, and child entry/exit logs managed by security

### Resident Features
- **Child Monitoring** — Register children and track their movement
- **Complaint System** — Raise maintenance complaints with Open → In Progress → Resolved workflow
- **Visitor Approval** — Members approve or reject their own visitors directly

### Society Operations
- **Staff Attendance** — Mark and track daily attendance for security and helper staff
- **Society Notices** — Post announcements visible to all residents
- **Society Settings** — Control visitor and delivery permissions globally

### AI Intelligence Layer
- **AI Insights** — Trend-based analysis of visitor and delivery activity
- **Smart Alert Engine** — Automated alerts for unusual patterns
- **Risk Watchlist** — AI-generated risk detection and scoring
- **Society Health Score** — Overall society activity health out of 100
- **eSociety Copilot** — Role-based AI assistant with priority tasks and recommendations

### System Features
- **Role-Based Access Control** — 5 distinct roles with granular permissions
- **Search with Autocomplete** — AJAX-powered search across all modules
- **Consistent Dark UI** — Professional dark theme with a unified design system
- **Responsive Design** — Works across desktop browsers

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 6.0 |
| Database | PostgreSQL |
| Frontend | HTML, CSS (Custom Dark UI), JavaScript |
| Fonts | Poppins, JetBrains Mono |
| Auth | Custom email-based authentication |
| AI | Custom AI services (no external API) |
| Version Control | Git + GitHub |

---

## 👥 Roles and Permissions

| Role | Access |
|---|---|
| **Super Admin** | Full access — all modules, AI dashboard, complaints, settings |
| **Chairman** | Full access — same as super admin |
| **Member** | Own visitors, deliveries, children, complaints, notices |
| **Security** | Gate operations — visitors, deliveries, logs, attendance |
| **Helper** | Notices and AI Copilot only |

---

## 📁 Project Structure

```
eSociety/
│
├── core/                   # Authentication — custom user model, login, signup
├── society/                # Main modules — visitors, deliveries, complaints, etc.
│   ├── models.py           # All data models
│   ├── views.py            # All view functions
│   ├── forms.py            # All form classes
│   ├── urls.py             # URL routing
│   ├── decorators.py       # role_required() decorator
│   └── static/society/css/
│       └── society.css     # Complete UI design system
│
├── ai/                     # AI intelligence layer
│   └── services/
│       ├── insights.py     # Trend-based AI insights
│       ├── alerts.py       # Smart alert engine
│       ├── risk_analysis.py# Risk watchlist
│       ├── health_score.py # Society health score
│       └── copilot.py      # Role-based AI assistant
│
├── templates/
│   ├── society/            # All society templates (25+ files)
│   └── ai/                 # AI dashboard and copilot templates
│
└── manage.py
```

---

## ⚙️ Local Setup

Follow these steps to run eSociety on your local machine.

### Prerequisites
- Python 3.10+
- PostgreSQL installed and running
- Git

### Step 1 — Clone the repository

```bash
git clone https://github.com/7990691553/eSoceity_Management_System.git
cd eSoceity_Management_System
```

### Step 2 — Create and activate virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://username:password@localhost:5432/esociety_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5 — Set up the database

```bash
# Create database in PostgreSQL first, then:
python manage.py makemigrations
python manage.py migrate
```

### Step 6 — Create a superuser

```bash
python manage.py createsuperuser
```

### Step 7 — Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/society/` in your browser.

---

## 🔐 Default Test Accounts

After setup, create users with these roles for testing:

| Role | How to create |
|---|---|
| Super Admin | Use `createsuperuser` command |
| Chairman | Sign up → set role via admin panel |
| Member | Sign up → set role via admin panel |
| Security | Sign up → set role via admin panel |
| Helper | Sign up → set role via admin panel |

---

## 📊 Data Models

| Model | Description |
|---|---|
| `Visitor` | Visitor requests with approval workflow |
| `VisitorEntryLog` | Entry and exit time tracking |
| `Delivery` | Incoming deliveries with collection status |
| `DeliveryLog` | Delivery received and collected times |
| `Child` | Registered children profiles |
| `ChildEntryLog` | Child entry and exit tracking |
| `StaffAttendance` | Daily staff attendance records |
| `SocietyNotice` | Society announcements |
| `SocietySettings` | Global society configuration (singleton) |
| `Complaint` | Maintenance complaints with status workflow |

---

## 🤖 AI Module

The AI layer is built as a custom service module with no external API dependency.

| Service | Function |
|---|---|
| `generate_ai_insight()` | Analyses visitor and delivery trends |
| `generate_smart_alerts()` | Detects unusual activity patterns |
| `generate_risk_watchlist()` | Scores and flags risk items |
| `generate_society_health_score()` | Calculates overall society health out of 100 |
| `generate_copilot_context(user)` | Generates role-specific guidance and tasks |

---

## 🎨 UI Design System

All styles are in a single CSS file: `society/static/society/css/society.css`

Key components:
- `.dash-grid` — responsive grid layout (cols-1 through cols-4)
- `.stat-card` — KPI cards with color accent bars
- `.panel-card` — content panels with headers
- `.status-badge` — color-coded status indicators
- `.search-fused` — compact integrated search bar
- `.action-row` — inline action rows for quick actions

---

## 🗺️ Roadmap

- [ ] Email notifications (visitor arrived, delivery ready)
- [ ] Gate pass QR code generation
- [ ] Society Settings management UI
- [ ] User management page (no Django admin needed)
- [ ] Analytics dashboard with charts
- [ ] Deployment to Railway / Render
- [ ] Unit tests

---

## 👨‍💻 Developer

**Keshav Pancholi**
Final Year Project — 2026

---

## 📄 License

This project is submitted as an academic project for final year evaluation.
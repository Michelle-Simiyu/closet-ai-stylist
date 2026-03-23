# 👗 Closet AI Stylist

> **AI-powered personal wardrobe assistant** — upload your clothing and get personalized outfit combinations in seconds.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-2.x-FF3E00?logo=svelte)](https://kit.svelte.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://typescriptlang.org)

---

## ✨ What is Closet AI?

Closet AI is a production-ready prototype of an AI personal stylist. Users catalog their clothing, and the AI generates personalized outfit combinations from their existing wardrobe using:

- **Color harmony rules** (neutral anchors, complementary pairs, analogous groups)
- **Formality matching** (ensures consistent dress codes across pieces)
- **Style coherence** (casual, formal, sporty, bohemian, minimalist)
- **Occasion filtering** (casual, work, formal, party, date)
- **Weather adaptation** (mock weather API for temperature-aware suggestions)
- **Personalization** (style quiz + feedback learning from likes/dislikes)

**Magic Moment:** User loads demo wardrobe → clicks Generate → receives 3-5 styled outfits with compatibility scores and styling tips in under 2 seconds.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Git

### Local Development (5 minutes)

```bash
# 1. Clone
git clone https://github.com/yourusername/closet-ai-stylist.git
cd closet-ai-stylist

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Edit .env if needed

# 3. Start backend (in one terminal)
uvicorn src.main:app --reload --port 8000

# 4. Frontend setup (in another terminal)
cd frontend
npm install
npm run dev

# 5. Open browser
open http://localhost:5173
```

### Docker (recommended for demos)

```bash
cp .env.example .env
docker-compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

### Make commands

```bash
make install        # Install all dependencies
make dev-backend    # Start backend with hot reload
make dev-frontend   # Start frontend dev server
make test           # Run backend tests
make test-coverage  # Run tests with coverage report
make docker-up      # Start with Docker Compose
make docker-down    # Stop Docker services
```

---

## 🎯 Demo Mode

The fastest way to see the magic moment:

1. Register an account at `http://localhost:5173/register`
2. Complete the style quiz (takes 30 seconds)
3. Click **"Load Demo Wardrobe"** — loads 10 pre-styled items
4. Navigate to **Outfits** → click **Generate**
5. Receive 3-5 AI-styled outfits with scores and tips!

Alternatively, skip registration and use the demo directly via `/onboarding`.

---

## 🏗️ Architecture

```
closet-ai/
├── backend/                    # FastAPI Python backend
│   ├── src/
│   │   ├── api/v1/endpoints/   # REST endpoints
│   │   │   ├── auth.py         # Register, login, JWT
│   │   │   ├── closet.py       # CRUD for clothing items
│   │   │   ├── outfits.py      # Generate, save, like
│   │   │   ├── ai.py           # Image analysis
│   │   │   └── weather.py      # Mock weather data
│   │   ├── core/               # Config, DB, security, exceptions
│   │   ├── models/             # SQLModel ORM models
│   │   │   ├── user.py
│   │   │   ├── clothing.py
│   │   │   ├── outfit.py
│   │   │   └── feedback.py
│   │   ├── services/           # Business logic layer
│   │   │   ├── closet_service.py
│   │   │   ├── outfit_service.py
│   │   │   └── ai_service.py
│   │   └── ai/                 # AI engine
│   │       ├── color_analyzer.py   # Color harmony rules
│   │       ├── rules_engine.py     # Formality/style/season rules
│   │       ├── compatibility.py    # Weighted scoring (0-100)
│   │       └── image_processor.py  # Background removal, resizing
│   └── tests/                  # pytest test suite
│
├── frontend/                   # SvelteKit TypeScript frontend
│   └── src/
│       ├── routes/             # File-based routing
│       │   ├── +page.svelte    # Landing page
│       │   ├── login/          # Auth pages
│       │   ├── register/
│       │   ├── onboarding/     # Style quiz + demo load
│       │   ├── closet/         # Wardrobe management
│       │   └── outfits/        # Generator + saved
│       └── lib/
│           ├── components/     # Reusable UI components
│           ├── stores/         # Svelte reactive stores
│           ├── api/            # Typed API client
│           └── utils/          # Analytics, helpers
│
├── docker-compose.yml
├── render.yaml                 # Render deployment
├── railway.json                # Railway deployment
└── Makefile
```

### AI Engine — Compatibility Scoring

Outfits are scored 0–100 using weighted rules:

| Dimension | Weight | Rules |
|-----------|--------|-------|
| Formality consistency | 30% | Max gap of 1 = perfect; gap > 3 = penalty |
| Color harmony | 25% | Neutrals always pass; complementary/analogous pairs score high |
| Style coherence | 20% | Casual + minimalist = compatible; sporty + formal = penalty |
| Outfit completeness | 15% | Has top+bottom or dress; bonus for shoes/accessories |
| Weather / Season | 10% | Cold weather requires outerwear; summer items in summer |

---

## 📡 API Reference

Interactive docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/quiz` | Save style quiz |
| GET | `/api/v1/closet` | List all clothing items |
| POST | `/api/v1/closet` | Add clothing item |
| PUT | `/api/v1/closet/{id}` | Update item |
| DELETE | `/api/v1/closet/{id}` | Delete item |
| POST | `/api/v1/closet/upload` | Upload image (+ background removal) |
| POST | `/api/v1/closet/demo` | Load demo wardrobe |
| GET | `/api/v1/closet/stats` | Wardrobe analytics |
| POST | `/api/v1/outfits/generate` | Generate AI outfits |
| GET | `/api/v1/outfits/saved` | Get saved outfits |
| POST | `/api/v1/outfits/{id}/save` | Save an outfit |
| POST | `/api/v1/outfits/{id}/like` | Like/dislike outfit |
| POST | `/api/v1/ai/analyze` | Analyze clothing image |
| GET | `/api/v1/weather` | Get mock weather |
| GET | `/health` | Health check |

### Example: Generate Outfits

```bash
curl -X POST http://localhost:8000/api/v1/outfits/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"occasion": "casual", "max_outfits": 5}'
```

Response:
```json
{
  "outfits": [
    {
      "id": "uuid",
      "items": [{"id": "...", "name": "White Shirt", ...}],
      "compatibility_score": 87.5,
      "feedback": ["Classic neutral palette", "Formality levels are consistent"],
      "description": "A great casual look: white shirt + navy jeans",
      "occasion": "casual"
    }
  ],
  "count": 5,
  "occasion": "casual",
  "generation_time_ms": 45.2
}
```

---

## 🔧 Configuration

### Environment Variables

**Backend** (`backend/.env`):

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | JWT signing key (use `openssl rand -hex 32`) |
| `DATABASE_URL` | No | SQLite path (default: `sqlite:///./closet_ai.db`) |
| `CLOUDINARY_CLOUD_NAME` | No | Cloudinary cloud name for image hosting |
| `CLOUDINARY_API_KEY` | No | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | No | Cloudinary API secret |
| `FRONTEND_URL` | No | CORS origin (default: `http://localhost:5173`) |
| `DEBUG` | No | Enable debug logging (default: `false`) |

**Frontend** (`frontend/.env`):

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_POSTHOG_KEY` | No | PostHog analytics key |

### Optional Services (Free Tier)

**Cloudinary** (image hosting):
1. Sign up at [cloudinary.com](https://cloudinary.com) — free tier includes 25GB storage
2. Add credentials to `backend/.env`

**PostHog** (analytics):
1. Sign up at [posthog.com](https://posthog.com) — free for <1M events/month
2. Add API key to `frontend/.env` as `VITE_POSTHOG_KEY`

---

## 🚢 Deployment

### Render (Recommended — free tier)

```bash
# 1. Fork/push this repo to GitHub
# 2. Go to render.com → New → Blueprint
# 3. Connect your repo — Render reads render.yaml automatically
# 4. Set environment variables in the Render dashboard
# 5. Deploy!
```

The `render.yaml` configures:
- Backend as a Python web service on port 8000
- Frontend as a Node.js web service on port 3000
- Auto-generated `SECRET_KEY`

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Deploy backend
cd backend
railway up

# Deploy frontend
cd frontend
railway up
```

### Manual / VPS

```bash
# Backend
cd backend
pip install -r requirements.txt
gunicorn src.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
node build/index.js  # or serve with nginx
```

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest -v

# Run specific test module
pytest tests/test_compatibility.py -v
pytest tests/test_api.py -v
pytest tests/test_services.py -v

# With coverage
pytest --cov=src --cov-report=term-missing

# Coverage target: 80% on core modules
```

Test suite covers:
- Color harmony scoring and neutral detection
- Formality matching rules
- Style compatibility matrix
- Outfit completeness checking
- Weather appropriateness
- Full API endpoint integration tests
- CRUD service layer tests
- Feedback learning tests

---

## 🛡️ Security

| Aspect | Implementation |
|--------|---------------|
| Passwords | bcrypt hashing via passlib |
| Auth | JWT tokens, 24-hour expiry |
| CORS | Configured for frontend origin only |
| SQL | SQLModel ORM — no raw SQL |
| XSS | SvelteKit auto-escaping |
| Input validation | Pydantic models on all endpoints |
| File uploads | Content-type check + 10MB limit |

---

## 🔮 Future Features (Roadmap)

- **Native iOS/Android apps** — React Native / Swift
- **Advanced ML models** — Neural networks trained on fashion datasets (DeepFashion)
- **Social feed** — Share outfits, follow friends
- **Marketplace integration** — Affiliate shopping links for completing outfits
- **Virtual try-on** — AR overlay with clothing items
- **Professional stylist tools** — Client management, lookbooks
- **PostgreSQL + Redis** — Production-grade database and caching
- **Background job queue** — Celery for async image processing
- **Email notifications** — Weekly outfit suggestions

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `make test`
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Code Standards

- Python: type hints on all functions, docstrings for public APIs
- TypeScript: strict mode enabled
- Tests: aim for 80%+ coverage on new features
- Commits: conventional commits format preferred

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) — excellent async Python framework
- [SvelteKit](https://kit.svelte.dev) — delightful full-stack framework
- [SQLModel](https://sqlmodel.tiangolo.com) — SQLAlchemy + Pydantic unified
- [rembg](https://github.com/danielgatis/rembg) — background removal
- [Tailwind CSS](https://tailwindcss.com) — utility-first CSS
- [Lucide](https://lucide.dev) — beautiful open-source icons
- Fashion color theory from [Color Matters](https://colormatters.com)

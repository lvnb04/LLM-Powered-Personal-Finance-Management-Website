# Finny: LLM-Powered Personal Finance Companion

**Finny** is a comprehensive personal finance management web application designed to empower you on your journey to financial well-being. Our intelligent platform, powered by a Large Language Model (LLM), provides tools and insights to manage your money effectively, reach your goals, and build a secure future.

---

## 🎥 Demo Video

Video Drive Link -> "https://drive.google.com/file/d/1TBHLD12ag394HBm5nFK1TyNwCzmj2k5J/view?usp=sharing"

<img width="1280" height="801" alt="image" src="https://github.com/user-attachments/assets/a658cce4-bff6-46e4-b517-85fdd66562d3" />






---

## ✨ Key Features

- **🔐 Secure User Authentication**
  - Built with **Supabase Auth**—secure sign-up/login and protected user data.
- **👋 Interactive Onboarding**
  - Guided setup for income, saving goals, and spending habits.
- **📊 Comprehensive Dashboard**
  - Track expenses, savings progress, and recent transactions at a glance.
- **🤖 LLM-Powered Chatbot**
  - "Finny" answers questions about spending, provides personalized financial insights and recommendations.
  - Example usage: _"How much did I spend on groceries last month?"_
- **🎮 Gamified Experience**
  - Earn XP for tracking expenses and hitting goals. Unlock achievements and level up.
- **📈 Data Visualization**
  - Interactive charts and graphs (Recharts) to explore trends and patterns.
- **⚡ Real-time Updates**
  - Supabase Realtime keeps the UI in sync with DB changes.

---

## 🛠️ Tech Stack

### Frontend
- React (with TypeScript)
- Vite
- Tailwind CSS
- shadcn/ui
- Recharts

### Backend
- Python 3.10+
- FastAPI
- LangChain (for connecting LLM workflows)
- Google Generative AI (Gemini Pro) — used to power the chatbot

### Database
- Supabase (Postgres + Auth + Realtime)

---

## 🏗️ Project Architecture

The multi Page Application frontend (React) communicates with a FastAPI backend. The backend uses LangChain and the Google AI API to interact with the LLM. Supabase hosts the Postgres database, authentication, and real-time features.

---

## 🚀 Getting Started (Quick)

### Prerequisites
- Node.js v18+
- Python 3.10+
- Supabase account: Create a project at [Supabase](https://supabase.com)
- Google AI API Key (Gemini Pro): Obtain an API key from [Google Cloud](https://cloud.google.com) or [MakerSuite](https://makersuite.google.com)

---

## 📁 File Structure

The project is organized into the following directories:

- `public/`: Contains public assets, such as images and fonts.
- `src/`: Contains the source code for the frontend application.
  - `components/`: Reusable UI components.
  - `contexts/`: React contexts for managing global state.
  - `hooks/`: Custom React hooks for managing state and side effects.
  - `integrations/`: Code for integrating with third-party services, such as Supabase.
  - `lib/`: Utility functions.
  - `pages/`: Application pages.
- `backend/`: Contains the Python backend code.
  - `financial_chatbot.py`: The Python backend for the chatbot.
- `supabase/`: Contains Supabase configuration files.

---

## 🔧 Setup — Full Steps

> These commands assume you're at the repository root.

### 1. Clone the Repository
```bash
git clone https://github.com/bharateesha2004/llm-powered-finance-management-website.git
cd llm-powered-finance-management-website
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Backend Setup
In a separate terminal:
```bash
cd backend
python -m venv .venv
# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn financial_chatbot:app --reload --host 0.0.0.0 --port 8000
```

### 4. Database (Supabase) Setup
- Create a new project on [Supabase](https://supabase.com).
- From Supabase project settings, copy the `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and database connection info.
- Run the SQL script to enable real-time on the required tables:
  ```sql
  -- Run: src/integrations/supabase/enable-realtime.sql
  ```

### 🔐 Environment Variables
Create a `.env` file in the project root (or in the `frontend` and `backend` folders as appropriate). Example:

```env
# Google AI API Key
GOOGLE_API_KEY="YOUR_GOOGLE_AI_API_KEY"

# Supabase (frontend)
VITE_SUPABASE_URL="https://your-supabase-url.supabase.co"
VITE_SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"

# Supabase DB (backend)
SUPABASE_DB_HOST="your-db-host"
SUPABASE_DB_PORT="5432"
SUPABASE_DB_USER="your-db-user"
SUPABASE_DB_PASSWORD="your-db-password"
SUPABASE_DB_NAME="your-db-name"

# Test / Development
TEST_USER_ID="your-dev-test-user-id"
```

---

## 📜 API Endpoints (Example)

**POST /chatbot**

- **Input**: `{ "user_id": "<id>", "question": "<text>" }`
- **Output**: `{ "response": "<LLM response>", "meta": {...} }`
- **Purpose**: Send user message to the LLM and return the model reply.

---

## 🧪 Testing & Local Development Tips

- Use `curl` or Postman to test `POST /chatbot`:
  ```bash
  curl -X POST http://localhost:8000/chatbot \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test-user","question":"Show my last 10 transactions"}'
  ```
- Use Supabase local development or the Supabase web UI to inspect tables and real-time logs.

---

## ✅ Deployment Tips

- **Frontend**: Deploy on Vercel, Netlify, or GitHub Pages (from Vite build).
- **Backend**: Deploy FastAPI on Fly.io, Render, Railway, or a Dockerized VM.
- **Secrets**: Store `.env` variables in secret managers.
- **CORS**: Configure FastAPI to allow the frontend domain.

### Example `.env.production`
```env
GOOGLE_API_KEY="PROD_GOOGLE_AI_API_KEY"
VITE_SUPABASE_URL="https://your-prod.supabase.co"
VITE_SUPABASE_ANON_KEY="PROD_ANON_KEY"
SUPABASE_DB_HOST="prod-db-host"
SUPABASE_DB_USER="prod-user"
SUPABASE_DB_PASSWORD="prod-password"
SUPABASE_DB_NAME="prod-db"
```

---

## 🤝 Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feat/my-new-feature`
3. Commit: `git commit -m "feat: add X"`
4. Push: `git push origin feat/my-new-feature`
5. Open a Pull Request.

---

## 🧭 Roadmap & Ideas

- Expense auto-categorization with ML.
- Bill reminders and notifications.
- CSV import/export.
- Multi-currency support.
- Team accounts.

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

---

## 📬 Contact

- **Repo**: [llm-powered-finance-management-website](https://github.com/bharateesha2004/llm-powered-finance-management-website)
- Please open GitHub Issues or PRs for contributions.

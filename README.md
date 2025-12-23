markdown
# Alpha-Mechanism: The Self-Evolving Hedge Fund 🧠📈

**Alpha-Mechanism** is an autonomous quantitative research engine that converts academic papers into executable trading strategies using Multimodal AI (Gemini 1.5 Pro). It features a "Self-Evolving" architecture where Reinforcement Learning (RL) agents tune parameters in real-time and Multi-Armed Bandits ensure fair capital allocation.



### 🚀 Key Features

* **Scholar-Parser (Phase 1):** Uses Vision Language Models (VLM) to read PDF research papers, extract complex mathematical formulas, and generate valid Python strategy code automatically.
* **Vectorized Backtester (Phase 2):** High-performance event-driven engine built with `pandas` and `pandas_ta` to simulate strategy performance against historical market data (Crypto/Equities).
* **RL Tuning Agent (Phase 3):** A PPO (Proximal Policy Optimization) agent that dynamically adjusts strategy parameters (e.g., lookback periods) based on market volatility.
* **Fairness Controller (Phase 4):** Implements **Fair Thompson Sampling** (inspired by Dr. Shweta Jain's research) to allocate capital across strategies without "starving" new or high-variance models.
* **Alpha Dashboard (Phase 5):** A modern React + Tailwind interface for uploading papers, visualizing backtests, and monitoring the fund's equity curve.

---

### 🛠️ Tech Stack

**Backend (Python)**
* **AI Core:** Google Gemini 1.5 Pro/Flash (via `google-generativeai`)
* **API:** FastAPI (Asynchronous Web Server)
* **Quant:** Pandas, NumPy, Pandas-TA (Technical Analysis), YFinance
* **RL/ML:** Stable-Baselines3 (PPO), Gymnasium, AST (Code Validation)

**Frontend (React)**
* **Framework:** Vite + React.js
* **Styling:** Tailwind CSS
* **Visualization:** Recharts (Interactive Equity Curves)
* **State:** Axios, Lucide-React

---

### ⚙️ Installation & Setup

#### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/alpha-mechanism.git](https://github.com/YOUR_USERNAME/alpha-mechanism.git)
cd alpha-mechanism

```

#### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Activate Virtual Environment
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt

```

**Configuration:**
Create a `.env` file in the `backend/` folder and add your API key:

```env
GEMINI_API_KEY=your_google_ai_key_here

```

#### 3. Frontend Setup

```bash
cd ../frontend
npm install

```

---

### 🏃‍♂️ How to Run

You need two terminal windows running simultaneously.

**Terminal 1: The Backend**

```bash
cd backend
# Ensure venv is active
uvicorn main:app --reload

```

*Server runs at: http://127.0.0.1:8000*

**Terminal 2: The Frontend**

```bash
cd frontend
npm run dev

```

*Dashboard runs at: http://localhost:5173*

---

### 📂 Project Structure

```text
alpha-mechanism/
├── backend/
│   ├── data/input_papers/   # PDF Storage
│   ├── src/
│   │   ├── parser/          # VLM & Code Generation Logic
│   │   ├── strategies/      # AI-Generated Python Strategies
│   │   ├── backtester/      # Vectorized Execution Engine
│   │   └── rl_agent/        # PPO Learning Modules
│   ├── main.py              # FastAPI Entry Point
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/      # React UI Components
    │   └── App.jsx          # Dashboard Logic
    └── package.json

```

---

### 🔮 Roadmap

* [ ] **Live Trading:** Integration with Binance/Alpaca APIs.
* [ ] **Advanced Fairness:** Implementing "Regret Minimization" constraints for capital allocation.
* [ ] **Paper Trading Mode:** Real-time forward testing of extracted strategies.

### 📜 License

MIT License. Free for educational and research use.


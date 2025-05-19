# 💹 Real-Time Cryptocurrency Trade Simulator

This project is a high-performance cryptocurrency trading simulator that connects to OKX WebSocket live orderbook data. It estimates transaction costs and market impact using regression models and visualizes real-time analytics in a user-friendly Streamlit dashboard.

---

## 📦 Features

- 📈 Live L2 orderbook integration via WebSockets
- 🧠 Real-time regression-based modeling of slippage and maker/taker classification
- 💡 Interactive UI for strategy simulation
- ⚙️ Performance-aware design using async and efficient data structures
- 📊 Optional benchmarking and latency profiling

---

## 📘 Detailed Documentation

### 1. ✅ Model Selection and Parameters

#### a. Slippage Estimation (Transaction Cost Impact)
- **Model Used:** `LinearRegression` (`sklearn.linear_model`)
- **Why:** Simple, interpretable, effective for modeling linear relation between order size and slippage.
- **Input:** Order size (USD)  
- **Output:** Predicted slippage (%)  
- **Assumption:** Slippage scales linearly with order size in liquid markets.

#### b. Maker/Taker Classification
- **Model Used:** `LogisticRegression` (`sklearn.linear_model`)
- **Why:** Suitable for binary classification with linear boundaries.
- **Inputs:** Orderbook-derived features (e.g., spread, depth, imbalance)
- **Output:** Probability of fill as Maker (vs. Taker)

---

### 2. ✅ Regression Techniques Chosen

#### 🔸 Linear Regression (Slippage)
- **Formula:**  
  `Slippage = β₀ + β₁ × Order Size`
- **Pros:**  
  - Fast, low-complexity  
  - No hyperparameter tuning required  
- **Cons:**  
  - Assumes linearity; may underperform in highly volatile markets

#### 🔸 Logistic Regression (Maker/Taker Classification)
- **Formula:**  
  `P(Maker) = 1 / (1 + exp(-(β₀ + β₁x₁ + ... + βₙxₙ)))`
- **Pros:**  
  - Fast, interpretable  
  - Ideal for real-time binary classification  
- **Cons:**  
  - May underfit if decision boundary is nonlinear

---

### 3. ✅ Market Impact Calculation Methodology

Market impact is calculated using the slippage model:

```python
impact = slippage_model.predict([[order_size]])[0]
```

---

## ✅ Performance Optimization Approaches

### ⚙️ Live Data Ingestion
**Tools:** `websockets`, `asyncio`  
- Non-blocking, event-driven L2 stream ingestion from OKX  
- Runs under an asyncio event loop  

**Impact:**  
- Low-latency updates  
- Minimal CPU usage and high throughput  

---

### 🧠 Efficient Model Inference
**Models:** `LinearRegression`, `LogisticRegression`  
- Preloaded into memory at app start  
- Inference time < **1ms** (`timeit` verified)  

**Impact:**  
- Instant simulation  
- No noticeable lag on prediction  

---

### 🖥️ Frontend Optimization (Streamlit)
**Optimizations:**  
- UI updates only on input/data change  
- Use of `@st.cache_data` and `@st.cache_resource`  
- Partial UI redraws for fast metric refresh  

**Impact:**  
- Smooth user interaction  
- Efficient use of resources  

---

### 🧪 Backend Enhancements
**Concurrency:**  
- Async background threads or tasks for WebSocket  
- `Queue` or `asyncio.Queue` used to decouple ingestion/render  

**Profiling Tools:**  
- `psutil`, `timeit`, `cProfile`, `line_profiler`  

**Impact:**  
- Non-blocking, scalable backend  
- Bottlenecks identified and resolved efficiently

### 📤 How to Deploy and Use

Follow these steps to deploy and run your app:

1.⁠ ⁠Go to [Hugging Face Spaces](https://huggingface.co/spaces)

2.⁠ ⁠Open your Space (click on its name)

3.⁠ ⁠Make sure the following files are uploaded:
   - ⁠ app.py ⁠⁠
   - ⁠ requirements.txt ⁠

4.⁠ ⁠After uploading:
   - The app will automatically *build and launch*
   - In a few seconds, you'll see the app running inline

#### 🚀 Live Demo Link https://huggingface.co/spaces/Anubhav1516/trade


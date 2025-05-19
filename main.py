import streamlit as st
import asyncio
import websockets
import json
import numpy as np
import pandas as pd
import time
import psutil
from datetime import datetime
from collections import deque
from sklearn.linear_model import LinearRegression, LogisticRegression

# Initialize models
slippage_model = LinearRegression()
maker_model = LogisticRegression()

# Mock training data
X_train = np.array([[50], [100], [200], [300], [400]])
y_slippage = np.array([0.1, 0.2, 0.3, 0.45, 0.6])
y_maker_prob = np.array([1, 1, 0, 0, 0])
slippage_model.fit(X_train, y_slippage)
maker_model.fit(X_train, y_maker_prob)

# Set Streamlit UI
st.set_page_config(layout="wide")
st.title("💹 Real-Time Trade Simulator (OKX Orderbook)")

col1, col2 = st.columns(2)

with col1:
    asset = st.selectbox("Select Asset", ["BTC-USDT-SWAP"])
    quantity_usd = st.number_input("Order Value (USD)", value=100.0)
    volatility = st.slider("Market Volatility (0.0 to 1.0)", 0.0, 1.0, 0.3)
    fee_tier = st.selectbox("Fee Tier", ["Taker (0.10%)", "Maker (0.02%)"])

with col2:
    output_placeholder = st.empty()

# Performance log
log_buffer = deque(maxlen=500)
download_button_counter = 0

# Define WebSocket handler
async def process_orderbook():
    global download_button_counter
    uri = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

    retry_attempts = 5
    retry_delay = 5  # seconds

    for attempt in range(retry_attempts):
        try:
            async with websockets.connect(uri, ping_interval=None) as websocket:
                while True:
                    try:
                        start_time = time.time()
                        process = psutil.Process()

                        await websocket.ping()
                        msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                        data = json.loads(msg)

                        asks = sorted([[float(p), float(q)] for p, q in data["asks"]])
                        bids = sorted([[float(p), float(q)] for p, q in data["bids"]], reverse=True)
                        mid_price = (bids[0][0] + asks[0][0]) / 2

                        # Simulate VWAP
                        qty_remaining = quantity_usd / mid_price
                        vwap_price, total_qty = 0, 0
                        for price, qty in asks:
                            trade_qty = min(qty_remaining, qty)
                            vwap_price += trade_qty * price
                            total_qty += trade_qty
                            qty_remaining -= trade_qty
                            if qty_remaining <= 0:
                                break
                        vwap_price = vwap_price / total_qty if total_qty > 0 else mid_price

                        order_feature = np.array([[quantity_usd]])
                        slippage_pct = float(slippage_model.predict(order_feature)[0])
                        fee = 0.001 * quantity_usd if "Taker" in fee_tier else 0.0002 * quantity_usd
                        impact = volatility * quantity_usd / 1_000_000
                        maker_prob = float(maker_model.predict_proba(order_feature)[0][1]) * 100
                        net_cost = (slippage_pct * quantity_usd) + impact + fee

                        latency = (time.time() - start_time) * 1000  # ms
                        cpu = process.cpu_percent(interval=None)
                        mem = process.memory_info().rss / (1024 ** 2)  # MB

                        # Append performance log
                        log_buffer.append({
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                            "mid_price": mid_price,
                            "vwap": vwap_price,
                            "slippage_pct": slippage_pct,
                            "fee": fee,
                            "impact": impact,
                            "maker_prob": maker_prob,
                            "net_cost": net_cost,
                            "latency_ms": latency,
                            "cpu_pct": cpu,
                            "memory_mb": mem
                        })

                        # UI update throttling
                        if len(log_buffer) % 5 == 0:
                            with output_placeholder.container():
                                st.subheader("📈 Simulation Output (Live)")
                                st.metric("Mid Price", f"${mid_price:,.2f}")
                                st.metric("VWAP Price", f"${vwap_price:,.2f}")
                                st.metric("Expected Slippage", f"{slippage_pct * 100:.2f}%")
                                st.metric("Estimated Fee", f"${fee:.2f}")
                                st.metric("Market Impact", f"${impact:.2f}")
                                st.metric("Maker Probability", f"{maker_prob:.2f}%")
                                st.metric("Net Cost", f"${net_cost:.2f}")
                                st.metric("Latency", f"{latency:.2f} ms")
                                st.metric("CPU (%)", f"{cpu:.2f}")
                                st.metric("Memory (MB)", f"{mem:.2f}")

                                with st.expander("📉 Performance Log & Export"):
                                    df = pd.DataFrame(list(log_buffer))
                                    st.subheader("Last 10 Entries")
                                    st.dataframe(df.tail(10))

                                    # Zig-zag chart
                                    zigzag_df = pd.DataFrame({
                                        "timestamp": df["timestamp"].repeat(2).reset_index(drop=True),
                                        "net_cost": np.tile(df["net_cost"].values, 2)
                                    })
                                    zigzag_df["timestamp"][1::2] = pd.NaT
                                    st.line_chart(zigzag_df.set_index("timestamp")[["net_cost"]])

                                    st.markdown("#### Export Simulation Log:")
                                    download_button_counter += 1
                                    unique_key = f"download_button_{download_button_counter}"
                                    csv = df.to_csv(index=False).encode("utf-8")
                                    st.download_button("📥 Download CSV Log", csv, "trade_log.csv", "text/csv", key=unique_key)

                    except asyncio.TimeoutError:
                        st.warning("WebSocket timeout. Retrying...")
                        await asyncio.sleep(1)
                    except Exception as e:
                        st.warning(f"Runtime error: {e}")
                        await asyncio.sleep(1)

        except websockets.ConnectionClosedError as e:
            st.warning(f"Connection lost: {e}. Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except Exception as e:
            st.warning(f"Connection error: {e}. Retrying in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)

# Async wrapper
async def start_stream():
    await process_orderbook()

# Launch Streamlit-safe event loop
def run_stream():
    asyncio.run(start_stream())

# Run the app
run_stream()

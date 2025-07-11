import streamlit as st
from collections import Counter, deque
import websocket
import threading
import json

st.set_page_config(page_title="V10 Digit Match Predictor", layout="centered")
st.title("🔢 V10 Digit Match Predictor (Live Data)")

st.write("Live tick data from Volatility 10 Index will be streamed here. We'll predict the most likely Digit Match based on recent activity.")

# Use deque for efficient fixed-length tick history
tick_list = deque(maxlen=10)
predicted_digit = None

# WebSocket connection setup
class DerivWebSocket:
    def __init__(self):
        self.ws = websocket.WebSocketApp(
            "wss://ws.deriv.com/websockets/v3",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )

    def on_message(self, ws, message):
        global predicted_digit
        try:
            data = json.loads(message)
            if "tick" in data:
                tick = data["tick"]["quote"]
                tick_list.append(tick)
                last_digits = [int(str(t)[-1]) for t in tick_list]
                freq = Counter(last_digits)
                predicted_digit = freq.most_common(1)[0][0]
        except Exception as e:
            print(f"Error parsing tick data: {e}")

    def on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def on_close(self, ws):
        print("WebSocket connection closed.")

    def on_open(self, ws):
        ws.send(json.dumps({
            "ticks": "R_10",
            "subscribe": 1
        }))

    def run(self):
        self.ws.run_forever()

# Run WebSocket in background
if 'ws_thread_started' not in st.session_state:
    threading.Thread(target=DerivWebSocket().run, daemon=True).start()
    st.session_state['ws_thread_started'] = True

# Display predictions
if tick_list:
    st.subheader("📊 Last 10 Ticks")
    st.write(list(tick_list))

    if predicted_digit is not None:
        st.success(f"🎯 Predicted Digit Match: **{predicted_digit}**")
else:
    st.info("Waiting for live tick data from Deriv...")

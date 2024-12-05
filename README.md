# A Telegram bot that will send you a message when NVDA price reach Bollinger Bands' (BOLL) upper, middle (20 period SMA) and lower bounds.
## How to Use?
1. Create a Telegram Bot and a Channel for it to send messages.
2. Fill in your bot's token and channel id into TELEGRAM_BOT_TOKEN="" and CHAT_ID=""
3. Run it!
4. You can change another stock and adjust the scale of a candlestick chart at
```python
data = yf.download('NVDA', period='1mo', interval='1d')
```

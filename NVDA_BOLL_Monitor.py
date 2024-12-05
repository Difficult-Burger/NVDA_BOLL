import yfinance as yf
import pandas as pd
import schedule
import time
import telegram.ext
import asyncio
from telegram.error import TelegramError

# Telegram 配置
TELEGRAM_BOT_TOKEN = ""
CHAT_ID = ""

# 创建新的事件循环
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_message(message):
    try:
        async with telegram.Bot(token=TELEGRAM_BOT_TOKEN) as bot:
            await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"发送Telegram消息失败: {e}")

def send_message(message):
    try:
        loop.run_until_complete(send_telegram_message(message))
    except Exception as e:
        print(f"消息发送错误: {e}")

def fetch_nvda_data():
    """获取 NVDA 日K数据并计算布林带"""
    # 获取最近一个月的日K数据
    data = yf.download('NVDA', period='1mo', interval='1d')
    print("\n获取到的NVDA日K数据：")
    print(data.tail())  # 显示最新的几天数据
    
    # 计算20日布林带
    sma = data['Close'].rolling(window=20).mean()
    std = data['Close'].rolling(window=20).std()
    
    # 创建新的DataFrame来存储结果
    result = pd.DataFrame()
    result['Close'] = data['Close']
    result['SMA'] = sma
    result['Upper'] = sma + (2 * std)
    result['Lower'] = sma - (2 * std)
    
    # 只返回最新的数据
    return result.tail(1)

def monitor_nvda():
    """监控 NVDA 股价与布林带"""
    try:
        data = fetch_nvda_data()
        print(data)
        if data.empty or len(data) < 1:
            print("数据不足，稍后重试。")
            return

        # 获取最新的价格和布林带值（使用.iloc来避免多层索引问题）
        latest_data = data.iloc[-1]
        price = float(latest_data['Close'])
        upper = float(latest_data['Upper'])
        lower = float(latest_data['Lower'])
        middle = float(latest_data['SMA'])
        
        # 设置误差范围
        ERROR_MARGIN = 2.0
        MIDDLE_ERROR_MARGIN = 0.5  # 中轨使用更小的误差范围

        # 检查是否触及布林带
        message = None
        if price >= (upper - ERROR_MARGIN):
            message = f"NVDA 股价 ({price:.2f}) 接近或触及布林线上轨 ({upper:.2f})"
        elif price <= (lower + ERROR_MARGIN):
            message = f"NVDA 股价 ({price:.2f}) 接近或触及布林线下轨 ({lower:.2f})"
        elif abs(price - middle) <= MIDDLE_ERROR_MARGIN:
            message = f"NVDA 股价 ({price:.2f}) 接近或触及布林线中轨 ({middle:.2f})"
        
        if message:
            print(message)
            send_message(message)
        else:
            status = f"当前价格：{price:.2f}，上轨：{upper:.2f}，中轨：{middle:.2f}，下轨：{lower:.2f}"
            print(status)
            #send_message(status)
    except Exception as e:
        print(f"监控过程出错: {e}")

# 定时任务
schedule.every(10).seconds.do(monitor_nvda)

print("监控已启动，按 Ctrl+C 停止。")
try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n程序已停止")
finally:
    if loop.is_running():
        loop.close()

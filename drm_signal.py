import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("8804602899:AAHhPxCDmJax8v4v3wl1yTTIwtLjEQrclyY")
CHAT_ID = os.environ.get("1780797125")
PAIR = "GC=F"
INTERVAL = "15m"

def calculate_drm(df):
    df = df.copy()
    df['PBL'] = (df['High'].rolling(20).max() + df['Low'].rolling(20).min()) / 2
    df['TR'] = np.maximum(df['High'] - df['Low'],
                          np.maximum(abs(df['High'] - df['Close'].shift(1)),
                                     abs(df['Low'] - df['Close'].shift(1))))
    df['ATR'] = df['TR'].rolling(14).mean()
    df['MO'] = (df['Close'] - df['Close'].shift(5)) / df['ATR'] * 100
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR_ADX'] = df[['H-L','H-PC','L-PC']].max(axis=1)
    df['DM_plus'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']),
                              np.maximum(df['High'] - df['High'].shift(1), 0), 0)
    df['DM_minus'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)),
                               np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
    df['ATR_ADX'] = df['TR_ADX'].rolling(14).mean()
    df['DM_plus_smooth'] = df['DM_plus'].rolling(14).mean()
    df['DM_minus_smooth'] = df['DM_minus'].rolling(14).mean()
    df['DI_plus'] = 100 * (df['DM_plus_smooth'] / df['ATR_ADX'])
    df['DI_minus'] = 100 * (df['DM_minus_smooth'] / df['ATR_ADX'])
    df['DX'] = 100 * abs(df['DI_plus'] - df['DI_minus']) / (df['DI_plus'] + df['DI_minus'])
    df['ADX'] = df['DX'].rolling(14).mean()
    mo_threshold = 25
    df['Long'] = ((df['Close'] > df['PBL']) & (df['MO'] > mo_threshold) &
                  (df['MO'] > df['MO'].shift(1)) &
                  ((df['ADX'] > 20) | ((df['Close'] - df['PBL']) > (0.5 * df['ATR']))))
    df['Short'] = ((df['Close'] < df['PBL']) & (df['MO'] < -mo_threshold) &
                   (df['MO'] < df['MO'].shift(1)) &
                   ((df['ADX'] > 20) | ((df['PBL'] - df['Close']) > (0.5 * df['ATR']))))
    return df

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
    except:
        pass

def main():
    try:
        ticker = yf.Ticker(PAIR)
        data = ticker.history(period="5d", interval=INTERVAL)
        if data.empty:
            return
        data.index = data.index.tz_localize(None)
        df = calculate_drm(data)
        latest = df.iloc[-1]
        candle_time = df.index[-1]
        if latest['Long']:
            msg = (f"🟢 LONG XAUUSD ({INTERVAL})\nHarga: {latest['Close']:.2f}\nMO: {latest['MO']:.1f} | ADX: {latest['ADX']:.1f}\nSL: {latest['Close'] - 2*latest['ATR']:.2f}\nTP: {latest['Close'] + 2.5*latest['ATR']:.2f}\nWaktu: {candle_time}")
            send_telegram(msg)
        elif latest['Short']:
            msg = (f"🔴 SHORT XAUUSD ({INTERVAL})\nHarga: {latest['Close']:.2f}\nMO: {latest['MO']:.1f} | ADX: {latest['ADX']:.1f}\nSL: {latest['Close'] + 2*latest['ATR']:.2f}\nTP: {latest['Close'] - 2.5*latest['ATR']:.2f}\nWaktu: {candle_time}")
            send_telegram(msg)
    except Exception as e:
        send_telegram(f"⚠️ Error: {str(e)}")

if __name__ == "__main__":
    main()

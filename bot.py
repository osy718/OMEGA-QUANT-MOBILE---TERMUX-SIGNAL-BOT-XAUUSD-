"""
OMEGA QUANT MOBILE - TERMUX SIGNAL BOT
========================================
5M, 15M, 1H XAUUSD Signals → Telegram
GitHub: github.com/YOUR_USER/omega-quant-mobile
"""

import time, requests, json, numpy as np
from datetime import datetime

# ═══════════════ CONFIG ═══════════════
TELEGRAM_TOKEN = '8419453226:AAEDUCi-gj5t0TFIDfr7xXXwZ2UDcHpfOjM'
CHAT_ID = '1002152636'
SYMBOL = "PAXGUSDT"
MIN_SCORE = 60
# ═══════════════════════════════════════

def get_price(): 
    try: return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={SYMBOL}", timeout=5).json()['price'])
    except: return None

def get_klines(interval, limit=50):
    try:
        d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={interval}&limit={limit}", timeout=5).json()
        return {
            'c': np.array([float(x[4]) for x in d]),
            'h': np.array([float(x[2]) for x in d]),
            'l': np.array([float(x[3]) for x in d]),
            'v': np.array([float(x[5]) for x in d])
        }
    except: return None

def calculate_rsi(c, p=14):
    d = np.diff(c[-p-1:])
    g = np.mean(np.where(d>0, d, 0))
    l = np.mean(np.where(d<0, -d, 0))
    return 100 - (100/(1+g/l)) if l > 0 else 100

def calculate_ema(d, p):
    a = 2/(p+1); e = d[0]
    for x in d[1:]: e = a*x + (1-a)*e
    return e

def detect_signal(tf_name, tf_code):
    d = get_klines(tf_code)
    if not d or len(d['c']) < 20: return None
    
    c, h, l, v = d['c'], d['h'], d['l'], d['v']
    cur = c[-1]
    score = 50
    direction = None
    reasons = []
    
    # Momentum
    m = (np.mean(c[-3:]) - np.mean(c[-8:])) / np.mean(c[-8:]) * 100
    if m > 0.05: score += 20; direction = 'BUY'; reasons.append(f"M+{m:.2f}%")
    elif m < -0.05: score += 20; direction = 'SELL'; reasons.append(f"M{m:.2f}%")
    
    # RSI
    rs = calculate_rsi(c)
    if rs < 35: score += 15; direction = direction or 'BUY'; reasons.append(f"RSI{int(rs)}")
    elif rs > 65: score += 15; direction = direction or 'SELL'; reasons.append(f"RSI{int(rs)}")
    
    # EMA Cross
    if calculate_ema(c[-10:], 5) > calculate_ema(c[-20:], 10):
        score += 10; direction = direction or 'BUY'; reasons.append("EMA↑")
    else:
        score += 10; direction = direction or 'SELL'; reasons.append("EMA↓")
    
    # Support/Resistance
    rh, rl = np.max(h[-10:]), np.min(l[-10:])
    rng = rh - rl
    if cur <= rl + rng*0.3: score += 10; direction = direction or 'BUY'; reasons.append("NearLow")
    elif cur >= rh - rng*0.3: score += 10; direction = direction or 'SELL'; reasons.append("NearHigh")
    
    # Consecutive bars
    up = sum(1 for i in range(-5, 0) if c[i] > c[i-1])
    dn = sum(1 for i in range(-5, 0) if c[i] < c[i-1])
    if up >= 3: score += 10; direction = direction or 'BUY'; reasons.append(f"{up}↑bars")
    elif dn >= 3: score += 10; direction = direction or 'SELL'; reasons.append(f"{dn}↓bars")
    
    # Volume
    if np.mean(v[-10:]) > 0 and v[-1] > np.mean(v[-10:])*1.3 and direction:
        score += 5; reasons.append("Vol↑")
    
    score = min(score, 98)
    atr = np.mean(h[-10:] - l[-10:])
    
    if direction == 'BUY':
        entry = cur; sl = round(entry - atr*1.5, 2); tp = round(entry + atr*2.0, 2)
    elif direction == 'SELL':
        entry = cur; sl = round(entry + atr*1.5, 2); tp = round(entry - atr*2.0, 2)
    else:
        entry = sl = tp = 0
    
    return {
        'tf': tf_name, 'dir': direction, 'score': int(score),
        'entry': round(cur, 2), 'sl': sl, 'tp': tp,
        'rsi': int(rs), 'reasons': ' | '.join(reasons),
        'time': datetime.now()
    }

def send_telegram(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={'chat_id': CHAT_ID, 'text': msg, 'parse_mode': 'HTML'},
            timeout=5
        )
    except: pass

def format_signal(s):
    if not s or not s['dir']: return None
    e = "🟢" if s['dir'] == 'BUY' else "🔴"
    st = "STRONG" if s['score'] >= 80 else "MODERATE" if s['score'] >= 65 else "WEAK"
    
    return f"""{e} <b>{s['tf']} {s['dir']} SIGNAL</b> {e}
━━━━━━━━━━━━━━━━━━
📊 <b>Score:</b> {s['score']}% ({st})
💰 <b>Entry:</b> ${s['entry']}
🛑 <b>SL:</b> ${s['sl']}
🎯 <b>TP:</b> ${s['tp']}
📈 <b>RSI:</b> {s['rsi']}
📝 <b>{s['reasons']}</b>
🕐 <b>{s['time'].strftime('%H:%M:%S')}</b>
━━━━━━━━━━━━━━━━━━
⚡ OMEGA QUANT MOBILE"""

# ═══════════════ MAIN ═══════════════
def main():
    print("=" * 50)
    print("  OMEGA QUANT MOBILE")
    print("  5M | 15M | 1H → Telegram")
    print("=" * 50)
    
    p = get_price()
    if p:
        print(f"\n✅ XAUUSD: ${p:.2f}")
        send_telegram(f"🟢 <b>Mobile Bot Started</b>\nXAUUSD: ${p:.2f}\nScanning 5M/15M/1H...")
    else:
        print("❌ No internet connection")
        return
    
    last_sig = {'5m': None, '15m': None, '1h': None}
    last_time = {'5m': 0, '15m': 0, '1h': 0}
    cooldown = {'5m': 120, '15m': 300, '1h': 600}
    count = 0
    
    print("\n🔍 Scanning... Ctrl+C to stop\n")
    
    try:
        while True:
            count += 1
            now = time.time()
            p = get_price()
            print(f"\r⏳ [{count}] XAUUSD: ${p:.2f if p else '--'}", end="")
            
            for name, code, key in [('5M','5m','5m'),('15M','15m','15m'),('1H','1h','1h')]:
                if now - last_time[key] < cooldown[key]:
                    continue
                
                s = detect_signal(name, code)
                if s and s['dir'] and s['score'] >= MIN_SCORE:
                    prev = last_sig[key]
                    if prev and prev['dir'] == s['dir'] and abs(prev['score'] - s['score']) < 5:
                        continue
                    
                    last_sig[key] = s
                    last_time[key] = now
                    
                    msg = format_signal(s)
                    if msg:
                        print(f"\n📤 Sending {name} signal...")
                        send_telegram(msg)
                        print(f"✅ {name} sent!")
            
            time.sleep(15)
            
    except KeyboardInterrupt:
        print("\n\n⏹ Stopped")
        send_telegram("⏹ <b>Mobile Bot Stopped</b>")

if __name__ == "__main__":
    main()

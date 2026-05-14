#!/usr/bin/env python3
"""
祖马耳朵模块 (EAR) v8 - 主程序
录音 → 小米mimo-v2-omni识别 → mimo-v2.5-pro大模型回复 → TTS播放

用法：
  python3 ~/openzuma/ear/main.py          # 前台运行
  python3 ~/openzuma/ear/main.py --bg     # 后台运行
"""
import subprocess
import time
import os
import struct
import wave
import signal
import sys
import base64
import json
import urllib.request

# 加载配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import *

# ── 对话历史 ─────────────────────
chat_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def cleanup(signum=None, frame=None):
    subprocess.run(["termux-microphone-record", "-q"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if signum is not None:
        print("\n👋 再见！")
        sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def m4a_to_wav(m4a_path):
    wav = os.path.join(TMP_DIR, f"voice_{int(time.time()*1000)}.wav")
    subprocess.run(["ffmpeg", "-y", "-i", m4a_path,
                    "-ar", str(SAMPLE_RATE), "-ac", "1",
                    "-acodec", "pcm_s16le", wav],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav if os.path.exists(wav) else None

def get_energy(wav_path):
    try:
        with wave.open(wav_path, 'rb') as wf:
            n = wf.getnframes()
            if n < 10:
                return 0
            data = wf.readframes(n)
            samples = struct.unpack(f'<{n}h', data)
            return (sum(s*s for s in samples) / n) ** 0.5
    except:
        return 0

def record_seconds(sec):
    m4a = os.path.join(TMP_DIR, f"voice_{int(time.time()*1000)}.m4a")
    subprocess.run(["termux-microphone-record", "-f", m4a, "-l", str(sec)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(sec + 0.5)
    return m4a if os.path.exists(m4a) and os.path.getsize(m4a) > 500 else None

def recognize_audio(wav_path):
    """用小米 mimo-v2-omni 识别音频"""
    print("  🧠 识别中...", end="", flush=True)
    try:
        with open(wav_path, 'rb') as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        req_data = json.dumps({
            "model": STT_MODEL,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "请识别这段音频中的语音内容，只输出识别到的文字，不要添加任何解释"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}}
                ]
            }]
        }).encode()

        req = urllib.request.Request(
            f"{API_BASE}/chat/completions",
            data=req_data,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        text = result['choices'][0]['message']['content'].strip()
        print(f" ✓")
        return text if text and len(text) > 1 else None
    except Exception as e:
        print(f" ✗ {e}")
        return None

def chat_with_llm(user_text):
    """用大模型生成回复"""
    print("  💭 思考中...", end="", flush=True)
    try:
        chat_history.append({"role": "user", "content": user_text})
        messages = chat_history[:1] + chat_history[-MAX_HISTORY:]

        req_data = json.dumps({
            "model": LLM_MODEL,
            "messages": messages,
            "max_tokens": LLM_MAX_TOKENS,
            "temperature": LLM_TEMPERATURE
        }).encode()

        req = urllib.request.Request(
            f"{API_BASE}/chat/completions",
            data=req_data,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())
        reply = result['choices'][0]['message']['content'].strip()

        chat_history.append({"role": "assistant", "content": reply})
        print(f" ✓")
        return reply
    except Exception as e:
        print(f" ✗ {e}")
        return "抱歉，我刚才没想好怎么说。"

def speak(text):
    subprocess.run(["termux-tts-speak", "-r", str(TTS_RATE), "-l", TTS_LANG, text],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def listen_once():
    """监听一次：检测到说话 → 录音 → 合并 → 返回m4a路径"""
    # 监听
    print("🎧 监听中...", end="", flush=True)
    detected = False
    while not detected:
        clip = record_seconds(MONITOR_SEC)
        if clip:
            wav = m4a_to_wav(clip)
            if wav:
                energy = get_energy(wav)
                os.remove(wav)
                if energy > ENERGY_THRESHOLD:
                    print(f" 听到! (能量:{energy:.0f})")
                    detected = True
            os.remove(clip)
        if not detected:
            time.sleep(0.1)

    # 录音
    print("🎤 说话中...", end="", flush=True)
    sys.stdout.flush()
    all_clips = []
    silence_start = None
    rec_start = time.time()

    while True:
        elapsed = time.time() - rec_start
        if elapsed >= MAX_RECORD:
            print(f" 最长录音")
            break

        clip = record_seconds(MONITOR_SEC)
        if clip:
            wav = m4a_to_wav(clip)
            if wav:
                energy = get_energy(wav)
                os.remove(wav)
                all_clips.append(clip)
                if energy < ENERGY_THRESHOLD:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= SILENCE_DURATION:
                        print(f" 说完 ({elapsed:.0f}秒)")
                        break
                else:
                    silence_start = None
                    sys.stdout.write(".")
                    sys.stdout.flush()

    if not all_clips:
        return None

    # 合并
    if len(all_clips) == 1:
        return all_clips[0]

    final_m4a = os.path.join(TMP_DIR, f"voice_final_{int(time.time())}.m4a")
    concat = os.path.join(TMP_DIR, f"voice_concat_{int(time.time())}.txt")
    with open(concat, 'w') as f:
        for c in all_clips:
            f.write(f"file '{c}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", concat, "-c", "copy", final_m4a],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(concat)
    for c in all_clips:
        if os.path.exists(c):
            os.remove(c)
    return final_m4a

def process_audio(m4a_path):
    """处理音频：转WAV → 识别 → 大模型回复 → TTS"""
    wav = m4a_to_wav(m4a_path)
    if not wav:
        print("  ❌ 转换失败")
        return

    text = recognize_audio(wav)

    # 清理
    for f in [m4a_path, wav]:
        if os.path.exists(f):
            os.remove(f)

    if not text:
        print("  ⚠️  未识别到\n")
        return

    # 过滤噪音
    if "没有语音" in text or "杂音" in text or "敲击" in text:
        print(f"  ⚠️  噪音，跳过\n")
        return

    print(f"  📝 你: {text}")

    # 大模型回复
    reply = chat_with_llm(text)
    print(f"  🤖 祖马: {reply}")
    speak(reply)
    print()
    print("─" * 40)

def main():
    print("╔═══════════════════════════════════════╗")
    print("║   🎙️  祖马耳朵模块 (EAR) v8          ║")
    print("║   语音识别 + 大模型回复                ║")
    print("╚═══════════════════════════════════════╝")
    print()
    print("💬 说话，祖马会用大模型回答你")
    print("   Ctrl+C 退出")
    print("─" * 40)
    sys.stdout.flush()

    while True:
        m4a = listen_once()
        if m4a:
            process_audio(m4a)

if __name__ == "__main__":
    main()

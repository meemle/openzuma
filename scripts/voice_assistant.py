#!/usr/bin/env python3
"""
祖马语音助手 v8 - 大模型回复
录音 → 小米mimo-v2-omni识别 → mimo-v2.5-pro大模型回复 → TTS播放
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

# ── 配置 ─────────────────────────
ENERGY_THRESHOLD = 80
SILENCE_DURATION = 2.0
MAX_RECORD = 15
MONITOR_SEC = 1
SAMPLE_RATE = 16000
# ─────────────────────────────────

TMP_DIR = "/data/data/com.termux/files/usr/tmp"

# 读取 API 配置
API_KEY = ""
API_BASE = ""
for line in open(os.path.expanduser("~/.openzuma/.env")).read().split("\n"):
    if line.startswith("XIAOMI_API_KEY="):
        API_KEY = line.split("=", 1)[1]
    if line.startswith("XIAOMI_BASE_URL="):
        API_BASE = line.split("=", 1)[1]

# 对话历史（保持上下文）
chat_history = [
    {"role": "system", "content": "你是祖马，一个智能语音助手。用户通过语音和你对话，你需要简洁、自然地回复。回答要简短（1-2句话），适合语音播放。不要用markdown格式，不要用emoji。"}
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
            "model": "mimo-v2-omni",
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

        # 保留最近10轮对话
        messages = chat_history[:1] + chat_history[-20:]

        req_data = json.dumps({
            "model": "mimo-v2.5-pro",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.7
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
    subprocess.run(["termux-tts-speak", "-r", "1.3", "-l", "zh", text],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    print("╔═══════════════════════════════════════╗")
    print("║   🎙️  祖马语音助手 v8 - 大模型回复     ║")
    print("╚═══════════════════════════════════════╝")
    print()
    print("💬 说话，祖马会用大模型回答你")
    print("   Ctrl+C 退出")
    print("─" * 40)
    sys.stdout.flush()

    while True:
        # ── 1. 监听 ──
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

        # ── 2. 录音 ──
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
            print("  ❌ 无录音\n")
            continue

        # ── 3. 合并音频 ──
        if len(all_clips) == 1:
            final_m4a = all_clips[0]
        else:
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

        # ── 4. 识别 ──
        final_wav = m4a_to_wav(final_m4a)
        if not final_wav:
            print("  ❌ 转换失败\n")
            continue

        text = recognize_audio(final_wav)

        for f in [final_m4a, final_wav]:
            if os.path.exists(f):
                os.remove(f)

        if not text:
            print("  ⚠️  未识别到\n")
            continue

        # 过滤噪音识别结果
        if "没有语音" in text or "杂音" in text or "敲击" in text:
            print(f"  ⚠️  噪音，跳过\n")
            continue

        print(f"  📝 你: {text}")

        # ── 5. 大模型回复 ──
        reply = chat_with_llm(text)
        print(f"  🤖 祖马: {reply}")
        speak(reply)
        print()
        print("─" * 40)

if __name__ == "__main__":
    main()

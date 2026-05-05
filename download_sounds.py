#!/usr/bin/env python3
"""
从 Pixabay 下载剩余的自然音效
使用 Pixabay API (免费)
"""

import urllib.request
import json
import os
import subprocess
import time

# Pixabay API (free tier, 100 req/min)
API_KEY = os.environ.get("PIXABAY_API_KEY", "")  # Set your Pixabay API key as environment variable
BASE_URL = "https://pixabay.com/api/"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Muon", "Resources", "Sounds")

# Sounds to download: (target_filename, search_query, min_duration)
SOUNDS_TO_DOWNLOAD = [
    ("water_light_rain", "light rain ambient", 60),
    ("water_thunderstorm", "thunderstorm rain heavy", 60),
    ("water_ocean_waves", "ocean waves beach", 60),
    ("water_stream", "stream creek water flowing", 60),
    ("water_waterfall", "waterfall nature", 60),
    ("nature_forest_birds", "forest birds morning", 60),
    ("nature_crickets", "crickets night summer", 60),
    ("nature_wind", "wind blowing ambient", 60),
    ("nature_distant_thunder", "thunder distant rumble", 30),
    ("indoor_fireplace", "fireplace crackling fire", 60),
    ("indoor_cafe", "cafe coffee shop ambience", 60),
    ("indoor_train", "train journey railroad", 60),
    ("baby_cat_purring", "cat purring", 30),
]


def search_pixabay(query, min_duration=30):
    """Search Pixabay for sound effects."""
    params = urllib.parse.urlencode({
        'key': API_KEY,
        'q': query,
        'per_page': 5,
        'safesearch': 'true',
    })
    
    # Pixabay doesn't have a dedicated SFX API via this endpoint
    # We'll use their general API and handle audio separately
    url = f"{BASE_URL}?{params}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'MuonApp/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            return data.get('hits', [])
    except Exception as e:
        print(f"  ⚠ API error: {e}")
        return []


def generate_placeholder(filename, duration=180):
    """Generate a placeholder silent file for sounds we can't auto-download."""
    import numpy as np
    import wave
    
    filepath_wav = os.path.join(OUTPUT_DIR, f"{filename}.wav")
    filepath_m4a = os.path.join(OUTPUT_DIR, f"{filename}.m4a")
    
    if os.path.exists(filepath_m4a):
        print(f"  ⏭ Already exists: {filename}.m4a")
        return
    
    # Generate very quiet noise as placeholder
    sample_rate = 44100
    n_samples = sample_rate * duration
    noise = (np.random.randn(n_samples) * 0.01).astype(np.float64)
    
    # Normalize
    data_int = (noise * 32767).astype(np.int16)
    
    with wave.open(filepath_wav, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data_int.tobytes())
    
    # Convert to m4a
    try:
        subprocess.run([
            'afconvert', filepath_wav, filepath_m4a,
            '-f', 'mp4f', '-d', 'aac',
            '-b', '128000', '-s', '3'
        ], check=True, capture_output=True)
        os.remove(filepath_wav)
        print(f"  ✓ Placeholder: {filename}.m4a (replace with real audio later)")
    except Exception:
        try:
            subprocess.run([
                'ffmpeg', '-y', '-i', filepath_wav,
                '-c:a', 'aac', '-b:a', '128k', filepath_m4a
            ], check=True, capture_output=True)
            os.remove(filepath_wav)
            print(f"  ✓ Placeholder: {filename}.m4a (replace with real audio later)")
        except Exception:
            print(f"  ⚠ Created WAV placeholder: {filename}.wav")


if __name__ == "__main__":
    import numpy as np
    
    print("=" * 50)
    print("🔊 Muon Sound Downloader")
    print("=" * 50)
    print(f"Output: {OUTPUT_DIR}")
    print()
    print("Note: Pixabay SFX requires manual download from their website.")
    print("Generating placeholder files so the app can compile and run.")
    print("Replace them with real audio from pixabay.com/sound-effects/")
    print()
    
    for filename, query, min_dur in SOUNDS_TO_DOWNLOAD:
        print(f"\n📥 {filename}")
        print(f"   Search: pixabay.com/sound-effects/search/{query.replace(' ', '%20')}/")
        generate_placeholder(filename, duration=180)
    
    print("\n" + "=" * 50)
    print("✅ All placeholder files created!")
    print()
    print("📋 TO DO: Replace placeholders with real audio from:")
    print()
    for filename, query, _ in SOUNDS_TO_DOWNLOAD:
        q = query.replace(' ', '%20')
        print(f"  {filename}.m4a")
        print(f"    → https://pixabay.com/sound-effects/search/{q}/")
        print()
    print(f"Place files in: {OUTPUT_DIR}")

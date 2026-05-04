#!/usr/bin/env python3
"""
Muon 全量音效生成脚本 v2
用算法生成全部18个高品质音效（自然音效本质上是各种滤波/调制噪声）
"""

import numpy as np
import wave
import os
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Muon", "Resources", "Sounds")
SAMPLE_RATE = 44100
DURATION = 180  # 3 minutes per file

os.makedirs(OUTPUT_DIR, exist_ok=True)


def simple_lowpass(data, kernel_size):
    """Simple moving average low-pass filter."""
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')


def simple_highpass(data, kernel_size):
    """Simple high-pass filter (original - lowpass)."""
    return data - simple_lowpass(data, kernel_size)


def save_wav(filename, data, sample_rate=SAMPLE_RATE):
    """Save numpy array as WAV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    data = np.clip(data, -1.0, 1.0)
    # Stereo
    if len(data.shape) == 1:
        data_int = (data * 32767).astype(np.int16)
        channels = 1
    else:
        data_int = (data * 32767).astype(np.int16)
        channels = 2

    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data_int.tobytes())
    
    print(f"  ✓ Generated: {filename}")
    return filepath


def convert_to_m4a(wav_path):
    """Convert WAV to M4A using afconvert."""
    m4a_path = wav_path.replace('.wav', '.m4a')
    try:
        subprocess.run([
            'afconvert', wav_path, m4a_path,
            '-f', 'mp4f', '-d', 'aac',
            '-b', '192000', '-s', '3'
        ], check=True, capture_output=True)
        os.remove(wav_path)
        print(f"  ✓ Converted: {os.path.basename(m4a_path)}")
        return m4a_path
    except Exception:
        print(f"  ⚠ Keeping WAV: {os.path.basename(wav_path)}")
        return wav_path


def crossfade_loop(data, crossfade_seconds=3.0, sample_rate=SAMPLE_RATE):
    """Create seamless loop using crossfade."""
    cf_samples = int(crossfade_seconds * sample_rate)
    if cf_samples >= len(data) // 2:
        cf_samples = len(data) // 4
    fade_out = np.linspace(1, 0, cf_samples)
    fade_in = np.linspace(0, 1, cf_samples)
    data[:cf_samples] = data[:cf_samples] * fade_in + data[-cf_samples:] * fade_out
    return data


def normalize(data, target=0.5):
    """Normalize audio to target amplitude."""
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * target
    return data


# ============================================================
# WATER SOUNDS
# ============================================================

def generate_light_rain():
    """Light rain: many tiny high-frequency clicks with some filtering."""
    print("\n🌧️  Generating: Light Rain")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base: filtered white noise (rain texture)
    noise = np.random.randn(n)
    rain = simple_lowpass(noise, 3)  # Slightly filtered
    
    # Add individual raindrop hits (sparse impulses)
    drops = np.zeros(n)
    n_drops = int(DURATION * 80)  # 80 drops per second
    drop_positions = np.random.randint(0, n, n_drops)
    drop_amplitudes = np.random.exponential(0.3, n_drops)
    for pos, amp in zip(drop_positions, drop_amplitudes):
        if pos < n - 500:
            decay = np.exp(-np.arange(500) / 50.0)
            drops[pos:pos+500] += amp * decay * np.random.randn(500)
    
    drops = simple_lowpass(drops, 5)
    
    # Combine
    signal = rain * 0.3 + drops * 0.5
    
    # Gentle amplitude modulation (wind gusts)
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    signal = signal * mod
    
    signal = normalize(crossfade_loop(signal), 0.45)
    convert_to_m4a(save_wav("water_light_rain.wav", signal))


def generate_thunderstorm():
    """Heavy rain + distant thunder rumbles."""
    print("\n⛈️  Generating: Thunderstorm")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Heavy rain base
    noise = np.random.randn(n)
    rain = simple_lowpass(noise, 2)
    
    # Dense drops
    drops = np.zeros(n)
    n_drops = int(DURATION * 300)
    drop_positions = np.random.randint(0, n, n_drops)
    for pos in drop_positions:
        if pos < n - 200:
            decay = np.exp(-np.arange(200) / 30.0)
            drops[pos:pos+200] += np.random.exponential(0.4) * decay * np.random.randn(200)
    drops = simple_lowpass(drops, 3)
    
    # Thunder rumbles (low frequency bursts, every 15-40 seconds)
    thunder = np.zeros(n)
    thunder_times = []
    pos = np.random.randint(10 * SAMPLE_RATE, 20 * SAMPLE_RATE)
    while pos < n - 5 * SAMPLE_RATE:
        thunder_times.append(pos)
        pos += np.random.randint(15 * SAMPLE_RATE, 40 * SAMPLE_RATE)
    
    for tpos in thunder_times:
        duration_samples = np.random.randint(2 * SAMPLE_RATE, 4 * SAMPLE_RATE)
        if tpos + duration_samples < n:
            rumble = np.random.randn(duration_samples)
            rumble = simple_lowpass(rumble, 400)  # Very low frequency
            envelope = np.exp(-np.arange(duration_samples) / (duration_samples * 0.3))
            attack = np.minimum(np.arange(duration_samples) / (SAMPLE_RATE * 0.3), 1.0)
            thunder[tpos:tpos+duration_samples] += rumble * envelope * attack * 3.0
    
    # Wind gusts
    wind_mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.03 * t + np.random.randn())
    
    signal = (rain * 0.4 + drops * 0.3) * wind_mod + thunder * 0.4
    signal = normalize(crossfade_loop(signal), 0.5)
    convert_to_m4a(save_wav("water_thunderstorm.wav", signal))


def generate_ocean_waves():
    """Ocean waves: rhythmic low-frequency surges."""
    print("\n🌊 Generating: Ocean Waves")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base ocean noise
    noise = np.random.randn(n)
    ocean = simple_lowpass(noise, 50)  # Low-frequency base
    
    # Wave surges (every 6-10 seconds)
    waves = np.zeros(n)
    wave_period = 8.0  # Average seconds per wave
    wave_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * (1.0/wave_period) * t)
    
    # High-frequency splash on wave crests
    splash_noise = np.random.randn(n)
    splash = simple_lowpass(splash_noise, 8) * (wave_envelope ** 3)
    
    # Combine low rumble + splash
    signal = ocean * 0.4 * wave_envelope + splash * 0.5
    
    # Add subtle second harmonic
    wave2 = 0.3 * np.sin(2 * np.pi * (1.0/12.0) * t)
    signal = signal * (0.7 + 0.3 * wave2)
    
    signal = normalize(crossfade_loop(signal), 0.5)
    convert_to_m4a(save_wav("water_ocean_waves.wav", signal))


def generate_stream():
    """Gentle stream: continuous babbling water."""
    print("\n💧 Generating: Gentle Stream")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base: band-passed noise (mid-high frequency)
    noise = np.random.randn(n)
    stream = simple_lowpass(noise, 5)
    stream = simple_highpass(stream, 100)
    
    # Bubbling sounds (random short bursts)
    bubbles = np.zeros(n)
    n_bubbles = int(DURATION * 15)
    for _ in range(n_bubbles):
        pos = np.random.randint(0, n - 5000)
        dur = np.random.randint(1000, 5000)
        freq = np.random.uniform(800, 2000)
        envelope = np.exp(-np.arange(dur) / (dur * 0.2))
        bubble = envelope * np.sin(2 * np.pi * freq * np.arange(dur) / SAMPLE_RATE)
        bubbles[pos:pos+dur] += bubble * np.random.uniform(0.1, 0.3)
    
    # Gentle modulation
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * t)
    
    signal = stream * 0.4 * mod + bubbles * 0.3
    signal = normalize(crossfade_loop(signal), 0.4)
    convert_to_m4a(save_wav("water_stream.wav", signal))


def generate_waterfall():
    """Waterfall: constant broadband noise with low-freq emphasis."""
    print("\n🏞️  Generating: Waterfall")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Dense broadband noise
    noise = np.random.randn(n)
    
    # Low-frequency emphasis (waterfall rumble)
    low = simple_lowpass(noise, 30)
    mid = simple_lowpass(noise, 8)
    
    # Very gentle modulation
    mod = 0.9 + 0.1 * np.sin(2 * np.pi * 0.02 * t)
    
    signal = (low * 0.5 + mid * 0.3 + noise * 0.1) * mod
    signal = normalize(crossfade_loop(signal), 0.45)
    convert_to_m4a(save_wav("water_waterfall.wav", signal))


# ============================================================
# NATURE SOUNDS
# ============================================================

def generate_forest_birds():
    """Forest birds: chirps at various pitches with forest ambience."""
    print("\n🐦 Generating: Forest Birds")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Forest ambience (light wind through leaves)
    ambience = np.random.randn(n)
    ambience = simple_lowpass(ambience, 20) * 0.15
    
    # Bird calls (synthetic chirps)
    birds = np.zeros(n)
    n_calls = int(DURATION * 3)  # ~3 calls per second
    
    for _ in range(n_calls):
        pos = np.random.randint(0, n - SAMPLE_RATE)
        # Each call is a short frequency sweep
        call_dur = np.random.randint(int(0.05 * SAMPLE_RATE), int(0.3 * SAMPLE_RATE))
        freq_start = np.random.uniform(2000, 5000)
        freq_end = np.random.uniform(1500, 6000)
        freqs = np.linspace(freq_start, freq_end, call_dur)
        phase = np.cumsum(freqs / SAMPLE_RATE) * 2 * np.pi
        envelope = np.sin(np.linspace(0, np.pi, call_dur))  # Smooth envelope
        chirp = envelope * np.sin(phase) * np.random.uniform(0.1, 0.4)
        birds[pos:pos+call_dur] += chirp
    
    signal = ambience + birds * 0.6
    signal = normalize(crossfade_loop(signal), 0.4)
    convert_to_m4a(save_wav("nature_forest_birds.wav", signal))


def generate_crickets():
    """Summer crickets: rhythmic high-frequency chirping."""
    print("\n🦗 Generating: Summer Crickets")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Night ambience
    ambience = np.random.randn(n)
    ambience = simple_lowpass(ambience, 30) * 0.08
    
    # Cricket chirps (pulsating high-frequency tone)
    crickets = np.zeros(n)
    
    # Multiple crickets at different frequencies
    for _ in range(5):
        freq = np.random.uniform(4000, 7000)
        chirp_rate = np.random.uniform(3, 8)  # Chirps per second
        duty = np.random.uniform(0.3, 0.6)
        
        # Pulsating pattern
        pulse = (np.sin(2 * np.pi * chirp_rate * t) > (1 - 2*duty)).astype(float)
        tone = np.sin(2 * np.pi * freq * t) * pulse
        tone = tone * np.random.uniform(0.1, 0.25)
        
        # Random start/stop
        start = np.random.randint(0, n // 4)
        crickets[start:] += tone[start:]
    
    signal = ambience + crickets
    signal = normalize(crossfade_loop(signal), 0.35)
    convert_to_m4a(save_wav("nature_crickets.wav", signal))


def generate_wind():
    """Wind: low-frequency filtered noise with gusts."""
    print("\n💨 Generating: Wind")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base wind
    noise = np.random.randn(n)
    wind = simple_lowpass(noise, 40)
    
    # Gusts (slow amplitude modulation)
    gust1 = 0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t)
    gust2 = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 1.5)
    
    # High whistle component
    whistle = simple_lowpass(np.random.randn(n), 10) * 0.15
    
    signal = wind * gust1 * gust2 + whistle * gust1
    signal = normalize(crossfade_loop(signal), 0.4)
    convert_to_m4a(save_wav("nature_wind.wav", signal))


def generate_distant_thunder():
    """Distant thunder: low rumbles without rain."""
    print("\n🌩️  Generating: Distant Thunder")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Quiet atmosphere
    ambience = np.random.randn(n)
    ambience = simple_lowpass(ambience, 60) * 0.1
    
    # Thunder rumbles (every 20-50 seconds)
    thunder = np.zeros(n)
    pos = np.random.randint(5 * SAMPLE_RATE, 15 * SAMPLE_RATE)
    while pos < n - 6 * SAMPLE_RATE:
        dur = np.random.randint(3 * SAMPLE_RATE, 6 * SAMPLE_RATE)
        rumble = np.random.randn(dur)
        rumble = simple_lowpass(rumble, 500)
        envelope = np.exp(-np.arange(dur) / (dur * 0.25))
        attack = np.minimum(np.arange(dur) / (SAMPLE_RATE * 0.5), 1.0)
        thunder[pos:pos+dur] += rumble * envelope * attack * 4.0
        pos += np.random.randint(20 * SAMPLE_RATE, 50 * SAMPLE_RATE)
    
    signal = ambience + thunder * 0.5
    signal = normalize(crossfade_loop(signal), 0.45)
    convert_to_m4a(save_wav("nature_distant_thunder.wav", signal))


# ============================================================
# INDOOR SOUNDS
# ============================================================

def generate_fireplace():
    """Fireplace: crackling with warm low-frequency base."""
    print("\n🔥 Generating: Fireplace")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Warm base (low-frequency hum of fire)
    base = np.random.randn(n)
    base = simple_lowpass(base, 80) * 0.3
    
    # Crackling (random sharp transients)
    crackle = np.zeros(n)
    n_crackles = int(DURATION * 8)  # 8 crackles per second
    
    for _ in range(n_crackles):
        pos = np.random.randint(0, n - 2000)
        dur = np.random.randint(100, 2000)
        amp = np.random.exponential(0.3)
        decay = np.exp(-np.arange(dur) / (dur * 0.15))
        burst = decay * np.random.randn(dur) * amp
        crackle[pos:pos+dur] += burst
    
    # Gentle breathing modulation
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.08 * t)
    
    signal = base * mod + crackle * 0.5
    signal = normalize(crossfade_loop(signal), 0.4)
    convert_to_m4a(save_wav("indoor_fireplace.wav", signal))


def generate_fan():
    """Electric fan: smooth white noise with subtle wobble."""
    print("\n🌀 Generating: Electric Fan")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    noise = np.random.randn(n)
    fan = simple_lowpass(noise, 8)
    
    # Fan wobble
    wobble = 0.95 + 0.05 * np.sin(2 * np.pi * 0.3 * t)
    # Motor hum
    hum = 0.05 * np.sin(2 * np.pi * 60 * t)
    
    signal = fan * wobble + hum
    signal = normalize(crossfade_loop(signal), 0.4)
    convert_to_m4a(save_wav("indoor_fan.wav", signal))


def generate_cafe():
    """Café ambience: murmuring voices + dishes + background music."""
    print("\n☕ Generating: Café Ambience")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Background chatter (band-passed noise)
    chatter = np.random.randn(n)
    chatter = simple_lowpass(chatter, 15)
    chatter = simple_highpass(chatter, 50)
    
    # Modulate to sound like conversation (rhythmic)
    talk_rhythm = 0.5 + 0.5 * np.sin(2 * np.pi * 2.5 * t)
    talk_rhythm2 = 0.6 + 0.4 * np.sin(2 * np.pi * 1.8 * t + 0.7)
    chatter = chatter * talk_rhythm * talk_rhythm2 * 0.3
    
    # Occasional clinks (dish/cup sounds)
    clinks = np.zeros(n)
    n_clinks = int(DURATION * 0.5)
    for _ in range(n_clinks):
        pos = np.random.randint(0, n - 5000)
        freq = np.random.uniform(3000, 6000)
        dur = np.random.randint(1000, 5000)
        envelope = np.exp(-np.arange(dur) / (dur * 0.1))
        clink = envelope * np.sin(2 * np.pi * freq * np.arange(dur) / SAMPLE_RATE)
        clinks[pos:pos+dur] += clink * np.random.uniform(0.05, 0.15)
    
    # Low background murmur
    murmur = simple_lowpass(np.random.randn(n), 40) * 0.2
    
    signal = chatter + clinks + murmur
    signal = normalize(crossfade_loop(signal), 0.35)
    convert_to_m4a(save_wav("indoor_cafe.wav", signal))


def generate_train():
    """Train journey: rhythmic clickety-clack + low rumble."""
    print("\n🚂 Generating: Train Journey")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base rumble (low-frequency continuous)
    rumble = np.random.randn(n)
    rumble = simple_lowpass(rumble, 60) * 0.4
    
    # Rhythmic clacking (rail joints every ~0.7 seconds)
    clack = np.zeros(n)
    clack_interval = int(0.7 * SAMPLE_RATE)
    
    for i in range(0, n - 1000, clack_interval):
        dur = np.random.randint(200, 500)
        decay = np.exp(-np.arange(dur) / 50.0)
        impact = decay * np.random.randn(dur) * 0.6
        clack[i:i+dur] += impact
        # Double clack (two wheels)
        offset = np.random.randint(100, 300)
        if i + offset + dur < n:
            clack[i+offset:i+offset+dur] += impact * 0.7
    
    # Slight speed variation
    speed_var = 0.9 + 0.1 * np.sin(2 * np.pi * 0.01 * t)
    
    signal = rumble * speed_var + clack * 0.4
    signal = normalize(crossfade_loop(signal), 0.45)
    convert_to_m4a(save_wav("indoor_train.wav", signal))


# ============================================================
# BABY SOUNDS
# ============================================================

def generate_pink_noise():
    """Pink noise (1/f spectrum)."""
    print("\n〰️  Generating: Pink Noise")
    n = SAMPLE_RATE * DURATION
    
    n_rows = 16
    array = np.random.randn(n_rows, n)
    pink = np.zeros(n)
    for i in range(n_rows):
        step = 2 ** i
        held = np.repeat(array[i, ::step], step)[:n]
        pink += held
    
    pink = normalize(crossfade_loop(pink), 0.45)
    convert_to_m4a(save_wav("baby_pink_noise.wav", pink))


def generate_heartbeat():
    """Womb heartbeat at ~70 BPM."""
    print("\n💓 Generating: Womb Heartbeat")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    bpm = 70
    beat_interval = 60.0 / bpm
    
    signal = np.zeros(n)
    
    for beat_start in np.arange(0, DURATION, beat_interval):
        # Lub
        envelope_lub = np.exp(-((t - beat_start) / 0.03) ** 2)
        signal += envelope_lub * np.sin(2 * np.pi * 45 * t) * 0.7
        # Dub
        dub_center = beat_start + 0.18
        envelope_dub = np.exp(-((t - dub_center) / 0.025) ** 2)
        signal += envelope_dub * np.sin(2 * np.pi * 55 * t) * 0.4
    
    # Body resonance
    rumble = simple_lowpass(np.random.randn(n), 500) * 0.05
    signal += rumble
    
    signal = normalize(crossfade_loop(signal), 0.55)
    convert_to_m4a(save_wav("baby_womb_heartbeat.wav", signal))


def generate_blood_flow():
    """Womb blood flow: low frequency whooshing."""
    print("\n🫀 Generating: Womb Blood Flow")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Brown noise
    white = np.random.randn(n)
    brown = np.cumsum(white) / np.sqrt(n)
    brown = brown / np.max(np.abs(brown))
    
    # Rhythmic modulation
    mod_freq = 70 / 60.0
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * mod_freq * t)
    whoosh = 0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * t)
    
    signal = brown * modulation * whoosh
    signal = simple_lowpass(signal, 200)
    signal = normalize(crossfade_loop(signal), 0.5)
    convert_to_m4a(save_wav("baby_womb_blood_flow.wav", signal))


def generate_shushing():
    """Rhythmic shushing sound."""
    print("\n🤫 Generating: Gentle Shushing")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    signal = np.zeros(n)
    shush_interval = 1.2
    
    for shush_start in np.arange(0, DURATION, shush_interval):
        shush_duration = 0.8
        envelope = np.where(
            (t >= shush_start) & (t <= shush_start + shush_duration),
            np.exp(-(t - shush_start) / 0.4),
            0
        )
        noise = np.random.randn(n) * 0.3
        signal += noise * envelope
    
    signal = simple_lowpass(signal, 10)
    signal = normalize(crossfade_loop(signal), 0.42)
    convert_to_m4a(save_wav("baby_shushing.wav", signal))


def generate_cat_purring():
    """Cat purring: rhythmic low-frequency vibration (~25Hz)."""
    print("\n🐱 Generating: Cat Purring")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Purr frequency 25Hz with harmonics
    purr_freq = 25
    purr = np.sin(2 * np.pi * purr_freq * t) * 0.5
    purr += np.sin(2 * np.pi * purr_freq * 2 * t) * 0.25
    purr += np.sin(2 * np.pi * purr_freq * 3 * t) * 0.1
    
    # Breathing modulation (inhale/exhale cycle ~3 seconds)
    breath = 0.6 + 0.4 * np.sin(2 * np.pi * (1.0/3.0) * t)
    
    # Add some noise texture
    noise = simple_lowpass(np.random.randn(n), 100) * 0.1
    
    signal = purr * breath + noise
    signal = normalize(crossfade_loop(signal), 0.45)
    convert_to_m4a(save_wav("baby_cat_purring.wav", signal))


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🔊 Muon Sound Generator v2 — Full Suite")
    print("=" * 50)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Duration: {DURATION}s | Sample rate: {SAMPLE_RATE}Hz")
    
    # Water (5)
    generate_light_rain()
    generate_thunderstorm()
    generate_ocean_waves()
    generate_stream()
    generate_waterfall()
    
    # Nature (4)
    generate_forest_birds()
    generate_crickets()
    generate_wind()
    generate_distant_thunder()
    
    # Indoor (4)
    generate_fireplace()
    generate_fan()
    generate_cafe()
    generate_train()
    
    # Baby (5)
    generate_pink_noise()
    generate_heartbeat()
    generate_blood_flow()
    generate_shushing()
    generate_cat_purring()
    
    print("\n" + "=" * 50)
    print("✅ All 18 sounds generated successfully!")
    print(f"Location: {OUTPUT_DIR}")

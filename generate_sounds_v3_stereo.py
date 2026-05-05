#!/usr/bin/env python3
"""
Muon 全量音效生成脚本 v3 - 立体声版
用算法生成全部18个高品质立体声音效
支持左右声道独立调制，增强沉浸感
"""

import numpy as np
import wave
import os
import subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Muon", "Resources", "Sounds_Stereo")
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
    """Save numpy array as WAV file (supports stereo)."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    data = np.clip(data, -1.0, 1.0)
    
    # Ensure stereo format (2 channels)
    if len(data.shape) == 1:
        # Mono to stereo
        data_stereo = np.column_stack((data, data))
    else:
        data_stereo = data
    
    data_int = (data_stereo * 32767).astype(np.int16)
    
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(2)
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
            '-b', '256000', '-s', '3'
        ], check=True, capture_output=True)
        os.remove(wav_path)
        print(f"  ✓ Converted: {os.path.basename(m4a_path)}")
        return m4a_path
    except Exception as e:
        print(f"  ⚠ Conversion failed: {e}")
        return wav_path


def crossfade_loop(data, crossfade_seconds=3.0, sample_rate=SAMPLE_RATE):
    """Create seamless loop using crossfade (supports stereo)."""
    cf_samples = int(crossfade_seconds * sample_rate)
    
    if len(data.shape) == 1:
        # Mono
        if cf_samples >= len(data) // 2:
            cf_samples = len(data) // 4
        fade_out = np.linspace(1, 0, cf_samples)
        fade_in = np.linspace(0, 1, cf_samples)
        data[:cf_samples] = data[:cf_samples] * fade_in + data[-cf_samples:] * fade_out
    else:
        # Stereo
        if cf_samples >= data.shape[0] // 2:
            cf_samples = data.shape[0] // 4
        fade_out = np.linspace(1, 0, cf_samples)
        fade_in = np.linspace(0, 1, cf_samples)
        data[:cf_samples, 0] = data[:cf_samples, 0] * fade_in + data[-cf_samples:, 0] * fade_out
        data[:cf_samples, 1] = data[:cf_samples, 1] * fade_in + data[-cf_samples:, 1] * fade_out
    
    return data


def normalize(data, target=0.5):
    """Normalize audio to target amplitude (supports stereo)."""
    if len(data.shape) == 1:
        peak = np.max(np.abs(data))
    else:
        peak = np.max(np.abs(data))
    
    if peak > 0:
        data = data / peak * target
    return data


def make_stereo(left, right=None):
    """Create stereo array from left and right channels."""
    if right is None:
        right = left
    
    n = len(left)
    stereo = np.column_stack((left, right))
    return stereo


def add_stereo_width(signal, width=0.5):
    """Add stereo width by delaying one channel slightly."""
    if len(signal.shape) == 1:
        return signal
    
    # Add slight delay to right channel for width
    delay_samples = int(0.001 * SAMPLE_RATE)  # 1ms delay
    right_shifted = np.roll(signal[:, 1], delay_samples)
    right_shifted[:delay_samples] = 0
    
    output = np.column_stack((
        signal[:, 0] * (1 - width) + right_shifted * width,
        signal[:, 1] * (1 - width) + signal[:, 0] * width
    ))
    
    return output


# ============================================================
# WATER SOUNDS (立体声版)
# ============================================================

def generate_light_rain():
    """Light rain: stereo with spatial raindrop placement."""
    print("\n🌧️  Generating: Light Rain (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base: filtered white noise (rain texture)
    noise_left = np.random.randn(n) * 0.3
    noise_right = np.random.randn(n) * 0.3
    
    rain_left = simple_lowpass(noise_left, 3)
    rain_right = simple_lowpass(noise_right, 3)
    
    # Add individual raindrop hits (spatial positioning)
    drops_left = np.zeros(n)
    drops_right = np.zeros(n)
    
    n_drops = int(DURATION * 80)
    drop_positions = np.random.randint(0, n, n_drops)
    drop_amplitudes = np.random.exponential(0.3, n_drops)
    drop_pan = np.random.uniform(-1, 1, n_drops)  # -1=left, 1=right
    
    for pos, amp, pan in zip(drop_positions, drop_amplitudes, drop_pan):
        if pos < n - 500:
            decay = np.exp(-np.arange(500) / 50.0)
            drop_signal = amp * decay * np.random.randn(500)
            
            # Pan drops spatially
            if pan < 0:
                drops_left[pos:pos+500] += drop_signal * (1 + pan)
            else:
                drops_right[pos:pos+500] += drop_signal * (1 - pan)
    
    drops_left = simple_lowpass(drops_left, 5)
    drops_right = simple_lowpass(drops_right, 5)
    
    # Combine
    signal_left = rain_left * 0.3 + drops_left * 0.5
    signal_right = rain_right * 0.3 + drops_right * 0.5
    
    # Gentle amplitude modulation (wind gusts)
    mod = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t)
    signal_left = signal_left * mod
    signal_right = signal_right * mod
    
    # Make stereo
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.3)
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("water_light_rain_stereo.wav", signal))


def generate_thunderstorm():
    """Heavy rain + distant thunder (stereo with spatial thunder)."""
    print("\n⛈️  Generating: Thunderstorm (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Heavy rain base
    rain_left = simple_lowpass(np.random.randn(n), 2) * 0.4
    rain_right = simple_lowpass(np.random.randn(n), 2) * 0.4
    
    # Thunder rumbles (spatial positioning)
    thunder_left = np.zeros(n)
    thunder_right = np.zeros(n)
    
    thunder_times = []
    pos = np.random.randint(10 * SAMPLE_RATE, 20 * SAMPLE_RATE)
    while pos < n - 5 * SAMPLE_RATE:
        thunder_times.append(pos)
        pos += np.random.randint(15 * SAMPLE_RATE, 40 * SAMPLE_RATE)
    
    for tpos in thunder_times:
        duration_samples = np.random.randint(2 * SAMPLE_RATE, 4 * SAMPLE_RATE)
        if tpos + duration_samples < n:
            rumble = np.random.randn(duration_samples)
            rumble = simple_lowpass(rumble, 400)
            envelope = np.exp(-np.arange(duration_samples) / (duration_samples * 0.3))
            attack = np.minimum(np.arange(duration_samples) / (SAMPLE_RATE * 0.3), 1.0)
            
            # Random stereo placement for thunder
            pan = np.random.uniform(-0.5, 0.5)
            thunder_left[tpos:tpos+duration_samples] += rumble * envelope * attack * (1 - pan) * 3.0
            thunder_right[tpos:tpos+duration_samples] += rumble * envelope * attack * (1 + pan) * 3.0
    
    # Wind gusts
    wind_mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.03 * t + np.random.randn())
    
    signal_left = rain_left * wind_mod + thunder_left * 0.4
    signal_right = rain_right * wind_mod + thunder_right * 0.4
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.4)
    signal = normalize(crossfade_loop(signal), 0.5)
    
    convert_to_m4a(save_wav("water_thunderstorm_stereo.wav", signal))


def generate_ocean_waves():
    """Ocean waves: stereo with left-right wave movement."""
    print("\n🌊 Generating: Ocean Waves (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base ocean noise
    ocean_left = simple_lowpass(np.random.randn(n), 50) * 0.4
    ocean_right = simple_lowpass(np.random.randn(n), 50) * 0.4
    
    # Wave surges with stereo panning
    wave_envelope_left = 0.5 + 0.5 * np.sin(2 * np.pi * (1.0/8.0) * t + 0.0)
    wave_envelope_right = 0.5 + 0.5 * np.sin(2 * np.pi * (1.0/8.0) * t + np.pi/4)
    
    # High-frequency splash (stereo)
    splash_noise_left = simple_lowpass(np.random.randn(n), 8) * (wave_envelope_left ** 3) * 0.5
    splash_noise_right = simple_lowpass(np.random.randn(n), 8) * (wave_envelope_right ** 3) * 0.5
    
    signal_left = ocean_left * wave_envelope_left + splash_noise_left
    signal_right = ocean_right * wave_envelope_right + splash_noise_right
    
    # Add subtle second harmonic
    wave2 = 0.3 * np.sin(2 * np.pi * (1.0/12.0) * t)
    signal_left = signal_left * (0.7 + 0.3 * wave2)
    signal_right = signal_right * (0.7 + 0.3 * wave2)
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.5)
    signal = normalize(crossfade_loop(signal), 0.5)
    
    convert_to_m4a(save_wav("water_ocean_waves_stereo.wav", signal))


def generate_stream():
    """Gentle stream: stereo with spatial bubbling."""
    print("\n💧 Generating: Gentle Stream (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base: band-passed noise
    noise_left = np.random.randn(n)
    noise_right = np.random.randn(n)
    
    stream_left = simple_highpass(simple_lowpass(noise_left, 5), 100) * 0.4
    stream_right = simple_highpass(simple_lowpass(noise_right, 5), 100) * 0.4
    
    # Bubbling sounds (spatial)
    bubbles_left = np.zeros(n)
    bubbles_right = np.zeros(n)
    
    n_bubbles = int(DURATION * 15)
    for _ in range(n_bubbles):
        pos = np.random.randint(0, n - 5000)
        dur = np.random.randint(1000, 5000)
        freq = np.random.uniform(800, 2000)
        envelope = np.exp(-np.arange(dur) / (dur * 0.2))
        bubble = envelope * np.sin(2 * np.pi * freq * np.arange(dur) / SAMPLE_RATE)
        
        # Random stereo placement
        if np.random.random() < 0.5:
            bubbles_left[pos:pos+dur] += bubble * np.random.uniform(0.1, 0.3)
        else:
            bubbles_right[pos:pos+dur] += bubble * np.random.uniform(0.1, 0.3)
    
    # Gentle modulation
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.1 * t)
    
    signal_left = stream_left * 0.4 * mod + bubbles_left * 0.3
    signal_right = stream_right * 0.4 * mod + bubbles_right * 0.3
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.6)
    signal = normalize(crossfade_loop(signal), 0.4)
    
    convert_to_m4a(save_wav("water_stream_stereo.wav", signal))


def generate_waterfall():
    """Waterfall: stereo with wide soundstage."""
    print("\n🌊 Generating: Waterfall (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Dense broadband noise (stereo)
    noise_left = np.random.randn(n)
    noise_right = np.random.randn(n)
    
    # Low-frequency emphasis
    low_left = simple_lowpass(noise_left, 30)
    low_right = simple_lowpass(noise_right, 30)
    mid_left = simple_lowpass(noise_left, 8)
    mid_right = simple_lowpass(noise_right, 8)
    
    # Very gentle modulation
    mod = 0.9 + 0.1 * np.sin(2 * np.pi * 0.02 * t)
    
    signal_left = (low_left * 0.5 + mid_left * 0.3 + noise_left * 0.1) * mod
    signal_right = (low_right * 0.5 + mid_right * 0.3 + noise_right * 0.1) * mod
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.7)  # Wide soundstage
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("water_waterfall_stereo.wav", signal))


# ============================================================
# NATURE SOUNDS (立体声版)
# ============================================================

def generate_forest_birds():
    """Forest birds: stereo with spatial bird positioning."""
    print("\n🐦 Generating: Forest Birds (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Forest ambience
    ambience_left = simple_lowpass(np.random.randn(n), 20) * 0.15
    ambience_right = simple_lowpass(np.random.randn(n), 20) * 0.15
    
    # Bird calls (spatial positioning)
    birds_left = np.zeros(n)
    birds_right = np.zeros(n)
    
    n_calls = int(DURATION * 3)
    
    for _ in range(n_calls):
        pos = np.random.randint(0, n - SAMPLE_RATE)
        call_dur = np.random.randint(int(0.05 * SAMPLE_RATE), int(0.3 * SAMPLE_RATE))
        freq_start = np.random.uniform(2000, 5000)
        freq_end = np.random.uniform(1500, 6000)
        freqs = np.linspace(freq_start, freq_end, call_dur)
        phase = np.cumsum(freqs / SAMPLE_RATE) * 2 * np.pi
        envelope = np.sin(np.linspace(0, np.pi, call_dur))
        chirp = envelope * np.sin(phase) * np.random.uniform(0.1, 0.4)
        
        # Random stereo placement
        pan = np.random.uniform(-1, 1)
        if pan < 0:
            birds_left[pos:pos+call_dur] += chirp * (1 + pan)
        else:
            birds_right[pos:pos+call_dur] += chirp * (1 - pan)
    
    signal_left = ambience_left + birds_left * 0.6
    signal_right = ambience_right + birds_right * 0.6
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.8)  # Wide stereo for birds
    signal = normalize(crossfade_loop(signal), 0.4)
    
    convert_to_m4a(save_wav("nature_forest_birds_stereo.wav", signal))


def generate_crickets():
    """Summer crickets: stereo with multiple cricket positions."""
    print("\n🦗 Generating: Summer Crickets (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Night ambience
    ambience_left = simple_lowpass(np.random.randn(n), 30) * 0.08
    ambience_right = simple_lowpass(np.random.randn(n), 30) * 0.08
    
    # Cricket chirps (multiple positions in stereo field)
    crickets_left = np.zeros(n)
    crickets_right = np.zeros(n)
    
    for i in range(5):
        freq = np.random.uniform(4000, 7000)
        chirp_rate = np.random.uniform(3, 8)
        duty = np.random.uniform(0.3, 0.6)
        
        pulse = (np.sin(2 * np.pi * chirp_rate * t) > (1 - 2*duty)).astype(float)
        tone = np.sin(2 * np.pi * freq * t) * pulse * np.random.uniform(0.1, 0.25)
        
        # Position in stereo field
        pan = (i - 2) / 3.0  # Spread from left to right
        crickets_left += tone * (1 - pan) * 0.5
        crickets_right += tone * (1 + pan) * 0.5
    
    signal_left = ambience_left + crickets_left
    signal_right = ambience_right + crickets_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.6)
    signal = normalize(crossfade_loop(signal), 0.35)
    
    convert_to_m4a(save_wav("nature_crickets_stereo.wav", signal))


def generate_wind():
    """Wind: stereo with swirling effect."""
    print("\n💨 Generating: Wind (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base wind (stereo)
    wind_left = simple_lowpass(np.random.randn(n), 40) * 0.4
    wind_right = simple_lowpass(np.random.randn(n), 40) * 0.4
    
    # Gusts (different timing for left/right)
    gust1_left = 0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t)
    gust1_right = 0.5 + 0.5 * np.sin(2 * np.pi * 0.04 * t + np.pi/3)
    gust2_left = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 1.5)
    gust2_right = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + 1.5 + np.pi/4)
    
    # High whistle component (stereo)
    whistle_left = simple_lowpass(np.random.randn(n), 10) * 0.15
    whistle_right = simple_lowpass(np.random.randn(n), 10) * 0.15
    
    signal_left = wind_left * gust1_left * gust2_left + whistle_left * gust1_left
    signal_right = wind_right * gust1_right * gust2_right + whistle_right * gust1_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.5)
    signal = normalize(crossfade_loop(signal), 0.4)
    
    convert_to_m4a(save_wav("nature_wind_stereo.wav", signal))


def generate_distant_thunder():
    """Distant thunder: stereo with spatial positioning."""
    print("\n🌩️  Generating: Distant Thunder (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Quiet atmosphere
    ambience_left = simple_lowpass(np.random.randn(n), 60) * 0.1
    ambience_right = simple_lowpass(np.random.randn(n), 60) * 0.1
    
    # Thunder rumbles (spatial)
    thunder_left = np.zeros(n)
    thunder_right = np.zeros(n)
    
    pos = np.random.randint(5 * SAMPLE_RATE, 15 * SAMPLE_RATE)
    while pos < n - 6 * SAMPLE_RATE:
        dur = np.random.randint(3 * SAMPLE_RATE, 6 * SAMPLE_RATE)
        rumble = np.random.randn(dur)
        rumble = simple_lowpass(rumble, 500)
        envelope = np.exp(-np.arange(dur) / (dur * 0.25))
        attack = np.minimum(np.arange(dur) / (SAMPLE_RATE * 0.5), 1.0)
        
        # Random stereo position
        pan = np.random.uniform(-0.7, 0.7)
        thunder_left[pos:pos+dur] += rumble * envelope * attack * (1 - pan) * 4.0
        thunder_right[pos:pos+dur] += rumble * envelope * attack * (1 + pan) * 4.0
        
        pos += np.random.randint(20 * SAMPLE_RATE, 50 * SAMPLE_RATE)
    
    signal_left = ambience_left + thunder_left * 0.5
    signal_right = ambience_right + thunder_right * 0.5
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.6)
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("nature_distant_thunder_stereo.wav", signal))


# ============================================================
# INDOOR SOUNDS (立体声版)
# ============================================================

def generate_fireplace():
    """Fireplace: stereo with spatial crackling."""
    print("\n🔥 Generating: Fireplace (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Warm base
    base_left = simple_lowpass(np.random.randn(n), 80) * 0.3
    base_right = simple_lowpass(np.random.randn(n), 80) * 0.3
    
    # Crackling (spatial)
    crackle_left = np.zeros(n)
    crackle_right = np.zeros(n)
    
    n_crackles = int(DURATION * 8)
    
    for _ in range(n_crackles):
        pos = np.random.randint(0, n - 2000)
        dur = np.random.randint(100, 2000)
        amp = np.random.exponential(0.3)
        decay = np.exp(-np.arange(dur) / (dur * 0.15))
        burst = decay * np.random.randn(dur) * amp
        
        # Random stereo placement
        if np.random.random() < 0.5:
            crackle_left[pos:pos+dur] += burst * 0.5
        else:
            crackle_right[pos:pos+dur] += burst * 0.5
    
    # Gentle breathing modulation
    mod = 0.8 + 0.2 * np.sin(2 * np.pi * 0.08 * t)
    
    signal_left = base_left * mod + crackle_left * 0.5
    signal_right = base_right * mod + crackle_right * 0.5
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.4)
    signal = normalize(crossfade_loop(signal), 0.4)
    
    convert_to_m4a(save_wav("indoor_fireplace_stereo.wav", signal))


def generate_fan():
    """Electric fan: stereo with motor hum."""
    print("\n🌀 Generating: Electric Fan (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    noise_left = np.random.randn(n)
    noise_right = np.random.randn(n)
    
    fan_left = simple_lowpass(noise_left, 8) * 0.4
    fan_right = simple_lowpass(noise_right, 8) * 0.4
    
    # Fan wobble (slightly different for left/right)
    wobble_left = 0.95 + 0.05 * np.sin(2 * np.pi * 0.3 * t)
    wobble_right = 0.95 + 0.05 * np.sin(2 * np.pi * 0.3 * t + 0.1)
    
    # Motor hum (stereo)
    hum_left = 0.05 * np.sin(2 * np.pi * 60 * t)
    hum_right = 0.05 * np.sin(2 * np.pi * 60 * t + 0.05)
    
    signal_left = fan_left * wobble_left + hum_left
    signal_right = fan_right * wobble_right + hum_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.3)
    signal = normalize(crossfade_loop(signal), 0.4)
    
    convert_to_m4a(save_wav("indoor_fan_stereo.wav", signal))


def generate_cafe():
    """Café ambience: stereo with spatial positioning."""
    print("\n☕ Generating: Café Ambience (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Background chatter (stereo)
    chatter_left = simple_lowpass(simple_highpass(np.random.randn(n), 50), 15) * 0.3
    chatter_right = simple_lowpass(simple_highpass(np.random.randn(n), 50), 15) * 0.3
    
    # Modulate to sound like conversation
    talk_rhythm = 0.5 + 0.5 * np.sin(2 * np.pi * 2.5 * t)
    talk_rhythm2 = 0.6 + 0.4 * np.sin(2 * np.pi * 1.8 * t + 0.7)
    chatter_left = chatter_left * talk_rhythm * talk_rhythm2 * 0.3
    chatter_right = chatter_right * talk_rhythm * talk_rhythm2 * 0.3
    
    # Occasional clinks (spatial)
    clinks_left = np.zeros(n)
    clinks_right = np.zeros(n)
    
    n_clinks = int(DURATION * 0.5)
    for _ in range(n_clinks):
        pos = np.random.randint(0, n - 5000)
        freq = np.random.uniform(3000, 6000)
        dur = np.random.randint(1000, 5000)
        envelope = np.exp(-np.arange(dur) / (dur * 0.1))
        clink = envelope * np.sin(2 * np.pi * freq * np.arange(dur) / SAMPLE_RATE)
        
        # Random stereo placement
        if np.random.random() < 0.5:
            clinks_left[pos:pos+dur] += clink * np.random.uniform(0.05, 0.15)
        else:
            clinks_right[pos:pos+dur] += clink * np.random.uniform(0.05, 0.15)
    
    # Low background murmur (stereo)
    murmur_left = simple_lowpass(np.random.randn(n), 40) * 0.2
    murmur_right = simple_lowpass(np.random.randn(n), 40) * 0.2
    
    signal_left = chatter_left + clinks_left + murmur_left
    signal_right = chatter_right + clinks_right + murmur_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.5)
    signal = normalize(crossfade_loop(signal), 0.35)
    
    convert_to_m4a(save_wav("indoor_cafe_stereo.wav", signal))


def generate_train():
    """Train journey: stereo with rhythmic clacking."""
    print("\n🚂 Generating: Train Journey (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Base rumble (stereo)
    rumble_left = simple_lowpass(np.random.randn(n), 60) * 0.4
    rumble_right = simple_lowpass(np.random.randn(n), 60) * 0.4
    
    # Rhythmic clacking (stereo with slight timing difference)
    clack_left = np.zeros(n)
    clack_right = np.zeros(n)
    
    clack_interval = int(0.7 * SAMPLE_RATE)
    
    for i in range(0, n - 1000, clack_interval):
        dur = np.random.randint(200, 500)
        decay = np.exp(-np.arange(dur) / 50.0)
        impact = decay * np.random.randn(dur) * 0.6
        
        # Slightly different timing for left/right (simulating wheel positions)
        offset = np.random.randint(50, 150)
        clack_left[i:i+dur] += impact * 0.4
        clack_right[i+offset:i+offset+dur] += impact * 0.7
    
    # Slight speed variation
    speed_var = 0.9 + 0.1 * np.sin(2 * np.pi * 0.01 * t)
    
    signal_left = rumble_left * speed_var + clack_left * 0.4
    signal_right = rumble_right * speed_var + clack_right * 0.4
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.3)
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("indoor_train_stereo.wav", signal))


# ============================================================
# BABY SOUNDS (立体声版)
# ============================================================

def generate_pink_noise():
    """Pink noise stereo version."""
    print("\n〰️  Generating: Pink Noise (Stereo)")
    n = SAMPLE_RATE * DURATION
    
    # Generate pink noise for left and right channels
    n_rows = 16
    pink_left = np.zeros(n)
    pink_right = np.zeros(n)
    
    array_left = np.random.randn(n_rows, n)
    array_right = np.random.randn(n_rows, n)
    
    for i in range(n_rows):
        step = 2 ** i
        held_left = np.repeat(array_left[i, ::step], step)[:n]
        held_right = np.repeat(array_right[i, ::step], step)[:n]
        pink_left += held_left
        pink_right += held_right
    
    signal = make_stereo(pink_left, pink_right)
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("baby_pink_noise_stereo.wav", signal))


def generate_heartbeat():
    """Womb heartbeat: stereo with body resonance."""
    print("\n💓 Generating: Womb Heartbeat (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    bpm = 70
    beat_interval = 60.0 / bpm
    
    signal_left = np.zeros(n)
    signal_right = np.zeros(n)
    
    for beat_start in np.arange(0, DURATION, beat_interval):
        # Lub
        envelope_lub = np.exp(-((t - beat_start) / 0.03) ** 2)
        signal_left += envelope_lub * np.sin(2 * np.pi * 45 * t) * 0.7
        signal_right += envelope_lub * np.sin(2 * np.pi * 45 * t) * 0.5
        
        # Dub
        dub_center = beat_start + 0.18
        envelope_dub = np.exp(-((t - dub_center) / 0.025) ** 2)
        signal_left += envelope_dub * np.sin(2 * np.pi * 55 * t) * 0.4
        signal_right += envelope_dub * np.sin(2 * np.pi * 55 * t) * 0.6
    
    # Body resonance (stereo)
    rumble_left = simple_lowpass(np.random.randn(n), 500) * 0.05
    rumble_right = simple_lowpass(np.random.randn(n), 500) * 0.05
    
    signal_left += rumble_left
    signal_right += rumble_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.2)  # Narrow stereo for intimacy
    signal = normalize(crossfade_loop(signal), 0.55)
    
    convert_to_m4a(save_wav("baby_womb_heartbeat_stereo.wav", signal))


def generate_blood_flow():
    """Womb blood flow: stereo low frequency whooshing."""
    print("\n🫀 Generating: Womb Blood Flow (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Brown noise (stereo)
    white_left = np.random.randn(n)
    white_right = np.random.randn(n)
    
    brown_left = np.cumsum(white_left) / np.sqrt(n)
    brown_right = np.cumsum(white_right) / np.sqrt(n)
    
    brown_left = brown_left / np.max(np.abs(brown_left))
    brown_right = brown_right / np.max(np.abs(brown_right))
    
    # Rhythmic modulation
    mod_freq = 70 / 60.0
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * mod_freq * t)
    whoosh = 0.8 + 0.2 * np.sin(2 * np.pi * 0.15 * t)
    
    signal_left = brown_left * modulation * whoosh
    signal_right = brown_right * modulation * whoosh
    
    signal_left = simple_lowpass(signal_left, 200)
    signal_right = simple_lowpass(signal_right, 200)
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.3)
    signal = normalize(crossfade_loop(signal), 0.5)
    
    convert_to_m4a(save_wav("baby_womb_blood_flow_stereo.wav", signal))


def generate_shushing():
    """Rhythmic shushing: stereo with spatial movement."""
    print("\n🤫 Generating: Gentle Shushing (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    signal_left = np.zeros(n)
    signal_right = np.zeros(n)
    
    shush_interval = 1.2
    
    for shush_start in np.arange(0, DURATION, shush_interval):
        shush_duration = 0.8
        envelope = np.where(
            (t >= shush_start) & (t <= shush_start + shush_duration),
            np.exp(-(t - shush_start) / 0.4),
            0
        )
        noise_left = np.random.randn(n) * 0.3
        noise_right = np.random.randn(n) * 0.3
        
        signal_left += noise_left * envelope
        signal_right += noise_right * envelope
    
    signal_left = simple_lowpass(signal_left, 10)
    signal_right = simple_lowpass(signal_right, 10)
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.4)
    signal = normalize(crossfade_loop(signal), 0.42)
    
    convert_to_m4a(save_wav("baby_shushing_stereo.wav", signal))


def generate_cat_purring():
    """Cat purring: stereo with rhythmic vibration."""
    print("\n🐱 Generating: Cat Purring (Stereo)")
    n = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n)
    
    # Purr frequency 25Hz with harmonics (stereo)
    purr_left = np.sin(2 * np.pi * 25 * t) * 0.5
    purr_right = np.sin(2 * np.pi * 25 * t) * 0.5
    
    purr_left += np.sin(2 * np.pi * 50 * t) * 0.25
    purr_right += np.sin(2 * np.pi * 50 * t) * 0.25
    
    purr_left += np.sin(2 * np.pi * 75 * t) * 0.1
    purr_right += np.sin(2 * np.pi * 75 * t) * 0.1
    
    # Breathing modulation (slightly different for left/right)
    breath_left = 0.6 + 0.4 * np.sin(2 * np.pi * (1.0/3.0) * t)
    breath_right = 0.6 + 0.4 * np.sin(2 * np.pi * (1.0/3.0) * t + 0.2)
    
    # Add some noise texture (stereo)
    noise_left = simple_lowpass(np.random.randn(n), 100) * 0.1
    noise_right = simple_lowpass(np.random.randn(n), 100) * 0.1
    
    signal_left = purr_left * breath_left + noise_left
    signal_right = purr_right * breath_right + noise_right
    
    signal = make_stereo(signal_left, signal_right)
    signal = add_stereo_width(signal, 0.3)
    signal = normalize(crossfade_loop(signal), 0.45)
    
    convert_to_m4a(save_wav("baby_cat_purring_stereo.wav", signal))


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🔊 Muon Sound Generator v3 — Stereo Edition")
    print("=" * 50)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Duration: {DURATION}s | Sample rate: {SAMPLE_RATE}Hz")
    print("Channels: Stereo (2-channel)")
    
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
    print("✅ All 18 stereo sounds generated successfully!")
    print(f"Location: {OUTPUT_DIR}")
    print("\n🎧 These are stereo versions with spatial positioning.")
    print("   Copy to Muon/Resources/Sounds/ and update Sound.swift")
    print("   to use *_stereo.m4a filenames.")

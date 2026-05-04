#!/usr/bin/env python3
"""
Muon 音效素材生成脚本
生成所有可以用算法生成的音效（粉红噪音、心跳、血流、嘘声等）
其余需要从 Pixabay/Freesound 手动下载
"""

import numpy as np
import struct
import wave
import os
import subprocess


def simple_lowpass(data, kernel_size):
    """Simple moving average low-pass filter (pure numpy, no scipy)."""
    kernel = np.ones(kernel_size) / kernel_size
    return np.convolve(data, kernel, mode='same')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "Muon", "Resources", "Sounds")
SAMPLE_RATE = 44100
DURATION = 180  # 3 minutes per file

os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_wav(filename, data, sample_rate=SAMPLE_RATE):
    """Save numpy array as WAV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    data = np.clip(data, -1.0, 1.0)
    data_int = (data * 32767).astype(np.int16)
    
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data_int.tobytes())
    
    print(f"  ✓ Generated: {filename}")
    return filepath


def convert_to_m4a(wav_path):
    """Convert WAV to M4A using ffmpeg/afconvert."""
    m4a_path = wav_path.replace('.wav', '.m4a')
    
    # Try afconvert (macOS native)
    try:
        subprocess.run([
            'afconvert', wav_path, m4a_path,
            '-f', 'mp4f', '-d', 'aac',
            '-b', '192000', '-s', '3'
        ], check=True, capture_output=True)
        os.remove(wav_path)
        print(f"  ✓ Converted: {os.path.basename(m4a_path)}")
        return m4a_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try ffmpeg
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', wav_path,
            '-c:a', 'aac', '-b:a', '192k',
            m4a_path
        ], check=True, capture_output=True)
        os.remove(wav_path)
        print(f"  ✓ Converted: {os.path.basename(m4a_path)}")
        return m4a_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ⚠ Could not convert to m4a (no ffmpeg/afconvert). Keeping WAV.")
        return wav_path


def apply_fade(data, fade_seconds=2.0, sample_rate=SAMPLE_RATE):
    """Apply fade-in and fade-out for seamless looping."""
    fade_samples = int(fade_seconds * sample_rate)
    fade_in = np.linspace(0, 1, fade_samples)
    fade_out = np.linspace(1, 0, fade_samples)
    data[:fade_samples] *= fade_in
    data[-fade_samples:] *= fade_out
    return data


def crossfade_loop(data, crossfade_seconds=2.0, sample_rate=SAMPLE_RATE):
    """Create seamless loop using crossfade."""
    cf_samples = int(crossfade_seconds * sample_rate)
    # Crossfade end into beginning
    fade_out = np.linspace(1, 0, cf_samples)
    fade_in = np.linspace(0, 1, cf_samples)
    data[:cf_samples] = data[:cf_samples] * fade_in + data[-cf_samples:] * fade_out
    return data


# ============================================================
# 1. Pink Noise (baby_pink_noise)
# ============================================================
def generate_pink_noise():
    """Generate pink noise (1/f spectrum) using Voss-McCartney algorithm."""
    print("\n🎵 Generating: Pink Noise")
    n_samples = SAMPLE_RATE * DURATION
    
    # Voss-McCartney pink noise
    n_rows = 16
    n_cols = n_samples
    array = np.random.randn(n_rows, n_cols)
    
    # Create pink noise by summing rows with different update rates
    pink = np.zeros(n_cols)
    for i in range(n_rows):
        step = 2 ** i
        held = np.repeat(array[i, ::step], step)[:n_cols]
        pink += held
    
    pink = pink / np.max(np.abs(pink)) * 0.5  # Normalize to 50% volume
    pink = crossfade_loop(pink)
    
    wav = save_wav("baby_pink_noise.wav", pink)
    convert_to_m4a(wav)


# ============================================================
# 2. Womb Heartbeat (baby_womb_heartbeat)
# ============================================================
def generate_heartbeat():
    """Generate realistic womb heartbeat at ~70 BPM."""
    print("\n🎵 Generating: Womb Heartbeat")
    n_samples = SAMPLE_RATE * DURATION
    bpm = 70
    beat_interval = 60.0 / bpm  # seconds per beat
    
    t = np.linspace(0, DURATION, n_samples)
    signal = np.zeros(n_samples)
    
    # Each heartbeat = lub-dub (two pulses)
    for beat_start in np.arange(0, DURATION, beat_interval):
        # Lub (louder, lower)
        lub_center = beat_start
        lub_duration = 0.08
        lub_freq = 45
        mask_lub = np.abs(t - lub_center) < lub_duration
        envelope_lub = np.exp(-((t - lub_center) / 0.03) ** 2)
        signal += envelope_lub * np.sin(2 * np.pi * lub_freq * t) * 0.7
        
        # Dub (softer, slightly higher)
        dub_center = beat_start + 0.18
        dub_duration = 0.06
        dub_freq = 55
        envelope_dub = np.exp(-((t - dub_center) / 0.025) ** 2)
        signal += envelope_dub * np.sin(2 * np.pi * dub_freq * t) * 0.4
    
    # Add low-frequency rumble (simulates body resonance)
    rumble = np.random.randn(n_samples) * 0.05
    # Low-pass filter the rumble
    
    rumble = simple_lowpass(rumble, 500)
    signal += rumble
    
    signal = signal / np.max(np.abs(signal)) * 0.6
    signal = crossfade_loop(signal)
    
    wav = save_wav("baby_womb_heartbeat.wav", signal)
    convert_to_m4a(wav)


# ============================================================
# 3. Womb Blood Flow (baby_womb_blood_flow)
# ============================================================
def generate_blood_flow():
    """Generate womb blood flow sound - low frequency whooshing."""
    print("\n🎵 Generating: Womb Blood Flow")
    n_samples = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n_samples)
    
    # Base: brown noise (low frequency emphasis)
    white = np.random.randn(n_samples)
    brown = np.cumsum(white) / np.sqrt(n_samples)
    brown = brown / np.max(np.abs(brown))
    
    # Rhythmic modulation (synced to ~70 BPM breathing/pulse)
    bpm = 70
    mod_freq = bpm / 60.0
    modulation = 0.7 + 0.3 * np.sin(2 * np.pi * mod_freq * t)
    
    # Whooshing effect
    whoosh_freq = 0.15  # Slow whoosh
    whoosh = 0.8 + 0.2 * np.sin(2 * np.pi * whoosh_freq * t)
    
    signal = brown * modulation * whoosh * 0.5
    
    # Low-pass effect (muffled, as heard inside womb)
    
    signal = simple_lowpass(signal, 200)
    
    signal = signal / np.max(np.abs(signal)) * 0.5
    signal = crossfade_loop(signal)
    
    wav = save_wav("baby_womb_blood_flow.wav", signal)
    convert_to_m4a(wav)


# ============================================================
# 4. Gentle Shushing (baby_shushing)
# ============================================================
def generate_shushing():
    """Generate rhythmic shushing sound."""
    print("\n🎵 Generating: Gentle Shushing")
    n_samples = SAMPLE_RATE * DURATION
    t = np.linspace(0, DURATION, n_samples)
    
    signal = np.zeros(n_samples)
    shush_interval = 1.2  # seconds between shushes
    
    for shush_start in np.arange(0, DURATION, shush_interval):
        # Each shush is shaped white noise
        shush_duration = 0.8
        center = shush_start + shush_duration / 2
        
        # Envelope: quick attack, slow release
        attack = np.exp(-((t - shush_start) / 0.05) ** 2)  
        sustain = np.where(
            (t >= shush_start) & (t <= shush_start + shush_duration),
            np.exp(-(t - shush_start) / 0.4),
            0
        )
        envelope = np.maximum(attack, sustain) * np.where(t >= shush_start, 1, 0)
        
        # Shaped noise (filtered white noise for "shhh")
        noise = np.random.randn(n_samples) * 0.3
        signal += noise * envelope
    
    # Slight low-pass to soften
    
    signal = simple_lowpass(signal, 10)
    
    signal = signal / np.max(np.abs(signal)) * 0.45
    signal = crossfade_loop(signal)
    
    wav = save_wav("baby_shushing.wav", signal)
    convert_to_m4a(wav)


# ============================================================
# 5. White Noise (for fan substitute) 
# ============================================================
def generate_white_noise_fan():
    """Generate smooth white noise (electric fan simulation)."""
    print("\n🎵 Generating: Electric Fan (White Noise)")
    n_samples = SAMPLE_RATE * DURATION
    
    noise = np.random.randn(n_samples)
    
    # Slight low-pass to simulate fan (not pure white, slightly warm)
    
    noise = simple_lowpass(noise, 8)
    
    # Very subtle amplitude modulation (fan wobble)
    t = np.linspace(0, DURATION, n_samples)
    wobble = 0.95 + 0.05 * np.sin(2 * np.pi * 0.3 * t)
    noise = noise * wobble
    
    noise = noise / np.max(np.abs(noise)) * 0.4
    noise = crossfade_loop(noise)
    
    wav = save_wav("indoor_fan.wav", noise)
    convert_to_m4a(wav)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🔊 Muon Sound Generator")
    print("=" * 50)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Duration: {DURATION}s per file")
    print(f"Sample rate: {SAMPLE_RATE}Hz")
    
    generate_pink_noise()
    generate_heartbeat()
    generate_blood_flow()
    generate_shushing()
    generate_white_noise_fan()
    
    print("\n" + "=" * 50)
    print("✅ All algorithmic sounds generated!")
    print("\n📋 Still need to download manually from Pixabay:")
    print("  1. water_light_rain.m4a")
    print("  2. water_thunderstorm.m4a")
    print("  3. water_ocean_waves.m4a")
    print("  4. water_stream.m4a")
    print("  5. water_waterfall.m4a")
    print("  6. nature_forest_birds.m4a")
    print("  7. nature_crickets.m4a")
    print("  8. nature_wind.m4a")
    print("  9. nature_distant_thunder.m4a")
    print("  10. indoor_fireplace.m4a")
    print("  11. indoor_cafe.m4a")
    print("  12. indoor_train.m4a")
    print("  13. baby_cat_purring.m4a")
    print(f"\nPlace downloaded files in: {OUTPUT_DIR}")

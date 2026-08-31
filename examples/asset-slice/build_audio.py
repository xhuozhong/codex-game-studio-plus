"""Generate an original PCM sound fixture beside this script; never replace an existing file."""
from pathlib import Path
import math, struct, wave
target = Path(__file__).with_name('hit.wav')
rate, count = 24000, 4800
with target.open('xb') as raw:
    with wave.open(raw, 'wb') as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(rate)
        samples = [int(9000 * math.sin(2 * math.pi * (480 - 180 * i / count) * i / rate) * (1 - i / count) ** 2) for i in range(count)]
        sound.writeframes(struct.pack('<' + 'h' * count, *samples))
print('Created original hit.wav (0.2 seconds); run audio_audit.py for sample measurements.')

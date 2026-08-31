"""Inspect PCM WAV levels and loop bounds without playback or modification."""
import argparse
import json
from pathlib import Path
import sys
import wave

def inspect(file, loop_start=None, loop_end=None):
    if bool(loop_start is not None) != bool(loop_end is not None):
        raise ValueError('Provide both loop frame bounds')
    with wave.open(str(file), 'rb') as audio:
        channels, width, rate, frames = audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()
        if audio.getcomptype() != 'NONE' or width not in (1, 2, 3, 4) or frames < 1:
            raise ValueError('Expected nonempty uncompressed integer PCM WAV (8/16/24/32-bit)')
        maximum, peak, squared, samples, clipped, read_frames = 2 ** (8 * width - 1), 0, 0, 0, 0, 0
        while raw := audio.readframes(8192):
            if len(raw) % (channels * width):
                raise ValueError('Truncated sample/frame data')
            read_frames += len(raw) // (channels * width)
            for offset in range(0, len(raw), width):
                sample = raw[offset] - 128 if width == 1 else int.from_bytes(raw[offset:offset + width], 'little', signed=True)
                peak = max(peak, abs(sample))
                squared += sample * sample
                samples += 1
                clipped += int(sample in (-maximum, maximum - 1))
        if read_frames != frames:
            raise ValueError('WAV declares more frames than available')
        if loop_start is not None and not (0 <= loop_start < loop_end <= frames):
            raise ValueError('Loop bounds must satisfy 0 <= start < end <= frame count')
        return {'ok': True, 'file': Path(file).name, 'channels': channels, 'sample_width': width,
                'sample_rate': rate, 'frames': frames, 'seconds': frames / rate,
                'peak_linear': peak / maximum, 'rms_linear': (squared / samples) ** 0.5 / maximum,
                'full_scale_samples': clipped, 'silent': peak == 0,
                'loop_frames': [loop_start, loop_end] if loop_start is not None else None,
                'limitation': 'No LUFS, codec/browser compatibility, loop audibility or listening verification.'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True)
    p.add_argument('--loop-start', type=int)
    p.add_argument('--loop-end', type=int)
    a = p.parse_args()
    try:
        result = inspect(a.input, a.loop_start, a.loop_end)
    except (ValueError, OSError, wave.Error, EOFError) as exc:
        result = {'ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1

if __name__ == '__main__':
    sys.exit(main())

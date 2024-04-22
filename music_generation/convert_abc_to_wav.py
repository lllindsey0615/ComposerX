from pathlib import Path
import subprocess
import os

def convert_abc_to_wav(abc_file_path, results_dir="results"):
    abc_file = Path(abc_file_path)  # abc file

    # Convert the ABC file to a MIDI file using abc2midi
    tmp_midi = Path(results_dir) / f'{abc_file.stem}.mid'
    subprocess.run(["abc2midi", abc_file, "-o", tmp_midi])

    # Convert MIDI to WAV using MuseScore (requires MuseScore installed)
    wav_file = Path(results_dir) / f'{abc_file.stem}.wav'
    subprocess.run(["/Applications/MuseScore 4.app/Contents/MacOS/mscore", "-f", "-o", wav_file, tmp_midi])

    print(f'output wav file: {wav_file}')
    return wav_file








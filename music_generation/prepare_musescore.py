# Usage: python prepare_musescore.py <convert_abc_to_wav.py> "your local musescore4 path"
#python prepare_musescore.py convert_abc_to_wav.py "/Applications/MuseScore 4.app/Contents/MacOS/mscore"

import sys
import re

import sys
import re

def prepare_musescore(script_path, musescore_path):
    # Pattern to find the MuseScore path line
    pattern = re.compile(r'subprocess\.run\(\["/[^"]+", "-f", "-o", wav_file, tmp_midi\]\)')

    try:
        # Read the script content
        with open(script_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace the MuseScore path with the new one
        new_content = pattern.sub(f'subprocess.run(["{musescore_path}", "-f", "-o", wav_file, tmp_midi])', content)

        # Write the modified content back to the script
        with open(script_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("MuseScore path updated successfully.")

    except FileNotFoundError:
        print(f"Error: The script file '{script_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python prepare_musescore.py <SCRIPT_PATH> <MUSESCORE_PATH>")
    else:
        script_path = sys.argv[1]
        musescore_path = sys.argv[2]
        prepare_musescore(script_path, musescore_path)


import subprocess
import os
import argparse
import sys
from convert_abc_to_wav import convert_abc_to_wav

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Welcome to ComposerX, a multi-agent based text-to-music generation system.")
parser.add_argument("--prompt", "-p", type=str, required=True, help="Input your prompt here")
parser.add_argument("--output_dir", "-o", type=str, required=True, help="Directory to store the results (Chat Log,ABC, WAV, an MIDI).")
args = parser.parse_args()

# Ensure the output directory exists
if not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

chat_log = []  # Initialize chat log

def extract_title(abc_notation):
    for line in abc_notation.split('\n'):
        if line.startswith('T:'):
            return line[2:].strip().replace(' ', '_') + '.abc'
    return "Untitled.abc"

def gene():
    prompt_file_path = "prompt.txt"
    chat_log_file_path = os.path.join(args.output_dir, "chat_log.txt")

    # Save the prompt to a file in the output directory
    with open(prompt_file_path, "w") as f:
        f.write(args.prompt)

    cmd = "python multi_agent_groupchat.py"

    try:
        g = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        outs, errs = g.communicate(input='exit')
        g.kill()
        print(outs)
        chat_log.append(outs)

        # Check if the expected output is present
        split_outs = outs.split("```")
        if len(split_outs) < 3:
            raise ValueError("ABC notation block not found in the output.")
        
        ori_abc = split_outs[-2]
        ori_abc = os.linesep.join([s for s in ori_abc.splitlines() if s])
        print(ori_abc)

        # Save chat log and ABC notation into files
        with open(chat_log_file_path, 'w') as f:
            f.writelines(chat_log)

        abc_filename = extract_title(ori_abc)
        abc_file_path = os.path.join(args.output_dir, abc_filename)
        with open(abc_file_path, 'w') as f:
            f.write(ori_abc)

        # Convert the ABC file to a WAV file
        convert_abc_to_wav(abc_file_path)
    except Exception as e:
        print(f"Generation failed: {e}")
        # Restart script on failure
        p = sys.executable
        os.execl(p, p, *sys.argv)

gene()

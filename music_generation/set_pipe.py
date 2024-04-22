import json
import subprocess
import os
import sys
from convert_abc_to_wav import convert_abc_to_wav
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Welcome to ComposerX, a multi-agent based text-to-music generation system.")
    parser.add_argument("--prompts_file", "-p", type=str, required=True, help="Path to the JSON file containing multiple prompts.")
    parser.add_argument("--results_dir", "-o", type=str, required=True, help="Directory to store the results.")
    return parser.parse_args()

def extract_title(abc_notation):
    for line in abc_notation.split('\n'):
        if line.startswith('T:'):
            return line[2:].strip().replace(' ', '_') + '.abc'
    return "Untitled.abc"

def run_multi_agent_system(prompt, results_dir):
    chat_log_file = os.path.join(results_dir, 'chat_log.txt')
    prompt_text_file = "prompt.txt"

    with open(prompt_text_file, "w") as f:
        f.write(prompt)

    header = f"\n\n--- Prompt: {prompt} ---\n\n"
    with open(chat_log_file, "a") as f:
        f.write(header)

    cmd = "python multi_agent_groupchat.py"
    try:
        process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        outs, _ = process.communicate(input='exit')
        process.kill()
        print(outs)

        with open(chat_log_file, "a") as f:
            f.write(outs)

        ori_abc = outs.split("```")[-2]
        ori_abc = os.linesep.join([s for s in ori_abc.splitlines() if s])
        abc_filename = extract_title(ori_abc)
        abc_filepath = os.path.join(results_dir, abc_filename)
        with open(abc_filepath, 'w') as f:
            f.write(ori_abc)

        return abc_filepath
    except Exception as e:
        print(f"Error during generation: {e}")
        return None

def main():
    args = parse_arguments()
    results_dir = args.results_dir
    prompts_file = args.prompts_file
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    with open(prompts_file, "r") as file:
        prompts = json.load(file)

    for index, prompt in enumerate(prompts):
        print(f"Prompt {index + 1}: {prompt['prompt']}")
        abc_filepath = run_multi_agent_system(prompt['prompt'], results_dir)
        if abc_filepath:
            wav_filename = convert_abc_to_wav(abc_filepath, results_dir)
            if wav_filename:
                print(f"Generated WAV file: {wav_filename}")

if __name__ == "__main__":
    main()

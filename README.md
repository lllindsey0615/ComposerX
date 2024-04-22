# ComposerX

## Introduction

This is code for paper "ComposerX: Multi-Agent Symbolic Music Composition with LLMs[here](paper link)
ComposerX is a multi-agent based text-to-music generation system powered by GPT where each GPT plays a role in the process of music composition. This is our demo page[here](https://lllindsey0615.github.io/ComposerX_demo/)


## Preparation

-Clone this project and install requirements.
-Download and install MuseScore [here](https://musescore.org/en/download) and add it to enviroment PATH.
-Download and install abc2midi [here](https://abcplus.sourceforge.net/) and add it to enviroment PATH.
-Download AutoGen here: [here](https://github.com/microsoft/autogen)

##Curated Prompt set:
prompt_set.json contains the curated prompt set using self-instruct


## Generate your music
-Prepare your MuseScore
```
python prepare_musescore.py convert_abc_to_wav.py "your local musescore4 path"
```

-Prepare your API
In music_generation/OAI_CONFIG_LIST, replace the api model and key with your own

-For one-time prompt input, run
```
python multi_agent_pipe.py -p "input your prompt here" -o "directory to store the results"
```

-For multiple time prompts input, run
```
set_pipe.py -p "path to your JSON file that contains multiple prompts" -o "directory to store the results"
```

## Acknoledgements


import openai
import json
import random
import numpy as np
import os
import time
import argparse
import copy
from multiprocessing import Pool
from ratelimiter import RateLimiter
import jsonlines
import random
from tqdm import tqdm
#from converter import abc2midi
# use seed 0
np.random.seed(0)
random.seed(0)
CoT_instruction="""Now the chord progression and other information are provided,you are required to create a ***16-bar long*** piece of music based on these informations."""
chord_instruction=""" Based on the song information in the ABC notation format provided earlier, generate a ***16-bar long*** chord progression and return it in text form, \
  with each bar separated by a "|" symbol. The generated chord progression should be consistent with the song's key and as closely aligned with the song's theme and characteristics as possible."""
instructionGpt1="""You are an intelligent agent with musical intelligence, and your goal is to create music that meets the relevant needs and human listening habits.\
    In this task, use ABC as the format for outputting sheet music.When return the results.Below are the requirements for the music,it contains music elements like title,genre,key and more:"""
chord_input="""input:
music information:
X:1
T:Chinese Style Melody
M:4/4
L:1/8
Q:120
K:Eb
chord progression:
| Eb | Bb | Cm | Ab |
| Eb | Bb | Gm | Ab |
| Cm | Fm | Bb | Ab |
| Cm | Bb | Gm | Eb |"""

chord_output="""output:
X:1
T:Chinese Style Melody
M:4/4
L:1/8
Q:120
K:Eb
z EF G2E EG | B2 z2 c3/2c/ BA | G2 z E EE | AA/c/ eA3z2 |
 z EF G2E EB  | d3 c BA z2|  z Bc B2G/A/ ce | dA3z4 | 
 ce GB c3B | c2 A3 z | z2 z G B/d/e fd |ec2A2z3| 
 ce GB dc2 A|BE F3z2 G | Bc d2 B2 cG | AF E6 |"""

Music_instruction="""Here are some tips for generating melodies that can be used as input prompts for the large model:

1. The generated melody should have clear phrase divisions, and it's preferable to avoid more than two consecutive measures within one phrase\
    to prevent an uncomfortable listening experience. There should be a certain amount of space between phrases, allowing the audience to clearly distinguish between them.

2. A phrase usually has a prominent ending note, which is the last note of the entire phrase. It typically has a longer duration, \
  or it might be followed by a rest. ***This ending note is usually within the key or the chord***,ex.phrases ending with a Cmaj chord usually terminate on one of the three chord tones, C, E, or G \
    ensuring a stable listening experience.

3. When generating melodies, the movement of the notes should primarily consist of stable intervals such as whole steps, thirds, and fifths,\
    while avoiding excessive large leaps. This will help maintain a sense of logic and coherence throughout the composition.

4. The rhythm of the phrases should be rich and harmonious. Try using different rhythmic patterns to build the melody, \
  such as combining eighth notes with **sixteenth notes, syncopated rhythms, or triplets**.

Below are some examples you can learn from,do not use the song names and other information directly as shown in the examples:"""
'''instruction1="""Now according to the ABC notation melody above,you should rewrite the melody,now delete every note and for every four bars,\
choose 2 or 3 or 4 notes within the key.They are the end of every phrase,so the number of the notes you choose decide how many phrase we will generate in next turns.\
By this displine,the number of it has relationship with the speed of rythm.In general,fast rythm styles like funk or disco have a shorter phrase,\
leading to more phrases each four bars,slow rythm styles have longer phrase,leading to a less number of phrases each four bars.
There shoud at least one bar between each note.Return the results by the format of following demonstration,notice that only return result without the word 'output':"""'''
inf_instruction="""First, you need to determine all the information related to the piece in the ABC notation format, such as the name,tune, speed, mode, and anything other than the notes. \
  ***Key should only be major.***This forms the basis of the piece's style.***Note that only return the music information in ABC notation format without any notes or text or Additional note.*** """
instruction2="""For a 16 bars long melody,you have three notes as the end of a phrase for each four bars,it's splited by ';' between each four bars and \
splited by',' between each note.Now according to the numbers of notes,generate a phrase for each note,use the notes as the end of a pharse.
As the ending notes,it should be longer than other notes to make the feeling of end of a phrase.\
Try to use notes of different length in a phrase to avoid boring melody,and try to use syncopation,anacrusis or triple notes to enrich the melody.
Here's an example of it following,Return it in ABC notation.
"""
instructionICL="""You are an intelligent agent with musical intelligence, and your goal is to create music that meets the relevant needs and human listening habits.\
    In this task, use ABC as the format for outputting sheet music.***Only return the ABC notation without any other description or text,and only return one piece that follow the music description given this time.***Below are the requirements for the music,it contains music elements like title,genre,key and more,and some composition examples are listed after the requirements:"""
instruction1="""Now, generate a ***16 bars long melody*** in ABC notation based on the given ABC-formatted work information and chord progression above, \
  so that it becomes a complete ABC notation formatted piece of music.In the generated ABC notation format work,all music-related information shou be \
    consistent with the information provided.Below are some demonstrations that can be used for formatting references:"""
instructionGpt="""You are an intelligent agent with musical intelligence, and your goal is to create music that meets the relevant needs and human listening habits.\
    In this task, use ABC as the format for outputting sheet music.***Only return the ABC notation without any other description or text,and only return one piece that follow the music description given this time.***Below are the requirements for the music,it contains music elements like title,genre,key and more:"""
instruction_fix="""You are a professional composer,here's a 16-bars long melody in ABC notation format,and there's something need optimization.
Below are the judgement of this piece and the melody in ABC notation.Try to optimize it and return the optimized one in ABC. """
instruction_judge='''You are a professional composer, and now you need to analyze a given 16-bar melody. This melody will be provided in the standard ABC notation format, along with the corresponding 16-bar harmonic progression. You need to evaluate the melody from the following aspects:

1. Is the melody's phrasing clear? A musical phrase should have a relatively obvious ending note, and there should be some distance between a phrase and the ones before and after it. Rate the clarity of the phrases in this melody on a scale of 1 to 5.   

2. Is the melodic progression of each bar harmonious with the harmony of that bar? Typically, the melody notes consist of chord tones, which highlight the chord tone. Rate the harmony of this melody on a scale of 1 to 5.

3. If the melody has clear phrases, are there any recognizable patterns among the different phrases, such as several phrases with roughly the same beginning, or phrases that are related by modulation? Rate the pattern recognizability of this melody on a 
scale of 1 to 5.

4. Is the rhythm of the notes too rigid and monotonous? An overly monotonous choice of note duration values can make the melody sound lackluster and unvarying. A good melody usually consists of various note durations, such as eighth notes, quarter notes, etc. Rate the rhythmic richness of this melody on a scale of 1 to 5.

5. Is the musical information consistent? Musical information includes the song's name, tonality, tempo, time signature, etc. Rate the consistency of the musical information in this melody on a scale of 1 to 5.

6.Check whether the number of beats in each measure is equal to the total duration of all notes and rests. For example, in a 4/4 time signature, if a measure has one half note and three quarter notes, the durations do not match. Indicate the number of measures out of 16 where the beats and note durations are not equal.
Below are 16 bars long chord progression and ABC notation piece. \n'''

ex1_in="""Human: Write a song that has the characteristics of Bach's musical compositions. </s> Assistant: """
ex1_out="""1. Title: \"Contrapuntal Mastery\"\n\nVerse 1:\nGently flowing melodies, intertwined in harmony,\nA symphony of voices, each with its own unique tone,\nIntricate counterpoint, a tapestry of sound,\nBach's music, a testament to his genius and renown.\n\nChorus 1:\nContrapuntal mastery, a hallmark of Bach's style,\nHis compositions, a timeless treasure trove,\nThe artistry of his work, a testament to his skill,\nA legacy that lives on through generations untold.\n\nVerse 2:\nFugues and canons, intricately woven together,\nAwe-inspiring complexity, yet still soothing to the ear,\nThe art of polyphony, a feast for the senses,\nBach's music, a journey into the realm of the sublime.\n\nChorus 2:\nContrapuntal mastery, a hallmark of Bach's style,\nHis compositions, a timeless treasure trove,\nThe artistry of his work, a testament to his skill,\nA legacy that lives on through generations untold.\n\nBridge:\nFrom Brandenburg Concertos to Mass in B Minor,\nEach piece a masterpiece, a testament to Bach's genius,\nHis ability to weave complex melodies,\nCreating a musical tapestry that captivates and inspires.\n\nChorus 3:\nContrapuntal mastery, a hallmark of Bach's style,\nHis compositions, a timeless treasure trove,\nThe artistry of his work, a testament to his skill,\nA legacy that lives on through generations untold.\n\nOutro:\nBach's music, a testament to his brilliance,\nA timeless legacy that continues to inspire and move us,\nHis contrapuntal mastery, a hallmark of his style,\nA gift that will never fade, forever etched in our hearts. """
ex2_in="""Human: Construct a melodious and harmonious piece that emulates the essence of Bach's iconic works. </s> Assistant: """
ex2_out='''X:1\nT:Music21 Fragment\nT:Music21 Fragment\nT:Music21\nC:Music21\n%%score 1 2 3 4\nL:1/8\nM:4/4\nK:C\nV:1 treble nm=\"Piano\" snm=\"Pno\"\n%%MIDI program 0\n%%MIDI control 7 100\n%%MIDI control 10 64\nL:1/4\nV:2 treble nm=\"Piano\" snm=\"Pno\"\n%%MIDI channel 3\n%%MIDI program 0\n%%MIDI control 7 100\n%%MIDI control 10 64\nV:3 bass nm=\"Piano\" snm=\"Pno\"\n%%MIDI channel 4\n%%MIDI program 0\n%%MIDI control 7 100\n%%MIDI control 10 64\nV:4 bass nm=\"Piano\" snm=\"Pno\"\n%%MIDI channel 5\n%%MIDI program 0\n%%MIDI control 7 100\n%%MIDI control 10 64\nV:1\n G2 A2 | !fermata!B2 A c | c B A A | !fermata!G2 A A | G F E E | !fermata!D2 D A | A G A B | %7\n c B A2 | !fermata!G2 G =F/G/ | A G G F | !fermata!E4 | E2 D2 | G2 A B | c c !fermata!c2 | %14\n c c B A | G A B B | !fermata!B2 E D | G A/B/ c c | !fermata!c2 c c | B A !fermata!G A | A G F E | %21\n !fermata!D2 D A | A G A B | c B A2 | !fermata!G2 G =F/G/ | A G G F | !fermata!E4 | B2 c2 | %28\n !fermata!d2 z B | d c B A | !fermata!G2 B c | d B/c/ d c | B A !fermata!G A | A G F E | %34\n !fermata!D2 D A | A G A B | c B A2 | !fermata!G2 G =F/G/ | A G G F | !fermata!E4 |] %40\nV:2\n EF G2 G^F/E/ F2 | !fermata!G4 =F2 E2 | A2 G2 G^F/E/ F2 | !fermata!D4 =FE D^C | D^C D3 C/B,/ C2 | %5\n !fermata!A,4 D2 E2 | F/E/ D2 E/D/ C F2 E | E/^F/ G2 G2 F/E/ F2 | !fermata!D4 E2 D2 | CD E2 E2 D2 | %10\n C2 B,A, !fermata!B,4 | B,2 CB, A,2 B,C | DF ED CD/E/ F2 | E/F/ G2 F2 E/D/ !fermata!E2 | %14\n E/^F/ G2 F2 E/D/ ^C/B,/A, | D C2 A2 G ^F/E/F | !fermata!E4 C3 B, | CD/E/ F/E/F E2 F2 | %18\n FE/D/ !fermata!E2 EA/^G/ A2 | A G2 ^F !fermata!D2 =FG | AG/F/ F E2 D2 ^C | %21\n !fermata!A,4 A,2 D/E/F | F3 E E/D/E/G/ F/E/^F/A/ | GD D G2 ^F/E/ F2 | !fermata!D4 E2 =FE | %25\n F2 FE/D/ E2 ED/C/ | B,D C4 !fermata!B,2 | G4 G4 | !fermata!G4 z2 G2 | G3 A2 G2 ^F | %30\n !fermata!D4 G2 A2 | AG/^F/ G2 G3 F | B,/C/D ED/C/ !fermata!B,2 D2 | D_E D^C D3 C | %34\n !fermata!A,4 D2 E2 | A, ^F2 E F3 E/^D/ | E =D2 G2 ^F/E/ F2 | !fermata!D4 DE DE | FE DG ^CA, D2 | %39\n ^C2 =C2 !fermata!B,4 |] %40\nV:3\n B,3 C/D/ EA, D2 | !fermata!D4 D2 CD | E4 EC A,D/C/ | !fermata!B,4 DC/_B,/ A,2 | %4\n _B,2 A,D B,G, E,A,/G,/ | !fermata!F,4 F,2 E,A, | A,D/C/ B,C/B,/ A,C DC/B,/ | %7\n A,G,/A,/ B,C/D/ EC A,D | !fermata!B,4 C3 _B, | A,=B, C_B, A, B,2 A, | A,2 ^G,^F, !fermata!G,4 | %11\n =G,2 A,G, ^F,2 G,2 | G,D CB, A,3 G,/F,/ | G,C/_B,/ A,2 !fermata!G,4 | A,2 A,2 =B,G, ED/=C/ | %15\n B,C/_B,/ A,D/C/ =B,D D/C/B,/A,/ | !fermata!G,4 G,2 G,2 | G,2 CD G,2 A,2 | %18\n A,G,/F,/ !fermata!G,2 CD E2 | ED ED/C/ !fermata!B,2 D2 | D^C DA, A,2 _B,A,/G,/ | %21\n !fermata!F,4 F,G, A,D | D=B, G,C/B,/ A,3 G,/^F,/ | E,A, B, E2 C A,D/C/ | !fermata!B,4 C3 _B, | %25\n C/_B,/C DG, CB, A,=B,/A,/ | ^G,2 A,4 !fermata!G,2 | E4 E4 | !fermata!B,4 z2 D2 | D2 ED D2 ED/C/ | %30\n !fermata!B,4 E2 E2 | D2 DC B,3 A, | A, G,2 ^F, !fermata!G,2 =F,G, | A, C2 _B,2 =B, E,A,/=G,/ | %34\n !fermata!^F,4 B,2 ^C2 | D3 C/B,/ C ^D2 G,/A,/ | G, A,2 G, E/D/ C2 B,/A,/ | %37\n !fermata!B,4 B,_B, A,G, | F,3 E,/D,/ E,F,/G,/ A,B, | B,A,/^G,/ A,3 G,/^F,/ !fermata!G,2 |] %40\nV:4\n\"Em\" E,3 D,\"Am7/C\" C,2\"D\" D,2 |\"G\" !fermata!G,,4\"Dm\" D,2\"Am\" A,,B,, | %2\n\"Am/C\" C,D,\"Em\" E,D,\"Am7/C\" C,A,,\"D\" D,2 |\"G\" !fermata!G,,4\"D7/F#\" ^F,2\"Dm/E\" E,2 | %4\n\"G#'''
instruction='''Write the code of nyquist programming language,which is used to create music.The length of the piece should be 16 bars long.'''

def load_api_key(path):
  with open(path, "r") as f:
    api_key = json.load(f)
  return api_key
request="Write a song that has the characteristic of Chinese music composition"

def ORI(md):
  try:
    results = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instructionGpt+md} 
            ]
        )["choices"][0]["message"]["content"]
  except:
    results='api error'
  print(results)
  return results

def ICL(md,ex_list):
  try:
    
    results = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instructionGpt+md+request},
                {"role": "user", "content": ex_list['Prompt']},
                {"role": "assistant", "content": ex_list['Output']},
            ]
        )["choices"][0]["message"]["content"]
  except:
    results='api error'
  print(results)
  return results

def ROLE(md):
  try:
    results = openai.ChatCompletion.create(
            engine=API_KEY.get("engine", None),
            model=API_KEY.get("model", None),
            request_timeout = API_KEY["request_timeout"],
            messages=[
                  {"role": "system", "content": instructionGpt+md+Music_instruction} 
              ]
          )["choices"][0]["message"]["content"]
  except:
    results='api error'
  print(results)
  return results

def COT(MD):
  try:
    results = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          #model="gpt-4-1106-preview",
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instructionGpt1+MD+inf_instruction}
              ]
        )["choices"][0]["message"]["content"]
    print(results)
    results2 = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          #model="gpt-4-1106-preview",
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instructionGpt1+MD+results+chord_instruction}
              ]
        )["choices"][0]["message"]["content"]
    print(results2)
    results3 = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          #model="gpt-4-1106-preview",
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instructionGpt+MD+results+results2+instruction1+chord_input+chord_output+CoT_instruction}
              ]
        )["choices"][0]["message"]["content"]
    results=' '.join([results+results2+results3])
  except:
    results='api error'
    results3='api error'
  print(results)
  return results,results3

def critic(ABC):
  results = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instruction_judge+ABC} 
            ]
        )["choices"][0]["message"]["content"]
  print(results)
  return results

def rewrite(ABC,judgement):
  results = openai.ChatCompletion.create(
          engine=API_KEY.get("engine", None),
          model=API_KEY.get("model", None),
          request_timeout = API_KEY["request_timeout"],
          messages=[
                {"role": "system", "content": instruction_fix+judgement+ABC} 
            ]
        )["choices"][0]["message"]["content"]
  print(results)
  return results

argparse = argparse.ArgumentParser()
argparse.add_argument('--chunk_size', '-c', type=int, default=256)
argparse.add_argument('--start_idx', '-s', type=int, default=0)
argparse.add_argument('--end_idx', '-e', type=int, default=None)
argparse.add_argument('--num_processes', '-p', type=int, default=8)
argparse.add_argument('--api_key', '-k', type=str, default='key-ust-gpt4.json')
argparse.add_argument("--music_discription",'-md',type=str,default='Make a song with chinese style')
argparse.add_argument('--model', '-m', type=str, default='ICL')
args = argparse.parse_args()
random.seed(time.perf_counter())
CHUNK_SIZE = args.chunk_size
START_IDX = args.start_idx
END_IDX = args.end_idx
NUM_PROCESSES = args.num_processes
API_KEY_PATH = args.api_key
MODEL=args.model
  #LANGUAGES = load_languages("data/all-text/languages.txt")
API_KEY = load_api_key(API_KEY_PATH)
MUSIC_DISCRIPTION=args.music_discription
  #NUM_PROCESSES * PROCESS_RATE = API_KEY["RPM"]
assert API_KEY["RPM"] >= NUM_PROCESSES, "API_KEY['RPM'] must be greater than or equal to NUM_PROCESSES"
PROCESS_RATE = round(API_KEY["RPM"] / NUM_PROCESSES)
assert PROCESS_RATE > 0, "PROCESS_RATE must be greater than 0"
rate_limiter = RateLimiter(max_calls=PROCESS_RATE, period=60)

if API_KEY["api_type"] == "azure":
    openai.api_type = API_KEY["api_type"]
    openai.api_version = API_KEY["api_version"]
    openai.api_base = API_KEY["api_base"]
openai.api_key = API_KEY["api_key"]

data=[]
with open('prompt_set_v2.json','rb') as f:
  set=json.load(f)
  f.close()
'''with open("text_description.txt",'rb') as f:
    line=f.readline()
    while line:
        line=str(line,"utf-8")
        data.append(line)
        line=f.readline()
set=data[::2]'''


'''match MODEL:
    case 'ICL':
      abc=ICL(MUSIC_DISCRIPTION)
    case  'ORI':
      abc=ORI(MUSIC_DISCRIPTION)
    case 'COT':
      abc=COT(MUSIC_DISCRIPTION)
    case 'ROLE':
      abc=ROLE(MUSIC_DISCRIPTION)'''
with open('textune_test/13_preds.json','rb') as f:
    icl1 = json.load(f)
with open('bach_test/setting18_full_preds.json','rb') as f:
    icl2 = json.load(f)
icl_ex=icl1+icl2
new_list={}
icl_list=[]
ori_list=[]
cotL_list=[]
cot_list=[]
role_list=[]
#set=set[0:73]
num=0
for prompt in tqdm(set):
  prompt=str(prompt)
  num=num+1
  #MUSIC_DISCRIPTION=md_list[k]['prompt']
  MUSIC_DISCRIPTION=prompt
  n=random.randint(0,len(icl_ex)-1)
  ex_list=icl_ex[n]
  for i in range(1):
    icl=ICL(MUSIC_DISCRIPTION,ex_list)
    ori=ORI(MUSIC_DISCRIPTION)
    cotLog,cot=COT(MUSIC_DISCRIPTION)
    role=ROLE(MUSIC_DISCRIPTION)
    icl_list.append(icl)
    ori_list.append(ori)
    cot_list.append(cot)
    cotL_list.append(cotLog)
    role_list.append(role)
    new_list['response_icl%d'%num]=icl
    new_list['response_ori%d'%num]=ori
    new_list['response_cot%d'%num]=cot
    new_list['response_cotLog%d'%num]=cotLog
    new_list['response_role%d'%num]=role
    

with open("generated_SingleGpt3.5.json",'w') as f:
  json.dump(new_list,f,indent=1)

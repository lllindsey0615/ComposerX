import subprocess
import os
from midi2audio import FluidSynth
import argparse
import sys
from Single_agent import ORI,COT,ROLE,ICL
from convert_abc_to_wav import convert_abc_to_wav
argparse=argparse.ArgumentParser()
argparse.add_argument("--prompt","-p",type=str,default="\"""create a R&B song\"""")
argparse.add_argument("--agent","-a",type=str,default="ORI")
args=argparse.parse_args()
fs=FluidSynth(sound_font='TimGM6mb.sf2')
MUSIC_DISCRIPTION=args.prompt
AGENT=args.agent
try:
    match AGENT:
        case 'ICL':
            abc=ICL(MUSIC_DISCRIPTION)
        case  'ORI':
            abc=ORI(MUSIC_DISCRIPTION)
        case 'COT':
            abc_log,abc=COT(MUSIC_DISCRIPTION)
        case 'ROLE':
            abc=ROLE(MUSIC_DISCRIPTION)
    with open('single_temp.abc','w') as f:
        #f.write(ori_abc.encode('unicode-escape').decode('utf8'))
            print(abc,file=f)
            f.close()
    
    '''check=abc2midi('abc_temp.abc',None)
    if check==1:
            fs.midi_to_audio('abc_temp.mid','wav_temp.wav')'''
    convert_abc_to_wav('single_temp.abc')
except:
        p=sys.executable
        os.execl(p,p,*sys.argv)
        sys.exit()
import music21 as m21
from pathlib import Path
import subprocess
import os
import json
def abc2midi(abcfile,turn):
    
    if abcfile is not None:
        abc_file = Path(abcfile)
            #midiname=turn+f'{abc_file.stem}.mid'
        midiname=f'{abc_file.stem}.mid'
        print("ABC")
        print(abcfile)
        temp=m21.converter.parse(abcfile)
        temp.write('midi', fp=midiname)
        print(midiname)
        return 1
        '''try:
            abc_file = Path(abcfile)
            #midiname=turn+f'{abc_file.stem}.mid'
            midiname=f'{abc_file.stem}.mid'
            print("ABC")
            print(abcfile)
            temp=m21.converter.parse(abcfile)
            temp.write('midi', fp=midiname)
            print(midiname)
            return 1
        except:return'''
    return 0
        

def convert_midi_to_wav(abc_file_path):
    
        midi_file = Path(abc_file_path)  # abc file

    # Convert the ABC file to a MIDI file using abc2midi
  
        tmp_midi = 'Song_data/'+f'{midi_file.stem}.mid'
    # Convert xml to WAV using MuseScore (requires MuseScore installed)
        wav_file = 'Song_data/'+f'{midi_file.stem}.wav'
        subprocess.run(["musescore", "-f", "-o", wav_file, tmp_midi])

        print(f'output wav file: {wav_file}')
        return wav_file
        '''except:
        return None'''
if __name__=='main':
    with open("generated1.json",'rb') as f:
        gen=json.load(f)
    print(len(gen))
    for i in range(len(gen)):
        for k in range(len(gen[i]['response_icl'])+len(gen[i]['response_ori'])+len(gen[i]['response_cot'])+len(gen[i]['response_role'])):
            
                match k%4:
                    case 0:
                        
                        with open("ABC_data/%d/%d.abc"%(i,k),'w',encoding='utf-8') as f:
                            f.write(gen[i]['response_icl'][k//4])
                            f.close()
                        abc2midi("ABC_data/%d/%d.abc"%(i,k),'Song_data/%d/'%(i))
                    case 1:
                        with open("ABC_data/%d/%d.abc"%(i,k),'w',encoding='utf-8') as f:
                            f.write(gen[i]['response_ori'][k//4])
                            f.close()
                        abc2midi("ABC_data/%d/%d.abc"%(i,k),'Song_data/%d/'%(i))
                    case 2:
                        with open("ABC_data/%d/%d.abc"%(i,k),'w',encoding='utf-8') as f:
                            f.write(gen[i]['response_cot'][k//4])
                            f.close()
                        abc2midi("ABC_data/%d/%d.abc"%(i,k),'Song_data/%d/'%(i))
                    case 3:
                        with open("ABC_data/%d/%d.abc"%(i,k),'w',encoding='utf-8') as f:
                            f.write(gen[i]['response_role'][k//4])
                            f.close()
                        abc2midi("ABC_data/%d/%d.abc"%(i,k),'Song_data/%d/'%(i))
                
            

import autogen
import argparse
import random

#OAI_CONFIG_LIST: the json file that contains the api keys

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
         "model": ["gpt-4-1106-preview", "gpt-4-1106", "gpt-4-0314","gpt4","gpt-4-32k","gpt-3.5-turbo"],

    }
)

with open ("prompt.txt","r") as f:
    prompt=f.read()
    f.close()
print(int)
llm_config = {"config_list": config_list, "cache_seed": None}
user_proxy = autogen.UserProxyAgent(
   name="User_proxy",
   system_message="""A human client.




                    """,
   code_execution_config=False,
)


Leader  = autogen.AssistantAgent(
    name = "Leader",
    system_message = """
                     You are the leader of a music production team, which includes Melody Agent, Harmony Agent, Instrument Agent, Reviewer Agent and Arrangement Agent.
                     You will receive the request from the client, which will be a breif desciption of the kind of music they want.
                     You need to carefully analyze the musical elements given in the request, which usually includes the title, genre, key, chord pregression, instruments, tempo, rhythm of the music.
                     After examing the client's request, you are responsible for decomposing it into subtasks, and assign the subtasks to only Melody Agent, Harmony Agent and Instumentation Agent in your team.
                     After the all the composing and reviewing process, you are responsible to output a final, complete and readable ABC notation of the work, markdown the final work using ```    ``` to the client.
                     """,
    llm_config=llm_config,

)



MelodyAgent = autogen.AssistantAgent(
    name="MelodyAgent",
    system_message="""
                    You are skillful musician, especially in melody.
                    You will compose a single-line melody based on the client's request and assigned tasks from the Leader
                    You must output your work in ABC Notations.
                    Here is a template of a music piece in ABC notation,in this template:
                    X:1 is the reference number. You can increment this for each new tune.
                    T:Title is where you'll put the title of your tune.
                    C:Composer is where you'll put the composer's name.
                    M:4/4 sets the meter to 4/4 time, but you can change this as needed.
                    L:1/8 sets the default note length to eighth notes.
                    K:C sets the key to C Major. Change this to match your desired key.
                    The music notation follows, with |: and :| denoting the beginning and end of repeated sections.
                    Markdown your work using ```    ``` to the client.

                    ```
                    X:1
                    T:Title
                    C:Composer
                    M:Meter
                    L:Unit note length
                    K:Key
                    |:GABc d2e2|f2d2 e4|g4 f2e2|d6 z2:|
                    |:c2A2 B2G2|A2F2 G4|E2c2 D2B,2|C6 z2:|


                    ```
                    You will output the melody following this template, but decide the time signature, key signature and the actual musical contents and length yourself.
                    After you receive the feedback from the Reviewer Agent, please improve your work according to the suggestions you were given.
                    """,
    llm_config=llm_config,
)

HarmonyAgent = autogen.AssistantAgent(
    name="HarmonyAgent",
    system_message="""
                    You are skillful musician, especially in harmony and counterpoints
                    You will harmonize the melody composed by Melody Agent, please do not left any unharmonized melody.
                    You will determine the number of voices in the harmony.
                    You must output your work, along with the melody.
                    Here is a template of two-voice music piece in ABC notation,in this template:
                    V:1 denotes the original melody (voice 1).
                    V:2 introduces the harmony part (voice 2), which is designed to complement the melody.
                    Markdown your work using ```    ``` to the client.
                    ```
                    X:1
                    T:Title
                    C:Composer
                    M:Meter
                    L:Unit note length
                    K:Key
                    V:1
                    |:GABc d2e2|f2d2 e4|g4 f2e2|d6 z2:|
                    |:c2A2 B2G2|A2F2 G4|E2c2 D2B,2|C6 z2:|
                    V:2
                    |:E2F2 G4|A2G2 F4|E4 D2C2|C6 z2:|
                    |:G,2E2 F2D2|E2C2 D4|B,2G2 A2F2|C6 z2:|
                    V:3
                    V:4

                    ```
                    You will output the harmonized piece following the same manner, but determine the number of voices and actual harmony yourself.
                    After you receive the feedback from the Reviewer Agent, please imporove your work according to the suggestions you were given.
 """,
    llm_config=llm_config,
)

InstrumentAgent = autogen.AssistantAgent(
    name = "InstrumentAgent",
    system_message="""
                   You are a skillful musician, especially in instrumentation.
                   For each vocing given by the Harmony Agent, you will decide with instrument to use for each voice.
                   Pick MIDI Program number using %%MIDI program with desired channel and midi program number for each corresponding instrument.
                   For some instruments that are not in the General MIDI standard, choose the closest match which is availabe in the General MIDI standard.
                   You must assign midi program number to every voice.
                   You need to make sure each voice and instrument is in appropiate musical range
                   Here is a template of a music piece with instrumentation in ABC notation:
                   Markdown your work using ```    ``` to the client.
                    ```
                    X:1
                    T:Title
                    C:Composer
                    M:Meter
                    L:Unit note length
                    K:Key
                    V:1 name="Guitar" clef=treble
                    %%MIDI program 1 24 (Guitar for melody)
                    |:GABc d2e2|f2d2 e4|g4 f2e2|d6 z2:|
                    |:c2A2 B2G2|A2F2 G4|E2c2 D2B,2|C6 z2:|
                    V:2 name="Clarinet" clef=treble
                    %%MIDI program 2 71 (Clarinet for harmony)
                    |:E2F2 G4|A2G2 F4|E4 D2C2|C6 z2:|
                    |:G,2E2 F2D2|E2C2 D4|B,2G2 A2F2|C6 z2:|

                    ```
                   You will output the intrumented piece in the same manner, but determine the instruments according to the given context yourself.
                   After you receive the feedback from the reviewer agent, please modify your work according to the suggestions you were given.

    """,
     llm_config=llm_config,



)

ArrangementAgent = autogen.AssistantAgent(
    name = "ArrangementAgent",
    system_message="""
                  You are an expert in writing ABC Notations.
                  You will be given with the a rough musical draft of ABC notation collaboratively written by the Melody Agent, Harmony Agent, and Instrument Agent.
                  The format of this rough draft might not follow the rules of ABC notations.
                  Your are responsible for re-format the draft into standard ABC notation form.
                  Make sure to delete all the empty lines, especially empty lines between each voice. 
                  Make sure the information about the instruments and the voices are correctly presented, using format like V:1, V:2, etc for each voice, and %%MIDI program for corresponding instruments under each voice.
                  Markdown your work using ```    ``` to the client.




    """,
    llm_config=llm_config,



)

ReviewerAgent = autogen.AssistantAgent(
    name = "ReviewerAgent",
    system_message="""
                    You are a skillful musician, you are expertized in music theory.
                    You need to be very strict and critical about their work.
                    You will check the entire work and provide constructive critics.
                    You will critize on each agent's performance so they can improve the quality of their work.
                    The agents are accessed based on:
                    Melodic Structure: Assess the flow, thematic development, and variety in pitch and rhythm.
                    Harmony and Counterpoint: Check how harmonies support the melody, effectiveness of counterpoint, and chord progressions.
                    Rhythmic Complexity: Evaluate the rhythm's contribution to interest, its interaction with the melody, and dynamic changes.
                    Instrumentation and Timbre: Look at the appropriateness of instruments, blending of timbres, and use of dynamics.
                    Form and Structure: Analyze the overall structure, transitions, and how sections are connected and concluded.


                   """,
    llm_config=llm_config,


)
groupchat = autogen.GroupChat(agents=[user_proxy,Leader, MelodyAgent, HarmonyAgent,InstrumentAgent,ArrangementAgent, ReviewerAgent], messages=[], max_round=12)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config,human_input_mode=None)
user_proxy.initiate_chat(manager, message= prompt
)

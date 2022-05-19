from fastapi import FastAPI
import soundfile as sf  # you can use other audio load packages.
from helper import wsola
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from math import log

# We define the FastApi module

app = FastAPI()

###### This part is needed in order to connect with the frontend #####
 
origins = [
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

###### this is like the songs database #####

# This part must migrate to a real database in furter improvements

songs_names = [
    {
    "id": 1,
    "path": "daniela_andrade",
    "title": "Crazy Daniela Andrade",
    "image_path": "https://i.scdn.co/image/ab67616d00001e0229455064ffc25216a8a576b2",
    "bpm": 99,
  },
  {
    "id": 2,
    "path": "Gnarls-Barkley-Crazy_cortado",
    "title": "Crazy Gnarls Barkley",
    "image_path": "https://m.media-amazon.com/images/I/81mWl+Yr5nL._SS500_.jpg",
    "bpm": 112,
  },
  {
    "id": 2,
    "path": "starwars",
    "title": "Star Wars",
    "image_path": "https://images.unsplash.com/photo-1618336753974-aae8e04506aa?crop=entropy&cs=tinysrgb&fm=jpg&ixlib=rb-1.2.1&q=80&raw_url=true&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1170",
    "bpm": 99,
  },
  {
    "id": 4,
    "path": "goingup60_mono",
    "title": "Going Up",
    "image_path": "https://images.unsplash.com/photo-1557177324-56c542165309?ixlib=rb-1.2.1&auto=format&fit=crop&w=1950&q=80",
    "bpm": 116,
  }
]

######## Endpoints ########

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/songs")
def get_songs():
    return songs_names

@app.get("/mix")
def get_mix(song_1: str, song_2: str, f_second: int, time_to_switch: int, attenuation: int):

    # This part is to load the audio files

    x, sr = sf.read(song_1 + '.wav')
    a, sr_a = sf.read(song_2 + '.wav')

    bpm_1 = 0
    bpm_2 = 0

    for song in songs_names:
        if(song["path"] == song_1):
            bpm_1 = song["bpm"]
        elif(song["path"] == song_2):
            bpm_2 = song["bpm"]
        
    if bpm_1 == 0 or bpm_2 == 0:
        return {"error": "At least one of the songs is not in the database"}
    # print(f_second)
    # print(time_to_switch)

    x = x.T
    x_length = x.shape[-1]  # length of the audio sequence x.

    first_second = f_second # First second of the switching part
    # time_to_switch = time in the song switch
    samples_to_switch = time_to_switch*sr # number of samples in the switch
    target_s = bpm_1/bpm_2 # BPMs relationship (BPM1/BPM2)
    step = 1*sr # Number of samples to change the speed
    veces_de_reduccion = attenuation # attenuation in the switch (is the number of times the song is reduced at the end throw a logaritmic function)
    
    # This part is to calculate some helper variables to the logaritmic function
    logaritm = log(veces_de_reduccion) / log(2)
    pendiente_del_log = logaritm/samples_to_switch

    # print(pendiente_del_log)

    # This part is to calculate the number of changes of speed in the switching part
    number_of_changes = int(samples_to_switch / step)
    # print(number_of_changes)

    ###### Here we separate the son in parts accordingly with the number of changes in the switch ######

    y = [] # array of arrays with the parts of the song 

    y.append(x[0:first_second*sr])
    for i in range(number_of_changes):
        y.append(x[first_second*sr+i*step:first_second*sr+(i+1)*step])

    #y.append(x[first_second*sr+number_of_changes*step:x_length])

    # print(len(y))

    ###### Here we calculate the factor of speed for every part of the song in the switching part ######

    # first we calculate the speed_step
    speed_step = (1-target_s) / number_of_changes
    # print(speed_step)

    speeds=[] # array of the speeds for every part of the song in the switching part

    for i in range(number_of_changes+1):
        speeds.append(1-i*speed_step)

    speeds.append(1)

    ##### Here we calculate the output of the wsola function for every song part in the switch with the correspondent speed factor #####

    z = []

    z.append(y[0])

    for i in range(number_of_changes):
        z.append(wsola(y[i+1], speeds[i+1]))

    #z.append(y[number_of_changes+1])
    # print(len(z))

    ##### Here we concatenate every part of the modified song ######

    output = []

    output = np.concatenate((output, z[0]))

    for i in range(number_of_changes):
        output = np.concatenate((output, z[i+1]))

    #output = np.concatenate((output, z[number_of_changes+1]))

    ##### Here we calculate the attenuation for every part of the song in the switch ######

    for i in range(len(output)- len(z[0])):
        output[i+first_second*sr] = output[i+first_second*sr] / (2**(i*pendiente_del_log)) + a[i] / (2**(
                (samples_to_switch-i)*pendiente_del_log))
    # print(len(output))
    # print(len(a))
    # print(len(x))
    # for i in range(900000):
    #     output[first_second*sr + samples_to_switch + i + 1] = a[samples_to_switch + i]
    output = np.concatenate((output, a[len(output)- len(z[0]):]))

    ##### Here we write the correspondent file and return a message to indicate that every works fine ######

    sf.write("../frontend/public/results.wav", output, sr)

    return {"song1": song_1, "song2": song_2, "f_second": f_second, "time_to_switch": time_to_switch, "attenuation": attenuation}




from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pytsmod as tsm
import soundfile as sf  # you can use other audio load packages.
import os

from fastapi.middleware.cors import CORSMiddleware

# import numpy as np
from scipy.interpolate import interp1d
# from .utils import win as win_func
# from .utils import _validate_audio, _validate_scale_factor

from math import log

origins = [
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

songs_names = [
    {
        "id": 1,
        "name": "star wars",
        "path": "starwars.wav"
    },
    {
        "id": 2,
        "name": "Crazy daniela andrade",
        "path": "daniela_andrade.wav"
    },
    {
        "id": 3,
        "name": "Crazy Gnarls Barkley",
        "path": "Gnarls-Barkley-Crazy_cortado.wav"
    },
    ]


def wsola(x, s, win_type='hann',
          win_size=1024, syn_hop_size=512, tolerance=512):
    """Modify length of the audio sequence using WSOLA algorithm.
    Parameters
    ----------
    x : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the input audio sequence to modify.
    s : number > 0 [scalar] or numpy.ndarray [shape=(2, num_points)]
        the time stretching factor. Either a constant value (alpha)
        or an 2 x n array of anchor points which contains the sample points
        of the input signal in the first row
        and the sample points of the output signal in the second row.
    win_type : str
               type of the window function. hann and sin are available.
    win_size : int > 0 [scalar]
               size of the window function.
    syn_hop_size : int > 0 [scalar]
                   hop size of the synthesis window.
                   Usually half of the window size.
    tolerance : int >= 0 [scalar]
                number of samples the window positions
                in the input signal may be shifted
                to avoid phase discontinuities when overlap-adding them
                to form the output signal (given in samples).
    Returns
    -------
    y : numpy.ndarray [shape=(channel, num_samples) or (num_samples)]
        the modified output audio sequence.
    """
    # validate the input audio and scale factor.
    x = _validate_audio(x)
    anc_points = _validate_scale_factor(x, s)

    n_chan = x.shape[0]
    output_length = int(anc_points[-1, -1]) + 1

    win = wind(win_type=win_type, win_size=win_size, zero_pad=0)

    sw_pos = np.arange(0, output_length + win_size // 2, syn_hop_size)
    ana_interpolated = interp1d(anc_points[1, :], anc_points[0, :],
                                fill_value='extrapolate')
    aw_pos = np.round(ana_interpolated(sw_pos)).astype(int)
    ana_hop = np.insert(aw_pos[1:] - aw_pos[0: -1], 0, 0)

    y = np.zeros((n_chan, output_length))

    min_fac = np.min(syn_hop_size / ana_hop[1:])

    # padding the input audio sequence.
    left_pad = int(win_size // 2 + tolerance)
    right_pad = int(np.ceil(1 / min_fac) * win_size + tolerance)
    x_padded = np.pad(x, ((0, 0), (left_pad, right_pad)), 'constant')

    aw_pos = aw_pos + tolerance

    # Applying WSOLA to each channels
    for c, x_chan in enumerate(x_padded):
        y_chan = np.zeros(output_length + 2 * win_size)
        ow = np.zeros(output_length + 2 * win_size)

        delta = 0

        for i in range(len(aw_pos) - 1):
            x_adj = x_chan[aw_pos[i] + delta: aw_pos[i] + win_size + delta]
            y_chan[sw_pos[i]: sw_pos[i] + win_size] += x_adj * win
            ow[sw_pos[i]: sw_pos[i] + win_size] += win

            nat_prog = x_chan[aw_pos[i] + delta + syn_hop_size:
                              aw_pos[i] + delta + syn_hop_size + win_size]

            next_aw_range = np.arange(aw_pos[i+1] - tolerance,
                                      aw_pos[i+1] + win_size + tolerance)

            x_next = x_chan[next_aw_range]

            cross_corr = np.correlate(nat_prog, x_next)
            max_index = np.argmax(cross_corr)

            delta = tolerance - max_index

        # Calculate last frame
        x_adj = x_chan[aw_pos[-1] + delta: aw_pos[-1] + win_size + delta]
        y_chan[sw_pos[-1]: sw_pos[-1] + win_size] += x_adj * win
        ow[sw_pos[-1]: sw_pos[-1] + win_size] += + win

        ow[ow < 1e-3] = 1

        y_chan = y_chan / ow
        y_chan = y_chan[win_size // 2:]
        y_chan = y_chan[: output_length]

        y[c, :] = y_chan

    return y.squeeze()


def wind(win_type='hann', win_size=4096, zero_pad=0):
    """Generate diverse type of window function
    Parameters
    ----------
    win_type : str
               the type of window function.
               Currently, Hann and Sin are supported.
    win_size : int > 0 [scalar]
               the size of window function.
               It doesn't contains the length of zero padding.
    zero_pad : int > 0 [scalar]
               the total length of zero-pad.
               Zeros are equally distributed
               for both left and right of the window.
    Returns
    -------
    win : numpy.ndarray([shape=(win_size)])
          the window function generated.
    """

    if win_type == 'hann':
        win = np.hanning(win_size)
    elif win_type == 'sin':
        win = np.sin(np.pi * np.arange(win_size) / (win_size - 1))
    else:
        raise Exception("Please use the valid window type. (hann, sin)")

    win = np.pad(win, zero_pad // 2, 'constant')

    return win


def _validate_audio(audio):
    """validate the input audio and modify the order of channels.
    Parameters
    ----------
    audio : numpy.ndarray [shape=(channel, num_samples) or (num_samples)\
                           or (num_samples, channel)]
            the input audio sequence to validate.
    Returns
    -------
    audio : numpy.ndarray [shape=(channel, num_samples)]
            the validataed output audio sequence.
    """
    if audio.ndim == 1:
        audio = np.expand_dims(audio, 0)
    elif audio.ndim > 2:
        raise Exception("Please use the valid audio source. "
                        + "Number of dimension of input should be less than 3.")
    elif audio.shape[0] > audio.shape[1]:
        warn('it seems that the 2nd axis of the input audio source '
             + 'is a channel. it is recommended that fix channel '
             + 'to the 1st axis.', stacklevel=3)
        audio = audio.T

    return audio


def _validate_scale_factor(audio, s):
    """Validate the scale factor s and
    convert the fixed scale factor to anchor points.
    Parameters
    ----------
    audio : numpy.ndarray [shape=(num_channels, num_samples) \
                           or (num_samples) or (num_samples, num_channels)]
            the input audio sequence.
    s : number > 0 [scalar] or numpy.ndarray [shape=(2, num_points) \
        or (num_points, 2)]
        the time stretching factor. Either a constant value (alpha)
        or an (2 x n) (or (n x 2)) array of anchor points
        which contains the sample points of the input signal in the first row
        and the sample points of the output signal in the second row.
    Returns
    -------
    anc_points : numpy.ndarray [shape=(2, num_points)]
                 anchor points which contains the sample points
                 of the input signal in the first row
                 and the sample points of the output signal in the second row.
    """
    if np.isscalar(s):
        anc_points = np.array([[0, np.shape(audio)[1] - 1],
                               [0, np.ceil(s * np.shape(audio)[1]) - 1]])
    elif s.ndim == 2:
        if s.shape[0] == 2:
            anc_points = s
        elif s.shape[1] == 2:
            warn('it seems that the anchor points '
                 + 'has shape (num_points, 2). '
                 + 'it is recommended to '
                 + 'have shape (2, num_points).', stacklevel=3)
            anc_points = s.T
    else:
        raise Exception('Please use the valid anchor points. '
                        + '(scalar or pair of input/output sample points)')

    return anc_points


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/songs")
def get_songs():
    return songs_names

@app.get("/mix")
def get_mix(song_1: str, song_2: str, f_second: int, time_to_switch: int, attenuation: int):
    x, sr = sf.read(song_1 + '.wav') # daniela_andrade.wav
    a, sr_a = sf.read(song_2 + '.wav') # Gnarls-Barkley-Crazy_cortado.wav


    print(f_second)
    print(time_to_switch)

    x = x.T
    x_length = x.shape[-1]  # length of the audio sequence x.

    first_second = f_second #  25 Segundo donde empieza a cambiar
    # time_to_switch = 6 # tiempo que tarda en cambiar
    samples_to_switch = time_to_switch*sr
    # number_of_changes = 7 # numero de cambios en velocidad que performea
    target_s = 0.68 # valor de velocidad buscado
    step = 1*sr # numero de samples luego de los cuales se realiza un cambio de velocidad
    veces_de_reducción = attenuation # 64.0
    logaritm = log(veces_de_reducción) / log(2)

    pendiente_del_log = logaritm/samples_to_switch

    print(pendiente_del_log)

    number_of_changes = int(samples_to_switch / step)
    print(number_of_changes)

    y = [] # vector con vectores correspondientes a las separaciones

    y.append(x[0:first_second*sr])
    for i in range(number_of_changes):
        y.append(x[first_second*sr+i*step:first_second*sr+(i+1)*step])

    y.append(x[first_second*sr+number_of_changes*step:x_length])

    print(len(y))

    speed_step = (1-target_s) / number_of_changes
    print(speed_step)

    speeds=[]

    for i in range(number_of_changes+1):
        speeds.append(1-i*speed_step)

    speeds.append(1)

    z = []

    z.append(y[0])

    for i in range(number_of_changes):
        z.append(wsola(y[i+1], speeds[i+1]))

    z.append(y[number_of_changes+1])
    print(len(z))

    output = []

    output = np.concatenate((output, z[0]))

    for i in range(number_of_changes):
        output = np.concatenate((output, z[i+1]))

    output = np.concatenate((output, z[number_of_changes+1]))

    for i in range(samples_to_switch):
        output[i+first_second*sr] = output[i+first_second*sr] / (2**(i*pendiente_del_log)) + a[i] / (2**(
                (samples_to_switch-i)*pendiente_del_log))
    # print(len(output))
    # print(len(a))
    # print(len(x))
    for i in range(900000):
        output[first_second*sr + samples_to_switch + i + 1] = a[samples_to_switch + i]



    sf.write("../frontend/public/results.wav", output, sr)

    return {"song1": song_1, "song2": song_2, "f_second": f_second, "time_to_switch": time_to_switch, "attenuation": attenuation}




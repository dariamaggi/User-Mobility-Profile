import os

import pyaudio
import wave
import socket  # Import socket module
import logging
import time
import pathlib

form_1 = pyaudio.paInt16  # 16-bit resolution
chans = 1  # 1 channel
samp_rate = 44100  # 44.1kHz sampling rate
chunk = 4096  # 2^12 samples per buffer
record_secs = 3  # secondi di registrazione
dev_index = 2  # QUI VA INDICE DEL DISPOSITIVO AUDIO ottenunuto dalla p.get_device_info_by_index(ii) nel 3 comando
wav_output_filename = 'audio_recorded.wav'  # nome del file formato .wav



def get_audio():
    audio = pyaudio.PyAudio()  # istanza pyaudio
    while 1 == 1:
        time.sleep(10)
        # create pyaudio stream
        stream = audio.open(format=form_1, rate=samp_rate, channels=chans,
                            input_device_index=dev_index, input=True,
                            frames_per_buffer=chunk)

        logging.info('Recorging....')
        frames = []

        # loop through stream and append audio chunks to frame array
        for ii in range(0, int((samp_rate / chunk) * record_secs)):
            data = stream.read(chunk)
            frames.append(data)

        logging.info('finished recording')

        # stop the stream, close it, and terminate the pyaudio instantiation
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # save the audio frames as .wav file
        wavefile = wave.open(os.path.join(pathlib.Path(__file__), 'song.png'), 'wb')
        wavefile.setnchannels(chans)
        wavefile.setsampwidth(audio.get_sample_size(form_1))
        wavefile.setframerate(samp_rate)
        wavefile.writeframes(b''.join(frames))
        wavefile.close()



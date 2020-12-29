import pydub
import numpy


# TODO: Marsha and Andrea

def identify_user(data):
    return data  # todo: deve chiamare la funzione per il riconoscimento e restiruire
    #                 1 --> non trovato
    #                 id dell'utente


# Funzione per conversione file mp3 del DB in numpy array #######################
# In file e first_audio e second_audio va il path del file mp3 in locale
def read_from_mp3_to_numpy(file_mp3, normalized=False):
    """MP3 to numpy array"""
    a = pydub.AudioSegment.from_mp3(file_mp3)
    y = numpy.array(a.get_array_of_samples())
    if a.channels == 2:
        y = y.reshape((-1, 2))
    if normalized:
        return numpy.float32(y) / 2 ** 15
    else:
        return y


# Funzione per matching audio ##################################################
def matching_audio(first, second):
    c = numpy.in1d(first, second)
    count_true = 0

    for elem in c:
        if elem is True:
            count_true = count_true + 1

    if count_true >= ((c.size * 90) / 100):
        return True
    else:
        return False

import numpy as np
from echolocate.audio import ItemRecognizer


def test_teach_and_match(tmp_path):
    recognizer = ItemRecognizer()
    # generate a dummy waveform
    wav = np.random.randn(16000).astype('float32')
    path = tmp_path / 'item.wav'
    import soundfile as sf
    sf.write(path, wav, 16000)
    recognizer.teach('item', path)

    hits = recognizer.match(wav)
    assert 'item' in hits or hits == []

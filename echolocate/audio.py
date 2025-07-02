import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
try:
    import sounddevice as sd
except Exception:  # fallback when portaudio is unavailable
    sd = None
import librosa
from sklearn.cluster import KMeans
from fastdtw import fastdtw

from .db import log_event

SAMPLE_RATE = 16000
CHUNK_SECONDS = 5

class RoomFingerprint:
    def __init__(self):
        self.fingerprints: List[np.ndarray] = []
        self.labels: Dict[int, str] = {}
        self.model = None

    def add(self, data: np.ndarray):
        mel = librosa.feature.melspectrogram(y=data, sr=SAMPLE_RATE, n_mels=40)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        self.fingerprints.append(mel_db.mean(axis=1))

    def cluster(self):
        if not self.fingerprints:
            return
        X = np.vstack(self.fingerprints)
        n_clusters = max(1, min(len(self.fingerprints), 5))
        self.model = KMeans(n_clusters=n_clusters, n_init=10)
        self.model.fit(X)

    def label_zone(self, idx: int, name: str):
        self.labels[idx] = name

    def predict(self, data: np.ndarray) -> str:
        if self.model is None:
            return "unknown"
        mel = librosa.feature.melspectrogram(y=data, sr=SAMPLE_RATE, n_mels=40)
        mel_db = librosa.power_to_db(mel, ref=np.max)
        feat = mel_db.mean(axis=1)
        idx = int(self.model.predict([feat])[0])
        return self.labels.get(idx, f"zone_{idx}")

def record_audio(duration: int) -> np.ndarray:
    """Record audio or return random noise if sounddevice is unavailable."""
    if sd is None:
        return np.random.randn(int(duration * SAMPLE_RATE)).astype('float32')
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    return audio.flatten()

class ItemRecognizer:
    def __init__(self):
        self.templates: Dict[str, np.ndarray] = {}

    def teach(self, item: str, path: Path):
        y, _ = librosa.load(path, sr=SAMPLE_RATE)
        mfcc = librosa.feature.mfcc(y=y, sr=SAMPLE_RATE, n_mfcc=20)
        self.templates[item] = mfcc

    def match(self, data: np.ndarray) -> List[str]:
        mfcc = librosa.feature.mfcc(y=data, sr=SAMPLE_RATE, n_mfcc=20)
        hits = []
        for item, tmpl in self.templates.items():
            dist, _ = fastdtw(mfcc.T, tmpl.T)
            if dist < 100:
                hits.append(item)
        return hits

class EchoLocateRunner:
    def __init__(self, recognizer: ItemRecognizer, fingerprint: RoomFingerprint):
        self.recognizer = recognizer
        self.fingerprint = fingerprint
        self.queue = queue.Queue()
        self.running = False
        self.thread = None

    def _worker(self):
        while self.running:
            data = record_audio(CHUNK_SECONDS)
            self.fingerprint.add(data)
            zone = self.fingerprint.predict(data)
            for item in self.recognizer.match(data):
                log_event(item, zone, datetime.utcnow())
            self.queue.put(zone)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

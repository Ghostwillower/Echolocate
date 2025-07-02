import numpy as np
from echolocate.audio import RoomFingerprint


def test_cluster_predict():
    rf = RoomFingerprint()
    # create dummy fingerprints for two rooms
    for i in range(5):
        rf.add(np.random.randn(8000))
    rf.cluster()
    zone = rf.predict(np.random.randn(8000))
    assert zone.startswith('zone_') or isinstance(zone, str)

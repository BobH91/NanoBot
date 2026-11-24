import json
import math
from pathlib import Path


MAP_PATH = Path(__file__).resolve().parents[1] / "maps" / "initial_landmarks.json"


def test_initial_landmark_map():
    data = json.loads(MAP_PATH.read_text())

    assert data["schema_version"] == 1

    frame = data["coordinate_frame"]
    assert frame["axes"]["x"] == "robot right, metres"
    assert frame["axes"]["y"] == "robot forward, metres"
    assert frame["axes"]["z"] == "robot up, metres"

    landmarks = data["landmarks"]
    ids = [item["tag_id"] for item in landmarks]

    assert ids == [0, 1, 2, 3, 4, 5]

    observed = [item for item in landmarks
                if item["status"] == "observed_preliminary"]
    missing = [item for item in landmarks
               if item["status"] == "not_observed"]

    assert [item["tag_id"] for item in observed] == [0, 1, 2, 3]
    assert [item["tag_id"] for item in missing] == [4, 5]

    for item in observed:
        assert item["sample_count"] > 0

        for value in item["position_m"].values():
            assert math.isfinite(value)

        for value in item["population_stddev_m"].values():
            assert math.isfinite(value)
            assert value >= 0

    for item in missing:
        assert item["position_m"] is None
        assert item["sample_count"] == 0


def test_map_records_scan_provenance():
    source = json.loads(MAP_PATH.read_text())["source"]

    assert source["scan_state"] == "done"
    assert source["stops_completed"] == 60
    assert source["detections"] == 33

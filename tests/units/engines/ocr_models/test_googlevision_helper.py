import numpy as np
from optics_framework.engines.vision_models.ocr_models.googlevision import GoogleVisionHelper


def test_find_element_multiword_monkeypatched():
    # create a dummy frame
    frame = np.zeros((100, 200, 3), dtype=np.uint8)

    helper = GoogleVisionHelper(fuzzy_threshold=0.4)

    # monkeypatch detect_text to return two separate words: 'this' and 'image'
    def fake_detect_text(input_frame):
        # return full_text, results
        # bbox format: [(x,y), (x,y), (x,y), (x,y)]
        results = [
            ([(10, 10), (50, 10), (50, 30), (10, 30)], "this", None),
            ([(100, 40), (140, 40), (140, 60), (100, 60)], "image", None),
        ]
        return "this image", results

    helper.detect_text = fake_detect_text

    # sanity check what detect_text returns
    full_text, ocr_results = helper.detect_text(frame)
    assert full_text == "this image"
    assert len(ocr_results) == 2

    # (We accept partial/fuzzy matches; no strict similarity asserted here)

    res = helper.find_element(frame, "this device")
    assert res is not None, "Expected to find 'this device' by combining 'this' + fuzzy 'image'~'device'"
    found, centre, bbox = res
    assert found is True
    assert isinstance(centre, tuple) and len(centre) == 2
    assert isinstance(bbox, tuple) and len(bbox) == 2

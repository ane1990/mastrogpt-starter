import os, requests as req
def test_reverse():
    url = os.environ.get("OPSDEV_HOST") + "/api/my/aanelli/reverse"
    res = req.post(url, {"input": "TEST"}).json()
    assert res.get("output") == "Input Reversed TSET"
    res = req.get(url).json()
    assert res.get("output") == "Please provide some inputs"

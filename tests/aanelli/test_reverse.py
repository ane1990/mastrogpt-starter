import sys 
sys.path.append("packages/aanelli/reverse")
import reverse

def test_reverse():
    res = reverse.reverse({"input": "TEST" })
    assert res["output"] == "Input Reversed TSET"

    res = reverse.reverse({})
    assert res["output"] == "Please provide some inputs"

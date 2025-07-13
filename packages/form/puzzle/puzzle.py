import re, os, requests as req
MODEL = "llama3.1:8b"
#MODEL = "phi4:14b"

FORM = [
  {
      "name": "queen",
      "label": "With a Queen",
      "type": "checkbox",
  },
  {
      "name": "rook",
      "label": "With a Rook",
      "type": "checkbox",
  },
  {
    "name": "knight",
    "label": "With a Knight",
    "type": "checkbox"
  },
  {
    "name": "bishop",
    "label": "With a Bishop",
    "type": "checkbox",
  },
]

def chat(args, inp):
  host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
  auth = args.get("AUTH", os.getenv("AUTH"))
  url = f"https://{auth}@{host}/api/generate"
  msg = { "model": MODEL, "prompt": inp, "stream": False}
  res = req.post(url, json=msg).json()
  out = res.get("response", "error")
  return  out
 
def extract_fen(out):
  pattern = r"([rnbqkpRNBQKP1-8]+\/){7}[rnbqkpRNBQKP1-8]+"
  fen = None
  m = re.search(pattern, out, re.MULTILINE)
  if m:
    fen = m.group(0)
  return fen

def puzzle(args):
  out = "If you want to see a chess puzzle, type 'puzzle'. To display a fen position, type 'fen <fen string>'."
  inp = args.get("input", "")
  res = {}
    
  if type(inp) is dict and "form" in inp:
    data = inp["form"]
    inpTmp = "Generate a chess puzzle in FEN format but with only and all the following figures: "
    for field in data.keys():
      if data[field] == "queen":
        inpTmp += " queen"      
      elif data[field] == "rook":
        inpTmp += " rook"
      elif data[field] == "knight":
        inpTmp += " knight"
      elif data[field] == "bishop":
        inpTmp += " bishop"
    out = chat(args, inpTmp)
    fen = extract_fen(out)
    print(out, fen)
    if fen:
      res['chess'] = fen
    res["output"] = out
    return res
  if inp == "2":
    inp = "generate a chess puzzle in FEN format"
    out = chat(args, inp)
    fen = extract_fen(out)
    if fen:
       print(fen)
       res['chess'] = fen
    else:
      out = "Bad FEN position."
  elif inp.startswith("fen"):
    fen = extract_fen(inp)
    if fen:
       out = "Here you go."
       res['chess'] = fen
  elif inp == "puzzle-form":
     out = "Select from the Form the puzzle character"
     res['form'] = FORM
  elif inp != "":
    out = chat(args, inp)
    fen = extract_fen(out)
    print(out, fen)
    if fen:
      res['chess'] = fen

  res["output"] = out
  return res

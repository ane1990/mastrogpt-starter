import os, requests as req
import vision2 as vision
import bucket, base64, time

USAGE = "Please upload a picture and I will tell you what I see"
FORM = [
  {
    "label": "Load Image",
    "name": "pic",
    "required": "true",
    "type": "file"
  },
]

def form(args):
  res = {}
  out = USAGE
  inp = args.get("input", "")
  #E5.1
  buc = bucket.Bucket(args)
  #END:E5.1

  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    vis = vision.Vision(args)
    out = vis.decode(img)
    img_data = img
    content = base64.b64decode(img_data)
    unix_timestamp = int(time.time())
    key = f"upload/{unix_timestamp}"
    if type(content) is bytes:
      upload = buc.write(key, content)
    print(f"The file with key {key} is uploaded {'OK' if upload == 'OK' else 'ERROR'}")

    if  buc.size(key) != -1:
      res['html'] = f'<img src="{buc.exturl(key, 3600)}">'
    else:
      res['html'] = f'<img src="data:image/png;base64,{img}">'
    

  res['form'] = FORM
  res['output'] = out
  return res

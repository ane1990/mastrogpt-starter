import vdb,bucket,vision
#TODO: refactor this import to use a common library
import datetime, base64
FORM = [
  {
    "label": "Load the Image",
    "name": "pic",
    "required": "false",
    "type": "file"
  }
]

USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB. 
Use the command `IMG` to use the Uploa Image FORM and insert the image in the DB.
Use `@[<coll>]` to select/create a collection and show the collections.
Use `*<string>` to vector search the <string>  in the DB.
Use `#<limit>`  to change the limit of searches.
Use `!<substr>` to remove text with `<substr>` in collection.
Use `!![<collection>]` to remove `<collection>` (default current) and switch to default.
"""

def loader(args):
  #print(args)
  # get state: <collection>[:<limit>]
  collection = "default"
  limit = 30
  sp = args.get("state", "").split(":")
  if len(sp) > 0 and len(sp[0]) > 0:
    collection = sp[0]
  if len(sp) > 1:
    try:
      limit = int(sp[1])
    except: pass
  print(collection, limit)
  result = {}
  out = f"{USAGE}Current collection is {collection} with limit {limit}"
  result['output'] = out
  result['html'] = ""
  db = vdb.VectorDB(args, collection)
  buc = bucket.Bucket(args)
  inp = args.get('input', "")
  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    ct = datetime.datetime.now()
    key = ct.strftime('%Y%m%d%H%M%S')
    keyToStore = "ragUpload/"+key
    content = base64.b64decode(img)
    if type(content) is bytes and key != "":
      upload = buc.write(keyToStore, content)
      if upload == "OK":
          vis = vision.Vision(args)
          imgText = vis.decode(img)
          print(f'Image described by `{imgText}` for the key {keyToStore}')
          db.insert(imgText, keyToStore)
          result['output'] = f'Image {keyToStore} described by Vision as `{imgText}` successully uploaded'
          result['html'] = f'<img src="{buc.exturl(keyToStore, 3600)}">'
          result['state'] = args.get("state", "")
          return result
      else:
          result['output'] = "Upload of the Image not successfull"
          result['state'] = args.get("state", "")
          return result
  else:
    inp = str(args.get('input', ""))
    # select collection
    if inp == 'IMG':
      result['form'] = FORM
      result['state'] = args.get("state", "")
      return result;
    if inp.startswith("@"):
      out = ""
      if len(inp) > 1:
        collection = inp[1:]
        out = f"Switched to {collection}.\n"
      out += db.setup(collection)
    # set size of search
    elif inp.startswith("#"):
      try: 
        limit = int(inp[1:])
      except: pass
      out = f"Search limit is now {limit}.\n"
    # run a query
    elif inp.startswith("*"):
      search = inp[1:]
      if search == "":
        search = " "
      res = db.vector_search(search, limit=limit)
      if len(res) > 0:
        out = f"Found:\n"
        for i in res:
          out += f"({i[0]:.2f}) {i[1]}"
          if i[2] is not None and i[2] != "": 
            out += f" Image s3ImageKey: {i[2]}\n"
            result['html']+= f'<img src="{buc.exturl(i[2], 3600)}">'
          else:
            out += "\n"
      else:
        out = "Not found"
    # remove a collection
    elif inp.startswith("!!"):
      if len(inp) > 2:
        collection = inp[2:].strip()
      out = db.destroy(collection)
      collection = "default"
    # remove content
    elif inp.startswith("!"):
      count = db.remove_by_substring(inp[1:])
      out = f"Deleted {count} records."    
    elif inp != '':
      out = "Inserted "
      lines = [inp]
      if args.get("options","") == "splitlines":
        lines = inp.split("\n")
      for line in lines:
        if line == '': continue
        res = db.insert(line)
        out += "\n".join([str(x) for x in res.get("ids", [])])
        out += "\n"
  
  result['output'] = out
  result['state'] = f"{collection}:{limit}"
  return result
  

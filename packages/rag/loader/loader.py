import vdb
#TODO: refactor this import to use a common library
import bucket, base64
FORM = [
  {
    "label": "Load the Image",
    "name": "pic",
    "required": "false",
    "type": "file"
  },
  {
    "label": "FileName / Key for the image",
    "name": "filename",
    "type": "text",
    "required": "false"
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

  out = f"{USAGE}Current collection is {collection} with limit {limit}"
  db = vdb.VectorDB(args, collection)
  inp = args.get('input', "")
  if type(inp) is dict and "form" in inp:
    img = inp.get("form", {}).get("pic", "")
    key = inp.get("form", {}).get("filename", "")
    content = base64.b64decode(img)
    buc = None
    if type(content) is bytes and key is not "":
      buc = bucket.Bucket(args)
      upload = buc.write(key, content)
      if upload == "OK":
        db.insert("visualImg", buc.exturl(key, 3600)) #TODO: manage retrieving the extUrl from the key stored in s3 ... the url will expire otherwise...
    return {"output": inp, "html": f'<img src="{buc.exturl(key, 3600)}">'}
  else:
    inp = str(args.get('input', ""))

  # select collection
  if inp == 'IMG':
    return {"output": out, "form": FORM}
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
        out += f"({i[0]:.2f}) {i[1]}\n"
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

  return {"output": out, "state": f"{collection}:{limit}"}
  

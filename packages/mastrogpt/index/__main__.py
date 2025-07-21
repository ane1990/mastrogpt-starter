#--kind python:default
#--web true
#--param OPSDEV_USERNAME $OPSDEV_USERNAME
#--param OPSDEV_HOST $OPSDEV_HOST
#--param OPSDEV_APIHOST $OPSDEV_APIHOST


import os, json
from pathlib import Path
from urllib.parse import urlparse, urlunparse

def main(args):  
  services = {}    
  current_dir = os.path.dirname(os.path.abspath(__file__))
  files = os.listdir(current_dir)
  files.sort()
  for file in files:
    #file = files[1]
    if not file.endswith(".json"):
      continue
    
    entry = file.rsplit(".", maxsplit=1)[0].split("-", maxsplit=1)[-1]
    if not entry in services:
      services[entry] = []
    dict = json.loads(Path(file).read_text())
    for key in dict:
      services[entry].append(key)
    
  username = args.get("OPSDEV_USERNAME", os.getenv("OPSDEV_USERNAME", ""))
  host = args.get("OPSDEV_HOST", os.getenv("OPSDEV_HOST", ""))
  apihost = args.get("OPSDEV_APIHOST", os.getenv("OPSDEV_APIHOST", ""))
  
  url = urlparse(apihost)
  s3_host = urlunparse(url._replace(netloc="s3."+url.netloc))
  stream_host = urlunparse(url._replace(netloc="stream."+url.netloc))

  res = {
    "username": username,
    "host": host,
    "apihost": apihost,
    "s3": s3_host,
    "streamer": stream_host,
    "services": services
  }
  return { "body":  res } 
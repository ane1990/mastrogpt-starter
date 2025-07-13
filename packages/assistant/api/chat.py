import os
import openai

MODEL = "llama3.1:8b"
ROLE = "system:You are an helpful assistant."

#:E4.1 add the stream function
#fix it to extract line.choices[0].delta.content
import json, socket, traceback
def stream(args, lines):
  print("Start Streaming!!")
  sock = args.get("STREAM_HOST")
  port = int(args.get("STREAM_PORT"))
  print(f"sock {sock} and port {port}")

  out = ""
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((sock, port))
    print(f"Connected to the socket, lines {lines}")

    try:
      for line in lines:
        print(f"Loop in line : {line}")
        dec = line.choices[0].delta.content
        msg = {"output": dec}
        out += dec
        s.sendall(json.dumps(msg).encode("utf-8"))
    except Exception as e:
      traceback.print_exc(e)
      out = str(e)
  return out
#END:E4.1

class Chat:
    def __init__(self, args):
        
        host = args.get("OLLAMA_HOST", os.getenv("OLLAMA_HOST"))
        api_key = args.get("AUTH", os.getenv("AUTH"))
        base_url = f"https://{api_key}@{host}/v1"
        
        self.client = openai.OpenAI(
            base_url = base_url,
            api_key = api_key,
        )
        
        self.messages = []
        self.add(ROLE)
        
        #:E4.1 
        # save args in a field
        self.args = args
        #END:E4.1
        
    def add(self, msg):
        [role, content] = msg.split(":", maxsplit=1)
        self.messages.append({
            "role": role,
            "content": content,
        })
    
    def complete(self):
        #:E4.1 
        # add stream: True
        res = self.client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            stream=True
        )
        # END:E4.1
        try: 
            #:E4.1 stream the result 
            out = stream(self.args, res)
            #END:E4.1
            self.add(f"assistant:{out}")
        except:
            out =  "error"
        return out
    

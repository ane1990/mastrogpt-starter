import chat, history

def stateful(args):
  
  inp = args.get("input", "")
  out = f"Hello from {chat.MODEL}"
  res = {}
  
  if inp != "":
    # load the history in the chat
    ch = chat.Chat(args)
    
    #E4.2 load the history
    hi = history.History(args)
    hi.load(ch)
    # END:E4.2
    
    # add a message and save it 
    msg = f"user:{inp}"
    ch.add(msg)
    print(ch.messages)
    out = ch.complete()
    
    # complete, save the assistant and return the id
    #E4.2 save the message and the state
    # return the id as state field in the response
    assistant_msg = f"assistant:{out}"
    ch.add(assistant_msg)
    state_id = hi.save(assistant_msg)
    res['state'] = state_id
    # END:E4.2

  res['output'] = out
  return res
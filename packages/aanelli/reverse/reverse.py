def reverse(args):
  inp = args.get("input")
  out = "Please provide some inputs"
  if inp != None and inp != "":
    out = inp[::-1]
    out = reverse_string(inp)
    return { "output": "Input Reversed " + out }
  else:
    return { "output": out }

def reverse_string(input_str):
    return input_str[::-1]

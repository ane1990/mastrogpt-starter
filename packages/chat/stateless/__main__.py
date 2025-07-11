#--kind python:default
#--web true
#:E2.1
#--param OLLAMA_HOST $OLLAMA_HOST
#--param AUTH $AUTH
#END :E2.1

import stateless
def main(args):
  return { "body": stateless.stateless(args) }

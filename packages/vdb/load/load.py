import re
import requests
from bs4 import BeautifulSoup

import vdb

USAGE = f"""Welcome to the Vector DB Loader.
Write text to insert in the DB.
Start with * to do a vector search in the DB.
Start with ! to remove text with a substring.
"""

# --- helpers ---------------------------------------------------------------
_sent_end = re.compile(r"(?<=[.!?])\s+")

def _split_into_sentences(text: str):
    """Return a list of sentences (whitespace stripped)."""
    return [s.strip() for s in _sent_end.split(text) if s.strip()]

def _chunks(iterable, size):
    """Yield successive `size`-sized chunks from iterable."""
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]

def tokenize(text):
    tokens = text.split()

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', token):
            pass
        elif re.match(r"\w+'s", token):
            token = re.sub(r"(\w+)'s", r"\1 's", token)
        elif re.match(r"\w+'\w+", token):
            token = token.replace("'", "")
        elif re.match(r"\w+-\w+", token):
            pass
        elif re.match(r"\d+(,\d+)*", token):
            pass
        else:
            token = re.sub(r"([^\w\s]+)", r" \1 ", token)

        token = re.sub(r"(\w+)\.", r"\1", token)
        token = re.sub(r"(\w+),", r"\1", token)
        token = re.sub(r"U\.S\.A\.", r"U.S.A.", token)

        tokens[i] = token
        i += 1

    return tokens

def load(args):
    collection = args.get("COLLECTION", "default")
    out = f"{USAGE}Current collection is {collection}"
    inp = str(args.get('input', ""))
    db = vdb.VectorDB(args)

    if inp.startswith("https://"):
        try:
            page = requests.get(inp, timeout=10)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            raw_text = soup.get_text(separator=" ", strip=True)

            # --- limit every sentence to 4096 chars ---
            limited = []
            for sent in _split_into_sentences(raw_text):
                if len(sent) > 4096:
                    # carve the sentence into 4096-char blocks
                    for chunk in _chunks(sent, 4096):
                        limited.append(chunk)
                else:
                    limited.append(sent)

            # tokenize & insert each chunk
            ids = []
            for chunk in limited:
                tokens = tokenize(chunk)
                clean = " ".join(tokens)
                res = db.insert(clean)
                ids.extend(res.get("ids", []))

            out = f"Inserted {' '.join(map(str, ids))}"
        except Exception as e:
            out = f"Error retrieving/processing URL: {e}"
    elif inp.startswith("*"):
        if len(inp) == 1:
            out = "please specify a search string"
        else:
            res = db.vector_search(inp[1:])
            if len(res) > 0:
                out = f"Found:\n"
                for i in res:
                    out += f"({i[0]:.2f}) {i[1]}\n"
            else:
                out = "Not found"
    elif inp.startswith("!"):
        count = db.remove_by_substring(inp[1:])
        out = f"Deleted {count} records."
    elif inp == 'clean-collections':
        db.setup(drop=True)
    elif inp != '':
        res = db.insert(inp)
        out = "Inserted "
        out += " ".join([str(x) for x in res.get("ids", [])])

    return {"output": out}
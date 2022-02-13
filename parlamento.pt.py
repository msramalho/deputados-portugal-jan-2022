import requests, json
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys

parlamento = "https://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID="
filename = "organised/parlamento.pt.json"

def update_file():
    with open(filename, "w") as outf:
        outf.write(json.dumps(name_to_id, indent=4, sort_keys=True, ensure_ascii=False))
        

try:
    with open(filename) as inf:
        name_to_id = json.loads(inf.read())
except: name_to_id = {}


START_FROM = max(name_to_id.values()) + 1
if len(sys.argv) >= 2: # START_FROM override
    START_FROM = int(sys.argv[1]) # needs to be a number

print(f"starting from: {START_FROM}")
for i in tqdm(range(START_FROM, 10_000)):
    r = requests.get(parlamento + str(i))
    html = BeautifulSoup(r.content, 'html.parser')
    try:
        name = html.select_one(".col-xs-12:nth-child(1) .TextoRegular").getText().strip()
        name_to_id[name] = i
        update_file()
    except: continue

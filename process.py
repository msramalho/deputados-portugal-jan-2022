import json
from collections import defaultdict
from os import listdir, mkdir
from os.path import isfile, join, exists

# CNE has errors...
TODO: substituir estes no redes.json
known_name_errors = {
    "Jorge Manuel de Valsassina AIveias Rodrigues": "Jorge Manuel de Valsassina Galveias Rodrigues",
    "Carlos Alberto Silva Braz": "Carlos Alberto Silva Brás",
    "Edite de Fátima Santos Marreiro Estrela": "Edite de Fátima Santos Marreiros Estrela",
    "Francisco José Pereira Oliveira": "Francisco José Pereira de Oliveira",
    "Hugo Miguel da Costa Carvalho": "Hugo Miguel Costa Carvalho",
    "Joana Fernanda Ferreira de Lima": "Joana Fernanda Ferreira Lima",
    "Jorge Manuel Nascimento Botelho": "Jorge Manuel do Nascimento Botelho",
    "João Titterniton Gomes Cravinho": "João Titternigton Gomes Cravinho",
    "Maria Antónia Moreno Areias Almeida Santos":"Maria Antónia Moreno Areias de Almeida Santos",
    "Miguel de Oliveira Pires da Costa de Matos": "Miguel de Oliveira Pires da Costa Matos"
}


def mkdir_if_not_exists(path_to_create):
    if not exists(path_to_create): mkdir(path_to_create)


DOWNLOADED = "downloaded/"
ORGANISED = "organised/"
mkdir_if_not_exists(ORGANISED)

pages = [json.load(open(join(DOWNLOADED, f))) for f in listdir(DOWNLOADED) if isfile(join(DOWNLOADED, f)) and ".json" in f]

# final structures
territories = defaultdict(list)  # elected per territory
parties = defaultdict(list)  # elected by party
names = []  # flat list of elected people
names_full = []  # flat list of elected people with all their data
territories_party = defaultdict(list)  # elected per territory with party

# organize
for page in pages:
    for t in page:  # territories
        territory = t["territory"]
        for p in t["results"]:  # result per party in that territory
            party, elected = p["name"], p["elected"]
            elected = list(map(lambda e: e if e not in known_name_errors else known_name_errors[e], elected))
            names.extend(elected)
            parties[party].extend(elected)
            territories[territory].extend(elected)
            for name in elected:
                territories_party[territory].append({"nome": name, "partido": party})
                names_full.append({"nome": name, "partido": party, "distrito": territory})


# save to files
def save_to_file(obj, filename, sort=True):
    if sort:
        if type(obj) == list: obj.sort()
        if type(obj) == defaultdict: [v.sort() for _, v in obj.items()]
    with open(ORGANISED + filename, "w") as outf:
        outf.write(json.dumps(obj, indent=4, sort_keys=sort, ensure_ascii=False))


save_to_file(names, "nomes.json")
names_full.sort(key=lambda x: (x["partido"], x["nome"]))
save_to_file(names_full, "nomes_tudo.json", False)
save_to_file(parties, "partidos.json")
save_to_file(territories, "distritos.json")
[v.sort(key=lambda x: x["nome"]) for _, v in territories_party.items()]
save_to_file(territories_party, "distritos_partido.json", False)

print("vários formatos exportados para JSON")

import pandas as pd
pd.read_json(ORGANISED + "nomes_tudo.json").to_csv(ORGANISED + "nomes_tudo.csv", index=None)
print("também para CSV")

# updated README.md
ds, de = "<!-- DATA_START -->", "<!-- DATA_END -->"
with open("README.md", "r") as inf:
    readme = inf.read()
header = readme.split("<!-- DATA_START -->")[0]
footer = readme.split("<!-- DATA_END -->")[-1]

content = ""
oldp = ""
for person in names_full:
    newp = person["partido"]
    if person["partido"] != oldp:
        content += f"<strong>{newp}</strong>"
        oldp = newp
    content += f"""
<li>
    <a href="https://www.google.com/search?q={person['nome']}">google</a> | | | 
    <a href="https://www.google.com/search?q={person['nome']} wikipedia {person['partido']}">wikipedia</a> | 
    <a href="https://www.google.com/search?q={person['nome']} facebook {person['partido']}">facebook</a> | 
    <a href="https://www.google.com/search?q={person['nome']} twitter {person['partido']}">twitter 1</a> | 
    <a href="https://twitter.com/search?q={person['nome']}&f=user">twitter 2</a> | 
    <a href="https://www.google.com/search?q={person['nome']} instagram {person['partido']}">instagram</a> | 
    {person["nome"]}
</li>\n"""


with open("README.md", "w") as outf:
    outf.write(f"{header}{ds}\n<ul>\n{content}\n</ul>\n{de}\n{footer}")

# optional template to search for their websites
save_to_file({n["nome"]: {"wikipedia": "", "facebook": "", "twitter": "", "instagram": ""} for n in names_full}, "redes.json", False)

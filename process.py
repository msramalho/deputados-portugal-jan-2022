import json
from collections import defaultdict
from os import listdir, mkdir
from os.path import isfile, join, exists
import pandas as pd

# CNE has errors...
known_name_errors = {
    "Jorge Manuel de Valsassina AIveias Rodrigues": "Jorge Manuel de Valsassina Galveias Rodrigues",
    "Carlos Alberto Silva Braz": "Carlos Alberto Silva Brás",
    "Edite de Fátima Santos Marreiro Estrela": "Edite de Fátima Santos Marreiros Estrela",
    "Francisco José Pereira Oliveira": "Francisco José Pereira de Oliveira",
    "Hugo Miguel da Costa Carvalho": "Hugo Miguel Costa Carvalho",
    "Joana Fernanda Ferreira de Lima": "Joana Fernanda Ferreira Lima",
    "Jorge Manuel Nascimento Botelho": "Jorge Manuel do Nascimento Botelho",
    "João Titterniton Gomes Cravinho": "João Titternigton Gomes Cravinho",
    "Maria Antónia Moreno Areias Almeida Santos": "Maria Antónia Moreno Areias de Almeida Santos",
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
names_to_info = {}  # flat list of elected people pointing to all their data
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
                names_to_info[name] = {"partido": party, "distrito": territory}


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

pd.read_json(ORGANISED + "nomes_tudo.json").to_csv(ORGANISED + "nomes_tudo.csv", index=None)
print("também para CSV")


# MERGE redes with parlamento.pt with scraped data
# name -> redes sociais
with open("manual/redes.json") as inf:
    redes_manual = json.load(inf)

# name -> parlamento.pt id
with open(ORGANISED + "parlamento.pt.json") as inf:
    name_to_id = json.loads(inf.read())


deputados = []
for name, redes in redes_manual.items():
    entry = {"parlamento.pt": "", "nome": name, "partido": "", "distrito": ""}
    if name not in names_to_info:
        print(f"{name} not found in scraped data data")
    else: entry.update(names_to_info[name])

    if name not in name_to_id:
        print(f"{name} not found in parlamento.pt data")
    else: entry["parlamento.pt"] = name_to_id[name]

    entry.update(redes)

    deputados.append(entry)


with open(ORGANISED + "deputados_final.json", "w") as outf:
    outf.write(json.dumps(deputados, indent=4, sort_keys=False, ensure_ascii=False))
print("lista final para JSON")

pd.read_json(ORGANISED + "deputados_final.json").to_csv(ORGANISED + "deputados_final.csv", index=None)
print("lista final para CSV")

  
# saving xlsx file
with pd.ExcelWriter(ORGANISED + "deputados_final.xlsx") as ew:
    pd.read_json(ORGANISED + "deputados_final.json").to_excel(ew, sheet_name="deputados")
  
print("lista final para Excel")


# put the links and data into another .md and html files
def get_anchor_if_exists(d, key):
    key_to_url = {
        "parlamento.pt": "https://www.parlamento.pt/DeputadoGP/Paginas/Biografia.aspx?BID=%s",
        "wikipedia": "https://pt.wikipedia.org/wiki/%s",
        "facebook": "https://www.facebook.com/%s",
        "facebook_id": "https://www.facebook.com/profile.php?%s",
        "twitter": "https://twitter.com/%s",
        "instagram": "https://www.instagram.com/%s",
    }
    if not len(str(d[key])): return ""
    url_key = "facebook_id" if key == "facebook" and d[key][0:3] == "id=" else key
    return f"<a href='{key_to_url[url_key] % d[key]}'>{d[key]}</a>"


# sorting by party, then name
deputados.sort(key=lambda x: (x["partido"], x["nome"]))
content = ""
for d in deputados:
    content += f"""
<tr>
    <td>{get_anchor_if_exists(d, "parlamento.pt")}</td>
    <td>{d['partido']}</td>
    <td>{d['nome']}</td>
    <td>{d['distrito']}</td>
    <td>{get_anchor_if_exists(d, "wikipedia")}</td>
    <td>{get_anchor_if_exists(d, "facebook")}</td>
    <td>{get_anchor_if_exists(d, "twitter")}</td>
    <td>{get_anchor_if_exists(d, "instagram")}</td>
</tr>
"""


with open("DEPUTADOS.md", "w") as outf, open("index.html", "w") as outf_html:
    final_html = f"""
<h1>Deputados legislativas 2022</h1>

<h3><a href="https://github.com/msramalho/deputados-portugal-jan-2022/">HOMEPAGE</a></h3>

Podes fazer o download do <a href="organised/deputados_final.csv">CSV</a> ou do <a href="organised/deputados_final.json">JSON</a>.

<table>
    <tr>
        <th>id parlamento.pt</th>
        <th>partido</th>
        <th>nome</th>
        <th>distrito</th>
        <th>wikipedia</th>
        <th>facebook</th>
        <th>twitter</th>
        <th>instagram</th>
    </tr>{content}
</table>"""
    outf.write(final_html)
    outf_html.write(f"---\nlayout: default\n---\n\n{final_html}")

# optional template to search for their websites
# save_to_file({n["nome"]: {"wikipedia": "", "facebook": "", "twitter": "", "instagram": ""} for n in names_full}, "redes.json", False)

print("FIM")

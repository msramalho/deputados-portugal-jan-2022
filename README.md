## Deputados e suas contas

<h3>Ver as informações recolhidas sobre os deputados <a href="Deputados.md">aqui 👀</a></h3>

<h4>Ver também outras organizações dos dados na pasta <a href="organised/">organised</a></h4>

---

Este projeto recolhe e estrutra dados sobre os deputados eleitos nas legislativas de 30 de janeiro de 2022. Também indexa todas as páginas de membros atuais e passados do parlamento, recolhidos do parlamento.pt. A informação sobre páginas de wikipedia, facebook, twitter e instagram foram feitas manualmente para complementar os dados. Por parte do processo ter sido manual, erros e lacunas são expectáveis, mesmo com o tempo, e agradeço contributos e correções, basta editar o ficheiro [redes.json](manual/redes.json). 


---


## Recolha replicável

### scraping + download (javascript)
1. ir a [legislativas2022.mai.gov.pt/candidatos?elected=1](https://www.legislativas2022.mai.gov.pt/candidatos?elected=1)
2. usar o código javascript [abaixo](#javascript-page-scrape) na consola
3. guardar o JSON resultante na consola
4. repetir os 2 passos anteriores para as restantes páginas
5. o resultado das 3 páginas está em [downloaded](downloaded/)
6. (há alguns dados duplicados sobre os partidos, mas em quantidade insignificante e que não estará assim no resultado final)


#### recolha - javascript
```js
let pageData = Array.from(document.querySelectorAll(".territoryName")).map(t=>{
    let territory = t.innerText;
    let results = Array.from(t.nextSibling.querySelectorAll(".candidates")).map(p=>{
        let logo = p.querySelector("img").src;
        let name = p.querySelector(".party").innerText;
        let elected = Array.from(p.querySelectorAll(".row.mb-1 .d-inline")).map(e=> e.innerText.split(".")[1].trimStart());
        return {logo, name, elected}
    })
    
    return{territory, results};
});
console.log(JSON.stringify(pageData));
```

### tratamento - python
#### setup
Usei o [pipenv](https://pipenv.pypa.io/en/latest/) para gerir os módulos de python usados de forma replicável, basta instalar e correr `pipenv install` para instalar, e depois `pipenv shell` para entrar no ambiente pronto a correr.

#### scraping parlamento.pt
Basta executar `python parlamento.pt.py <id-inicial>` (com `pipenv shell` ativada) para atualizar a lista de deputados. Se não especificates `<id-inicial>` é usado o máximo dos ids já recolhidos, mas como a lista não é crescente de forma congruente pode ser necessário recomeçar do 0 em alguns casos. Nota: se quiseres contribuir para o projeto, um bom desafio é paralelizar os pedidos ao site do parlamento.pt para demorar menos tempo, atualmente deve demorar uns 30min sem paralelização. 

#### juntar os dados e produzir os JSONs, CSVs e a página DEPUTADOS.md
Basta correr `python organise.py` (com `pipenv shell` ativada)
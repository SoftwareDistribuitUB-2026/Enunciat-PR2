# Flux de Treball amb Git i Integració Contínua (CI)

**Resum:** Aquesta guia detalla el flux de treball professional basat en branques (`main` i `dev`) que utilitzarem durant l'assignatura per desenvolupar de manera segura i col·laborativa. També explica com funciona la Integració Contínua (CI) mitjançant GitHub Actions per validar automàticament la qualitat del teu codi, i com pots executar aquestes mateixes validacions al teu ordinador abans de pujar els canvis al repositori.

**Índex de continguts:**
* [1. L'Estratègia de Branques (`main` vs `dev`)](#1-lestratègia-de-branques-main-vs-dev)
* [2. GitHub Actions i els Informes de Validació](#2-github-actions-i-els-informes-de-validació)
* [3. Com executar les proves en local abans de pujar el codi](#3-com-executar-les-proves-en-local-abans-de-pujar-el-codi)

---

## 1. L'Estratègia de Branques (`main` vs `dev`)

Per mantenir el codi ordenat i evitar trencar l'aplicació, no treballarem directament sobre la branca principal. Utilitzarem dues branques:

* **`main` (o `master`):** És la branca de **producció**. Aquí només hi ha d'haver codi que estigui 100% acabat, testejat i funcionant.
* **`dev` (development):** És la branca de **desenvolupament**. Aquí és on integrareu la feina del dia a dia.

**El teu flux de treball habitual hauria de ser:**
1. Quan clonis el repositori, estaràs a `main`.
2. Immediatament, crea i mou-te a la branca de desenvolupament:
   ```bash
   git checkout -b dev
   ```
   *(Si la branca ja existeix al repositori remot, simplement fes `git checkout dev`).*
3. Treballa, fes els teus commits i puja els canvis a aquesta branca:
   ```bash
   git push origin dev
   ```
4. Quan una pràctica o sessió estigui completament acabada i validada a `dev`, obriràs una **Pull Request (PR)** a GitHub per fusionar els canvis de `dev` cap a `main`.

## 2. GitHub Actions i els Informes de Validació

Cada cop que facis un `push` a les branques `main` o `dev`, GitHub executarà automàticament un conjunt de proves al núvol. Això es coneix com a **Integració Contínua (CI)**.

Aquestes proves verifiquen dues coses:
1.  **Linter i Format:** Que el codi estigui ben escrit i segueixi les regles d'estil (usant *Ruff* al backend i *ESLint* al frontend).
2.  **Tests Unitaris:** Que totes les proves automatitzades passin correctament (usant *Pytest* i *Vitest*).

### Com veure si la teva feina és correcta?

1.  Ves al teu repositori a GitHub i fes clic a la pestanya **"Actions"**.
2.  Veuràs una llista amb tots els teus *commits*. Si veus una rodoneta verda (✅), tot ha anat bé. Si és vermella (❌), alguna cosa ha fallat.
3.  Fes clic sobre l'execució que vulguis revisar. A la pàgina de resum (Summary), veuràs un informe visual amb el detall exacte dels tests:
    * Quants tests s'han executat.
    * Quins tests específics han fallat i en quina línia de codi s'ha produït l'error.
4.  A més, si fas una *Pull Request* de `dev` a `main`, GitHub no et deixarà (o t'avisarà) fer la fusió si les proves estan fallant.

## 3. Com executar les proves en local abans de pujar el codi

Pujar codi que no funciona i esperar que GitHub Actions et digui on has fallat és un procés lent i frustrant. La millor pràctica és **executar les mateixes eines en el teu ordinador** abans de fer el `git commit` i el `git push`. Així tindràs un retorn immediat.

Aquí tens les comandes exactes que executa el pipeline i que tu també pots llançar des del teu terminal:

### Al Backend (Django)
Obre un terminal, assegura't d'estar dins la carpeta `backend/` i executa:

1. **Revisar l'estil (Format):**
   ```bash
   uv run ruff format .
   ```
   *Aquesta comanda arregla automàticament la majoria de problemes d'espais i cometes al teu codi Python.*

2. **Passar el Linter (Errors i males pràctiques):**
   ```bash
   uv run ruff check .
   ```

3. **Executar els Tests Unitaris:**
   ```bash
   uv run pytest
   ```
   *Veuràs per consola quins tests passen i quins fallen amb el detall de l'error.*

### Al Frontend (Vue)
Obre un altre terminal, assegura't d'estar dins la carpeta `frontend/` i executa:

1. **Passar el Linter (ESLint):**
   ```bash
   npm run lint
   ```

2. **Executar els Tests Unitaris:**
   ```bash
   npm run test:unit
   ```
   *Això obrirà Vitest, que es queda "escoltant". Si modifiques un fitxer i guardes, tornarà a passar els tests automàticament. Per sortir-ne, prem `q` o `Ctrl+C`.*

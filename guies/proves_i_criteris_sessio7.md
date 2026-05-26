# Catàleg de proves i criteris d'avaluació (Sessió 7)

Aquesta guia defineix les proves a executar, els resultats esperats i què cal revisar en cas d'error.

## 1. Criteris generals

1. Cada prova ha de quedar registrada a l'informe amb codi, descripció i resultat.
2. El resultat s'ha d'indicar com a mínim com: `PASSA`, `FALLA` o `NO APLICABLE`.
3. Quan una prova falla, cal afegir una observació amb evidència mínima.
4. Sempre que sigui possible, combineu prova automatitzada (script) i validació manual.

## 2. Prova de desplegament (obligatòria)

### T00 - Desplegament amb Docker Compose

* **Objectiu:** comprovar que el sistema es pot aixecar i operar amb `docker compose`.
* **Precondicions:** repositori de cada grup que s'avalua clonat i dependències de Docker disponibles.
* **Passos generals:**
  1. Executar la comanda de desplegament indicada pel grup.
  2. Verificar que els serveis principals arrenquen.
  3. Comprovar accés als serveis principals (API i frontend, si escau).
* **Resultat esperat:** serveis en estat funcional.
* **Què revisar si falla:** errors de configuració, variables d'entorn, ports, dependències i serveis no saludables.

## 3. Catàleg de proves funcionals

### T01 - Registre d'usuari correcte

* **Objectiu:** validar alta d'usuari.
* **Resultat esperat:** resposta d'èxit i alta creada.

### T02 - Login correcte

* **Objectiu:** validar autenticació i recepció de token.
* **Resultat esperat:** resposta d'èxit amb token vàlid.

### T03 - Accés a endpoint protegit sense token

* **Objectiu:** validar protecció d'endpoints.
* **Resultat esperat:** accés denegat (`401` o `403`).

### T04 - Accés a la llista d'usuaris sense autenticació

* **Objectiu:** comprovar control d'accés a llistat sensible.
* **Resultat esperat:** accés denegat.

### T05 - Modificació d'usuari sense autenticació

* **Objectiu:** impedir edició sense credencials.
* **Resultat esperat:** accés denegat.

### T06 - Modificació d'un altre usuari sense permisos d'admin

* **Objectiu:** validar restricció per propietat/rol.
* **Resultat esperat:** accés denegat.

### T07 - Modificació de les pròpies dades

* **Objectiu:** validar que l'usuari pot editar el seu perfil (si la API ho permet).
* **Resultat esperat:** edició permesa o justificació clara si no està suportat.

### T08 - Modificació de la capacitat d'un espectacle per usuari normal

* **Objectiu:** impedir manipulació d'aforament per usuaris no privilegiats.
* **Resultat esperat:** accés denegat.

### T09 - Alta d'esdeveniment per usuari no privilegiat

* **Objectiu:** validar política de creació d'esdeveniments.
* **Resultat esperat:** segons política del projecte (cal indicar-la explícitament a l'informe).

### T10 - Alta d'esdeveniment per usuari amb permisos elevats

* **Objectiu:** validar flux administratiu.
* **Resultat esperat:** creació correcta.

### T11 - Compra correcta amb estoc suficient

* **Objectiu:** validar flux de compra correcte.
* **Resultat esperat:** compra acceptada i registrada.

### T12 - Compra fallida amb estoc insuficient

* **Objectiu:** validar control d'estoc.
* **Resultat esperat:** compra rebutjada amb error funcional coherent.

### T13 - Compra per un segon usuari sobre esdeveniment existent

* **Objectiu:** comprovar consistència multiusuari.
* **Resultat esperat:** flux correcte segons estoc disponible i permisos.

## 4. Proves unitàries pròpies del grup

A més de les proves creuades, cada grup ha de descriure a l'informe:

1. Quins tests unitaris té implementats.
2. Quines parts del sistema cobreixen (autenticació, permisos, compra, etc.).
3. Quins buits de cobertura coneixen.
4. Resultat global de l'execució de tests.

## 5. Taula recomanada de resum de resultats

Per homogeneïtzar correcció, utilitzeu aquesta taula a l'informe:

| Codi | Descripció | Resultat |
| :--- | :--- | :--- |
| T00 | Desplegament amb Docker Compose |  |
| T01 | Registre d'usuari correcte |  |
| T02 | Login correcte |  |
| T03 | Accés endpoint protegit sense token |  |
| T04 | Llista d'usuaris sense autenticació |  |
| T05 | Modificació d'usuari sense autenticació |  |
| T06 | Modificació d'un altre usuari sense permisos |  |
| T07 | Modificació de les pròpies dades |  |
| T08 | Modificació de capacitat d'esdeveniment (usuari normal) |  |
| T09 | Alta d'esdeveniment (usuari no privilegiat) |  |
| T10 | Alta d'esdeveniment (usuari privilegiat) |  |
| T11 | Compra correcta amb estoc suficient |  |
| T12 | Compra fallida amb estoc insuficient |  |
| T13 | Compra d'un segon usuari sobre esdeveniment existent |  |

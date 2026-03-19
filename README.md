---
author: Xevi Baró, Mario Moliner, Eloi Puertas
date: Abril 2025
title: Pràctica 2 - DJango and Vue application (Software distribuït)
---

# Enunciat Pràctica 2

# Introducció

En aquesta pràctica implementarem una aplicació de comerç electrònic, però a diferència de la pràctica1, en aquest cas utilitzarem protocols estàndard web i una base de dades.
Treballarem amb dos mòduls completament diferenciats:

- **Backend**: Implementarà una REST-API per accedir i gestionar de forma segura les dades de l'aplicació. S'encarregarà de l'autenticació dels usuaris i de l'accés a la base de dades.
- **Frontend**: Consisteix en una aplicació web que s'executarà localment en el navegador de l'usuari, permetent la interacció de l'usuari amb l'aplicació.

## Important

Aquest exercici guiat suposa que ja teniu alguna versió de Python de versió mínima `3.12` instal·lada. 

Es recomana altament l'ús de la IDE [PyCharm Professional](https://www.jetbrains.com/pycharm/) per al desenvolupament del backend d'aquesta pràctica i l'IDE [WebStorm](https://www.jetbrains.com/webstorm/) per al frontend. Si no el teniu instal·lat, existeix una versió per a estudiants que podeu obtenir si us registreu amb el correu de la UB. També es pot utilitzar Visual Studio Code si us resulta més còmode.

## Enviament dels Exercicis

Es treballarà de la mateixa manera que a la Pràctica 1, utilitzant un repositori de `GitHub Classroom` com a base. El repositori ha de contenir:

- El codi que implementa totes les funcionalitats requerides.
- `Pull Requests` setmanals amb:
  - la descripció de les tasques complertes durant la setmana i les que han quedat pendents.
  - organització dels membres de l'equip per a la realització de les tasques
  - problemes sorgits durant la setmana
  - resum de proves realitzades
- Durant la realització de la pràctica haureu d'anar documentant el vostre progrés en la memòria que trobareu en el directori `docs` del template de la pràctica.

**NOTA:** Recordeu que els `Pull Requests` cal que els iniciï un membre de l'equip i els accepti l'altre, donant així conformitat al seu contingut per part dels dos membres de l'equip.

## Avaluació pràctica 2.

- 20% pull requests setmanals
- 80% Lliurament final:
  - 20% Sessió de Test,
  - 20% Proves unitàries
  - 50% codi final,
  - 10% Memòria progrés.

## Objectius de la Pràctica

#### Back-End:

- Crear aplicació CRUD amb autentificació per a gestionar (CRUD: Create, Read, Update i Delete) de la part de model d'aplicació
- Gestionar la lògica del joc

#### Front-End:

- Interacció amb l'usuari, tant pel que fa a la visualització de dades com a la recollida d'accions.
- Comunicació segura amb el back-end

# Calendari

| Sessió | Data (Setmana) | Tema | Guia | Enllaços |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 23/03/26 | Backend Foundation (Models i DRF) | [Sessió 1](sessions/sessio1.md) | [Intro a Django](guies/inici_django.md) |
| 2 | 06/04/26 | Frontend, Axios i Reactivitat | [Sessió 2](sessions/sessio2.md) | [Intro a Vue](guies/introduccio_vue.md)<br>[CORS i CSRF](guies/seguretat_cors_csrf.md) |
| 3 | 13/04/26 | Navegació (Router) i Cistella (Pinia) | [Sessió 3](sessions/sessio3.md) | [Estat amb Pinia](guies/estat_pinia.md) |
| 4 | 27/04/26 | Autenticació i Autorització |  | |
| 5 | 04/05/26 | Finalització de Compres i Testing | | |
| 6 | 11/05/26 | Sessió de Proves i Desplegament |  | |


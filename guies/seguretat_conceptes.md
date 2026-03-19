# Conceptes de Seguretat Web: Autenticació, JWT i Criptografia

**Resum:** Aquesta guia estableix els fonaments teòrics de la seguretat en aplicacions web modernes. Abans de picar codi, és imprescindible entendre la diferència entre saber qui és un usuari i què pot fer, per què mai guardem contrasenyes en text pla, com funciona l'estàndard JWT per comunicar de forma segura el frontend i el backend, i els conceptes d'encriptació simètrica i asimètrica per protegir dades sensibles.

**Índex de continguts:**
* [1. Autenticació vs. Autorització](#1-autenticació-vs-autorització)
* [2. Hash de Contrasenyes](#2-hash-de-contrasenyes)
* [3. Encriptació: Simètrica vs. Asimètrica](#3-encriptació-simètrica-vs-asimètrica)
* [4. JSON Web Tokens (JWT) i les Signatures](#4-json-web-tokens-jwt-i-les-signatures)
* [5. Protecció de dades sensibles a la Base de Dades i Xarxa](#5-protecció-de-dades-sensibles-a-la-base-de-dades-i-xarxa)
* [6. Referències i Enllaços Útils](#6-referències-i-enllaços-útils)

---

## 1. Autenticació vs. Autorització

Tot i que sovint es confonen, són dos processos completament diferents dins del cicle de seguretat:


* **Autenticació (Qui ets?):** És el procés de verificar la identitat d'un usuari. Normalment es fa demanant unes credencials (com un email i una contrasenya). Si són correctes, el sistema diu: *"D'acord, sé que ets l'Alice"*.
* **Autorització (Què pots fer?):** Un cop sabem que ets l'Alice, el sistema ha de decidir si tens permís per fer una acció concreta. *"L'Alice pot llegir aquest article, però no el pot esborrar perquè no n'és l'autora ni és administradora"*.

## 2. Hash de Contrasenyes

**Mai, sota cap concepte, es guarden les contrasenyes en text pla a la base de dades.** Si un atacant robés la base de dades, tindria accés immediat als comptes de tothom.

En lloc d'això, s'aplica una funció de **Hash** (com *PBKDF2* o *Bcrypt*). Un hash és un algorisme matemàtic unidireccional:
1. Transforma "hola123" en una cadena il·legible com `$2b$12$xyz...`
2. És **unidireccional**: No pots agafar el hash i desfer-lo per recuperar "hola123".
3. Quan l'usuari fa login, el sistema aplica el hash a la contrasenya que acaba d'escriure i compara si el resultat coincideix amb el hash guardat a la base de dades.

## 3. Encriptació: Simètrica vs. Asimètrica

A diferència del Hash (que no es pot desfer), l'**Encriptació** s'utilitza quan necessitem amagar una dada però hem de poder recuperar-ne el valor original més endavant (com el número d'una targeta de crèdit o un missatge privat). Hi ha dos tipus principals:


[Image of Symmetric vs Asymmetric encryption diagram]


* **Encriptació Simètrica:** Utilitza **una única clau secreta** tant per xifrar (amagar) com per desxifrar (recuperar) la informació. És molt ràpida i eficient, ideal per xifrar grans quantitats de dades a la nostra base de dades. El repte és que si algú descobreix aquesta clau única, podrà llegir-ho tot.
* **Encriptació Asimètrica:** Utilitza **un parell de claus (Pública i Privada)**. El que es xifra amb la Pública només es pot desxifrar amb la Privada, i viceversa. És més lenta, però resol el problema de compartir claus de forma segura per Internet. S'utilitza en protocols com HTTPS i per crear signatures digitals.

## 4. JSON Web Tokens (JWT) i les Signatures

Com que les APIs REST són *stateless* (no guarden memòria de les peticions anteriors), necessitem una manera de recordar qui està fent la petició després del login. Aquí entra el **JWT**.


Un JWT és un "passaport" que el backend dona al frontend. Està format per tres parts (`header.payload.signature`):
1. **Header:** Indica el tipus de token i l'algorisme usat.
2. **Payload:** Conté les dades públiques de l'usuari (ex: `{"user_id": 4}`). *Aquestes dades es poden llegir, no hi posis mai contrasenyes!*
3. **Signature (Signatura):** És la part màgica. Garanteix que ningú ha manipulat el token.

**Com es relaciona la signatura amb la criptografia?**
* **Signatura Simètrica (HMAC / HS256):** El backend utilitza una única clau secreta (ex. `SECRET_KEY` de Django) per signar el token i per verificar-lo quan el frontend l'envia de tornada. És l'enfocament més comú i senzill per a aplicacions on el mateix servidor que emet el token és el que el valida.
* **Signatura Asimètrica (RSA / RS256):** Un servidor d'autenticació signa el token amb la seva Clau Privada. Després, altres microserveis poden utilitzar la Clau Pública per verificar que el token és vàlid sense necessitat de conèixer el secret principal.

## 5. Protecció de dades sensibles a la Base de Dades i Xarxa

Quan dissenyem el nostre model de dades, hem d'identificar quines dades són sensibles (historials mèdics, dades bancàries, tokens de tercers). Aquestes dades s'han de guardar a la base de dades utilitzant **encriptació simètrica** (a nivell de camp o de disc). D'aquesta manera, si un atacant obté una còpia de l'arxiu `.sqlite3` o un bolcat de MariaDB, només veurà text xifrat il·legible.

Finalment, tota aquesta seguretat no serveix de res si algú pot "escoltar" la xarxa i robar el JWT o les dades mentre viatgen. Per això, en producció és obligatori l'ús de **HTTPS** (basat en criptografia asimètrica per establir la connexió i simètrica per transmetre les dades), que xifra totes les comunicacions en trànsit.

## 6. Referències i Enllaços Útils
* [OWASP: Conceptes d'Autenticació](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
* [JWT.io - Eina per depurar i entendre els JSON Web Tokens](https://jwt.io/)
* [Mozilla Developer Network (MDN) - Què és HTTPS?](https://developer.mozilla.org/en-US/docs/Glossary/HTTPS)

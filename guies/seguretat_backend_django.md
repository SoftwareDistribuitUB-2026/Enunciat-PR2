# Aplicant la Seguretat al Backend (Django i DRF)

**Resum:** Com traslladem la teoria criptogràfica i d'autenticació a la pràctica? Aquesta guia t'ensenya com Django gestiona els usuaris i els hashes de contrasenya de forma nativa, com generar JSON Web Tokens (JWT) amb la llibreria `SimpleJWT`, com protegir els teus endpoints (URLs) amb permisos de DRF, i com utilitzar encriptació simètrica per protegir dades sensibles (com targetes de crèdit) directament a la base de dades.

**Índex de continguts:**
* [1. Usuaris i Hashes a Django](#1-usuaris-i-hashes-a-django)
* [2. Generació i validació de JWT](#2-generació-i-validació-de-jwt)
* [3. Autorització: Protegir Endpoints i Instàncies](#3-autorització-protegir-endpoints-i-instàncies)
* [4. Encriptació de camps sensibles a la Base de Dades](#4-encriptació-de-camps-sensibles-a-la-base-de-dades)
* [5. Referències i Enllaços Útils](#5-referències-i-enllaços-útils)

---

## 1. Usuaris i Hashes a Django

Django ja porta un sistema d'autenticació robust de sèrie (`django.contrib.auth`). Quan crees un usuari, el framework s'encarrega d'aplicar el hash a la contrasenya automàticament si utilitzes els mètodes correctes. **Mai has d'assignar la contrasenya directament al camp text.**

* **Incorrecte:** `user.password = "hola123"` (Es guardaria en text pla).
* **Correcte:** `user.set_password("hola123")` (Aplica el hash, normalment PBKDF2, abans de guardar).

Si fas servir Serialitzadors de DRF per registrar usuaris, recorda sobreescriure el mètode `create` per assegurar-te que s'aplica el hash:

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}} # Evita que la contrasenya s'enviï en un GET

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password']) # Apliquem el hash
        user.save()
        return user
````

## 2\. Generació i validació de JWT

Per implementar JWT a Django REST Framework (DRF), fem servir la llibreria `djangorestframework-simplejwt`.
Aquesta llibreria ens proporciona rutes prefabricades al `urls.py` (`TokenObtainPairView`).

**Com funciona el flux?**

1.  El frontend envia un POST amb `username` i `password`.
2.  La vista de SimpleJWT busca l'usuari, n'agafa el hash de la base de dades i comprova si la contrasenya coincideix.
3.  Si és correcte, agafa la `SECRET_KEY` del teu `settings.py` (clau simètrica), genera el JWT, el signa, i el retorna al frontend.
4.  En peticions futures, quan DRF rep el token a la capçalera, n'extreu la signatura, la verifica amb la mateixa `SECRET_KEY`, i si és vàlida, identifica l'usuari posant-lo a `request.user`.

## 3\. Autorització: Protegir Endpoints i Instàncies

Saber qui és l'usuari (Autenticació) no és suficient. Hem de decidir què pot fer (Autorització). A DRF utilitzem les `permission_classes`.

**Protecció general d'un Endpoint:**
Pots aplicar permisos a tot un ViewSet per evitar que usuaris anònims hi accedeixin.

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

class PerfilViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated] # Només usuaris amb JWT vàlid
    # ...
```

**Protecció a nivell d'Instància (Object-level):**
Si tens un endpoint `DELETE /api/articles/5/`, `IsAuthenticated` permetrà a qualsevol usuari registrat esborrar l'article 5. Necessites un permís personalitzat per validar que l'usuari que fa la petició és el propietari d'aquell objecte:

```python
from rest_framework import permissions

class EsPropietari(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return True
        return obj.autor == request.user # Només True si ets el creador
```

## 4\. Encriptació de camps sensibles a la Base de Dades

De vegades necessitem guardar dades crítiques (com números de compte bancari o historials mèdics). Com hem vist a la teoria, no en podem fer un hash perquè necessitarem llegir-les més endavant. Hem de fer servir **encriptació simètrica**.

A Django, la manera més senzilla de fer-ho és utilitzant llibreries com `django-cryptography`. Aquesta llibreria xifra la dada abans de fer l'INSERT a la base de dades (fent que quedi il·legible si algú roba l'arxiu SQL) i la desxifra automàticament quan fas un `SELECT` amb l'ORM.

**Exemple d'ús:**

```python
from django.db import models
from cryptography.fernet import Fernet
from django_cryptography.fields import encrypt

class Pagament(models.Model):
    usuari = models.ForeignKey(User, on_delete=models.CASCADE)
    import_pagat = models.DecimalField(max_digits=6, decimal_places=2)
    # Aquest camp estarà encriptat a la base de dades real
    targeta_credit = encrypt(models.CharField(max_length=16)) 
```

Perquè això funcioni de forma segura, la teva aplicació necessita una clau criptogràfica (diferent de la de Django, idealment) guardada a les variables d'entorn (`.env`).

## 5\. Referències i Enllaços Útils

  * [Documentació Oficial de Django - Gestió d'Usuaris i Hashes](https://www.google.com/search?q=https://docs.djangoproject.com/en/stable/topics/auth/default/%23django.contrib.auth.models.User.set_password)
  * [Django REST Framework - Permisos i Autorització](https://www.django-rest-framework.org/api-guide/permissions/)
  * [SimpleJWT - Documentació per generar Tokens a Django](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
  * [GitHub - django-cryptography](https://www.google.com/search?q=https://github.com/georgema1982/django-cryptography)

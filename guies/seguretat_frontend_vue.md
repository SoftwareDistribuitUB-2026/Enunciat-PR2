# Gestionant l'Autenticació i Dades Sensibles al Frontend (Vue i Axios)

**Resum:** Aquesta guia detalla com gestionar l'estat de la sessió al navegador i com interactuar amb una API segura. Aprendràs on desar el JWT, com configurar Axios perquè injecti el token automàticament a totes les peticions, com utilitzar els "Guards" del Vue Router per bloquejar pantalles, i quines són les bones pràctiques a l'hora de manipular dades sensibles (com targetes de crèdit) al costat del client.

**Índex de continguts:**
* [1. On guardem el Token?](#1-on-guardem-el-token)
* [2. Axios Interceptors: Injectant el JWT](#2-axios-interceptors-injectant-el-jwt)
* [3. Protegint rutes amb Vue Router Guards](#3-protegint-rutes-amb-vue-router-guards)
* [4. Manipulació de dades sensibles al Client](#4-manipulació-de-dades-sensibles-al-client)
* [5. Referències i Enllaços Útils](#5-referències-i-enllaços-útils)

---

## 1. On guardem el Token?

Quan el backend ens retorna el JWT després d'un login correcte, necessitem guardar-lo perquè sobrevisqui si l'usuari recarrega la pàgina (F5). Tenim dues opcions principals a l'API del navegador:

* **`localStorage`:** Les dades persisteixen fins i tot si l'usuari tanca la pestanya o el navegador. Útil per mantenir la sessió iniciada durant dies.
* **`sessionStorage`:** Les dades s'esborren tan bon punt es tanca la pestanya. És més segur per a aplicacions crítiques (com bancs).

Habitualment el guardem al `localStorage` i, en paral·lel, el carreguem a l'estat global de l'aplicació (Pinia o variables reactives) perquè la interfície de Vue (com la Navbar) s'actualitzi immediatament.

*Nota de seguretat:* Guardar el JWT a `localStorage` ens fa vulnerables a atacs XSS (Cross-Site Scripting). Ens hem d'assegurar que el nostre codi Vue no renderitza mai HTML cru introduït per usuaris (usant `v-html` sense sanejar).

## 2. Axios Interceptors: Injectant el JWT

No volem haver de posar el token manualment a la capçalera cada vegada que fem una petició `axios.get()` o `axios.post()`. Els **Interceptors** d'Axios permeten executar codi automàticament just abans que la petició surti del navegador.

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000' });

// Interceptor per afegir el token a cada petició
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    // Afegim la capçalera estàndard d'autorització Bearer
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
````

Ara, quan facis `api.get('/api/perfil/')`, el token viatjarà automàticament i el backend et reconeixerà.

## 3\. Protegint rutes amb Vue Router Guards

De la mateixa manera que al backend protegim els endpoints, al frontend hem de protegir les Vistes perquè un usuari no loguejat no pugui veure la pantalla `/el-meu-perfil`.
Ho fem al fitxer de rutes, afegint una propietat `meta` a la ruta i utilitzant un `beforeEach` (un Guard).

```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView },
    { 
      path: '/perfil', 
      component: PerfilView,
      meta: { requiresAuth: true } // Marquem que requereix login
    }
  ]
})

// S'executa abans de cada canvi de URL
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token');
  
  // Si la ruta requereix autenticació i no hi ha token
  if (to.meta.requiresAuth && !token) {
    next('/login'); // Redirigim al login
  } else {
    next(); // Deixem passar
  }
})
```

## 4\. Manipulació de dades sensibles al Client

Com hem vist a les guies anteriors, dades com els números de compte o targetes de crèdit es guarden **encriptades** a la base de dades del backend.

**Com arriben al frontend?**
Quan l'usuari fa un `GET` del seu perfil, el backend desxifra la dada i l'envia en format llegible (en text pla) dins del JSON. Per això és absolutament crític utilitzar **HTTPS** en producció; l'HTTPS actua com un túnel xifrat entre el backend i el navegador perquè ningú ho pugui llegir pel camí.

**La regla d'or al Frontend:**
El navegador web és un entorn inherentment insegur (el codi s'executa a la màquina de l'usuari). Per tant:

1.  **Mai** guardis dades sensibles (targetes de crèdit, números de seguretat social, historials mèdics desxifrats) al `localStorage` o `sessionStorage`.
2.  Aquestes dades només han de viure en memòria temporal (dins d'una variable `ref` de Vue o a l'estat de Pinia). Quan l'usuari tanca la pestanya o recarrega la pàgina, la memòria s'allibera i les dades desapareixen.

## 5\. Referències i Enllaços Útils

  * [Vue Router - Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
  * [Axios - Interceptors](https://axios-http.com/docs/interceptors)
  * [OWASP - HTML5 Security Cheat Sheet (Emmagatzematge Local)](https://www.google.com/search?q=https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html%23local-storage)

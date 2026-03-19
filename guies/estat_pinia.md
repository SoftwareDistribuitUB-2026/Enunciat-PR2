# Gestió de l'Estat Global amb Pinia

**Resum:** A mesura que la teva aplicació Vue creixi, et trobaràs amb dades que necessiten ser accessibles des de múltiples pantalles diferents (com les dades de l'usuari identificat o els missatges d'alerta globals). Aquesta guia t'explica la diferència entre l'estat local d'un component i l'estat global, i et mostra com instal·lar i utilitzar **Pinia**, la llibreria oficial i recomanada per Vue 3 per gestionar aquest estat compartit de manera senzilla i eficient.

**Índex de continguts:**
* [1. Estat Local vs Estat Global](#1-estat-local-vs-estat-global)
* [2. Instal·lació i configuració de Pinia](#2-instal·lació-i-configuració-de-pinia)
* [3. Creació del teu primer "Store" (Magatzem)](#3-creació-del-teu-primer-store-magatzem)
* [4. Com utilitzar l'Store als teus components](#4-com-utilitzar-lstore-als-teus-components)

---

## 1. Estat Local vs Estat Global

* **Estat Local:** Són les variables que defineixes dins d'un component concret (utilitzant `ref` o `reactive` a Vue 3). Només aquest component les coneix. Està bé per a coses com "el text d'aquest formulari" o "si aquest menú desplegable està obert o tancat".
* **Estat Global:** Són dades que afecten tota l'aplicació i que es necessiten en pàgines (vistes) diferents. Si intentes passar aquestes dades de pare a fill contínuament (el que es coneix com a *prop drilling*), el codi es torna un caos. Aquí és on entra Pinia.

## 2. Instal·lació i configuració de Pinia

Si no vas dir "Sí" a Pinia durant la creació del projecte amb Vite, ho pots afegir manualment. Obre una terminal a la carpeta del frontend i executa:

```bash
npm install pinia
```

A continuació, has de dir-li a Vue que l'utilitzi. Obre el fitxer `src/main.js` (o `main.ts`) i modifica'l per incloure Pinia abans de muntar l'aplicació:

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. Importem Pinia
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia() // 2. Creem la instància

app.use(pinia) // 3. L'afegim a la nostra app
app.use(router)

app.mount('#app')
```

## 3. Creació del teu primer "Store" (Magatzem)

Un **Store** és un fitxer on guardem un "tros" del nostre estat global. Es recomana crear una carpeta `src/stores/`. Per exemple, crearem un store per gestionar si l'usuari està autenticat: `src/stores/auth.js`.

A Vue 3, Pinia permet escriure els stores exactament igual que si fos el bloc `setup` d'un component (Composition API):

```javascript
// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 1. Estat (State) -> Variables reactives (ref)
  const user = ref(null)
  const token = ref(null)

  // 2. Getters -> Propietats calculades (computed)
  const isAuthenticated = computed(() => token.value !== null)

  // 3. Accions (Actions) -> Funcions per modificar l'estat
  function login(userData, userToken) {
    user.value = userData
    token.value = userToken
  }

  function logout() {
    user.value = null
    token.value = null
  }

  // Retornem el que volem fer públic
  return { user, token, isAuthenticated, login, logout }
})
```

## 4. Com utilitzar l'Store als teus components

Ara, des de qualsevol component (ja sigui la barra de navegació, el perfil o el *login*), pots importar i utilitzar aquest magatzem lliurement.

```html
<script setup>
import { useAuthStore } from '../stores/auth'

// Instanciem l'store per poder-lo fer servir
const authStore = useAuthStore()
</script>

<template>
  <nav>
    <router-link to="/">Inici</router-link>
    
    <div v-if="authStore.isAuthenticated">
      Benvingut, {{ authStore.user.name }}!
      <button @click="authStore.logout()">Tancar Sessió</button>
    </div>
    
    <div v-else>
      <router-link to="/login">Iniciar Sessió</router-link>
    </div>
  </nav>
</template>
```

Amb això, si l'usuari fa login en una pantalla i crida `authStore.login(...)`, la barra de navegació (que és un altre component diferent) s'actualitzarà automàticament a l'instant, ja que tots dos miren al mateix origen de veritat.

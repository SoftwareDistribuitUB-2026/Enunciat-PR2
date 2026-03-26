# Gestió d'Estat amb Pinia i Persistència amb LocalStorage

**Resum:** Com gestionar dades globals en una aplicació Vue perquè estiguin disponibles a qualsevol component utilitzant Pinia. Aprendrem també a combinar aquest gestor amb el `LocalStorage` del navegador per aconseguir que les dades (com les preferències d'un usuari o una cistella de la compra) no s'esborrin en refrescar la pàgina.

**Índex de continguts:**

1. Què és l'Estat Global i Pinia?
2. Què és el LocalStorage?
3. Instal·lació i Configuració Base.
4. Exemple Pràctic: Store de Preferències.
5. Bones Pràctiques.
6. Referències i enllaços relacionats.

## 1. Què és l'Estat Global i Pinia?

En aplicacions Vue petites, passem dades entre components utilitzant *Props* (de pare a fill) i *Emits* (de fill a pare). No obstant això, quan l'aplicació creix, hi ha dades que necessiten estar disponibles a molts llocs alhora de forma independent a la jerarquia de components. Identificarem dos estats:

* **Estat Local:** Són les variables que defineixes dins d'un component concret (utilitzant `ref` o `reactive` a Vue 3). Només aquest component les coneix. Està bé per a coses com "el text d'aquest formulari" o "si aquest menú desplegable està obert o tancat".
* **Estat Global:** Són dades que afecten tota l'aplicació i que es necessiten en pàgines (vistes) diferents. Si intentes passar aquestes dades de pare a fill contínuament (el que es coneix com a *prop drilling*), el codi es torna un caos.

Per resoldre el problema de l'estat global utilitzem **Pinia**, el gestor d'estat global oficial de Vue. Un "Store" (magatzem) de Pinia es divideix en tres conceptes fonamentals:
* **State (Estat):** Les dades o variables reactives (equivalent a `ref()` o `reactive()`).
* **Getters:** Dades calculades derivades de l'estat (equivalent a `computed()`).
* **Actions (Accions):** Funcions per modificar l'estat o fer operacions asíncrones.

## 2. Què és el LocalStorage?

El `LocalStorage` és una memòria integrada al navegador web de l'usuari que permet guardar informació de forma permanent (fins que l'usuari esborra l'historial o la memòria cau de forma manual).
Té algunes particularitats importants:
* Només pot guardar text (*Strings*).
* Per guardar objectes o arrays (el més habitual a Vue), hem de convertir-los a text amb `JSON.stringify()`.
* Per recuperar-los, els hem de tornar a convertir a codi amb `JSON.parse()`.

## 3. Instal·lació i Configuració Base

Abans de crear el nostre primer *Store*, cal instal·lar Pinia al projecte executant la següent comanda al terminal:

```bash
npm install pinia
```

Després, l'hem d'activar al fitxer principal de l'aplicació (`src/main.js`):

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```

## 4. Exemple Pràctic: Store de Preferències

Anem a crear un *Store* per gestionar les preferències d'un usuari: el seu nom i si prefereix el mode visual fosc o clar.

### Pas 1: Crear el Store (`src/stores/preferences.js`)
Dins de la carpeta `stores`, crearem el fitxer `preferences.js`. Utilitzarem la *Composition API* i la funció `watch` de Vue per guardar automàticament els canvis al `LocalStorage`.

```javascript
import { defineStore } from 'pinia';
import { ref, watch, computed } from 'vue';

export const usePreferencesStore = defineStore('preferences', () => {
  
  // 1. ESTAT: Intentem llegir del LocalStorage primer. Si no hi ha res, posem valors per defecte.
  const theme = ref(localStorage.getItem('app-theme') || 'light');
  const userName = ref(localStorage.getItem('app-username') || 'Convidat');

  // 2. PERSISTÈNCIA: Vigilem els canvis a les variables i actualitzem el LocalStorage
  watch(theme, (newTheme) => {
    localStorage.setItem('app-theme', newTheme);
  });

  watch(userName, (newName) => {
    localStorage.setItem('app-username', newName);
  });

  // 3. GETTERS: Dades derivades
  const isDarkMode = computed(() => theme.value === 'dark');

  // 4. ACCIONS: Funcions per modificar l'estat
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light';
  };

  const setUserName = (name) => {
    if (name.trim() !== '') {
      userName.value = name;
    }
  };

  // 5. EXPORTAR: Retornem tot allò que volem fer servir des dels components
  return { theme, userName, isDarkMode, toggleTheme, setUserName };
});
```

Un altre exemple típic el trobem en com es gestiona la informació de l'usuari. 

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

### Pas 2: Utilitzar el Store en un Component
Ara podem importar aquest store a qualsevol lloc (per exemple, a `App.vue`) i utilitzar-ne la informació de forma reactiva:

```vue
<script setup>
import { usePreferencesStore } from './stores/preferences';

// Creem una instància del store
const preferencesStore = usePreferencesStore();
</script>

<template>
  <div :class="preferencesStore.theme" class="app-container">
    
    <h1>Hola, {{ preferencesStore.userName }}!</h1>
    
    <p>El mode actual és: 
      <strong>{{ preferencesStore.isDarkMode ? 'Fosc' : 'Clar' }}</strong>
    </p>

    <button @click="preferencesStore.toggleTheme">
      Canviar Tema
    </button>

    <div class="input-group">
      <label>Actualitza el teu nom:</label>
      <input 
        type="text" 
        :value="preferencesStore.userName"
        @input="preferencesStore.setUserName($event.target.value)"
      />
    </div>

  </div>
</template>

<style scoped>
.light { background-color: #ffffff; color: #333333; }
.dark { background-color: #222222; color: #f0f0f0; }
</style>
```

En el cas de la informació d'usuari, des de qualsevol component (ja sigui la barra de navegació, el perfil o el *login*), pots importar i utilitzar el magatzem lliurement.

```vue
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

## 5. Bones Pràctiques

1. **No guardeu dades sensibles al LocalStorage:** Qualsevol *script* que s'executi a la pàgina pot llegir aquesta memòria. Mai hi guardeu contrasenyes, tokens crítics o targetes de crèdit.
2. **Vigileu la profunditat (Deep Watch):** A l'exemple anterior guardem *Strings* simples. Si el vostre estat és un Objecte complex o un Array (com una llista de la compra), cal afegir `{ deep: true }` al *watcher* perquè detecti canvis interns:
   ```javascript
   watch(meuArray, (nouValor) => {
     localStorage.setItem('clau', JSON.stringify(nouValor));
   }, { deep: true });
   ```
3. **Stores petits i específics:** És molt millor dividir l'estat en diversos fitxers (ex: `cart.js`, `preferences.js`, `user.js`) que tenir un únic fitxer gegant.


## 6. Com inspeccionar el LocalStorage al navegador

Per comprovar que les vostres dades s'estan guardant correctament o per fer proves, no us cal escriure codi addicional. Podeu veure i modificar el contingut del `LocalStorage` directament amb les eines de desenvolupador del vostre navegador.

**A Google Chrome / Microsoft Edge / Brave:**
1. Feu clic dret a qualsevol lloc de la vostra aplicació web i seleccioneu **Inspecciona** (o premeu `F12` / `Ctrl+Shift+I`).
2. A la finestra que s'obre, busqueu la pestanya **Application** (Aplicació). *(Nota: Si la pantalla és petita, potser heu de fer clic a la icona `>>` a la barra superior de les eines per veure aquesta pestanya).*
3. Al menú lateral esquerre, a la secció **Storage** (Emmagatzematge), desplegueu **Local Storage** i feu clic al vostre domini (normalment `http://localhost:5173` si esteu amb Vite).

**A Mozilla Firefox:**
1. Feu clic dret i seleccioneu **Inspecciona** (o premeu `F12`).
2. Aneu a la pestanya **Storage** (Emmagatzematge).
3. Desplegueu l'opció **Local Storage** al menú lateral esquerre i seleccioneu el vostre domini local.

**Què hi veureu?**
Al centre de la pantalla apareixerà una taula amb dues columnes principals:
* **Key (Clau):** El nom que heu posat a l'hora de guardar (ex: `app-theme`, `ticketflow-cart`).
* **Value (Valor):** El contingut guardat (sempre en format text o JSON).

💡 *Truc de depuració:* Podeu fer doble clic sobre qualsevol valor per editar-lo manualment o prémer la tecla `Suprimir` per esborrar-lo i veure com reacciona la vostra aplicació en recarregar la pàgina.

## 7. Referències i enllaços relacionats

* 🔗 [Documentació Oficial de Pinia: Core Concepts](https://pinia.vuejs.org/core-concepts/)
* 🔗 [MDN Web Docs: Window.localStorage](https://developer.mozilla.org/es/docs/Web/API/Window/localStorage)
* 🔗 [Vue.js: Watchers (Guia Oficial)](https://vuejs.org/guide/essentials/watchers.html)

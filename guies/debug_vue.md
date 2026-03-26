# Debugar Codi Vue.js

**Resum:** Trobar i solucionar errors ("bugs") és una part fonamental del desenvolupament web. En aquesta guia aprendrem a utilitzar les eines de desenvolupador del navegador, la consola, els punts d'interrupció i la indispensable extensió Vue DevTools per entendre què passa exactament dins la nostra aplicació i per què falla.

**Índex de continguts:**

1.  L'eina imprescindible: Vue DevTools.
2.  El clàssic `console.log()` i els Proxies de Vue.
3.  Pausar el temps amb `debugger`.
4.  Debugar peticions a l'API (Network Tab).
5.  Errors comuns a la consola i com llegir-los.
6.  Referències i enllaços relacionats.

-----

## 1\. L'eina imprescindible: Vue DevTools

La primera norma per desenvolupar amb Vue és instal·lar l'extensió oficial per al navegador: **Vue DevTools**. Et permet inspeccionar l'aplicació en temps real sense haver d'omplir el codi de `console.log()`.

**Instal·lació:**

  * Cerca "Vue DevTools" a la botiga d'extensions del teu navegador (Chrome Web Store, Firefox Add-ons, etc.) i instal·la-la.
  * Un cop instal·lada, obre la teva aplicació, fes clic dret \> **Inspecciona** i busca la nova pestanya anomenada **Vue**.

**Què hi pots fer?**

  * **Components:** Pots veure l'arbre de components de la teva pàgina. Si fas clic a un component (ex: `EventItem`), veuràs a la dreta totes les seves variables (`ref`), les *Props* que està rebent i el seu estat actual. Pots modificar aquests valors directament des d'allà per veure com reacciona la interfície\!
  * **Pinia:** Té una secció dedicada on pots veure el contingut en temps real de tots els teus *Stores* (com la cistella) i l'historial de canvis.
  * **Router:** Et permet veure quina és la ruta actual i quins paràmetres té.

## 2\. El clàssic `console.log()` i els Proxies de Vue

Imprimir variables per la consola és la tècnica de debugatge més antiga i utilitzada. Tanmateix, a Vue 3 hi ha un detall molt important que et pot confondre: **la reactivitat funciona amb Proxies**.

Si intentes fer un `console.log()` d'una variable reactiva (un `ref`), a la consola veuràs un objecte estrany ple de propietats internes com `[[Target]]` o `[[Handler]]`.

**Com fer-ho bé?**

1.  **Recorda el `.value`:** Si fas servir `ref`, el valor real sempre està a `.value`.

    ```javascript
    const comptador = ref(0);

    // ❌ MALAMENT: Et mostrarà l'objecte Proxy sencer
    console.log(comptador); 

    // ✅ BÉ: Et mostrarà només el número 0
    console.log(comptador.value); 
    ```

2.  **Per a objectes i arrays complexos:** Si imprimeixes un array reactiu d'esdeveniments i la consola et mostra un "Proxy", pots convertir-lo a text normal per llegir-lo fàcilment:

    ```javascript
    console.log(JSON.parse(JSON.stringify(meuArrayReactiu.value)));
    ```

    *A la versió més recent de Vue també pots importar i usar la funció `toRaw(meuArrayReactiu)` per obtenir l'objecte net.*

## 3\. Pausar el temps amb `debugger`

De vegades el codi s'executa tan ràpid que un `console.log` no és suficient per entendre l'ordre de les coses (per exemple, dins d'un bucle o d'una funció complexa).

Pots escriure la paraula `debugger;` en qualsevol lloc del teu codi Javascript:

```javascript
const calcularTotal = (cistella) => {
  let total = 0;
  debugger; // <-- EL NAVEGADOR ES PAUSARÀ AQUÍ!
  for (const item of cistella) {
    total += item.preu * item.quantitat;
  }
  return total;
};
```

**Com funciona?**

1.  Obre les Eines de Desenvolupador (DevTools) del navegador (F12).
2.  Fes alguna acció a la teva pàgina que executi aquest codi.
3.  El navegador es quedarà "congelat" exactament a la línia del `debugger`.
4.  A la pestanya **Sources**, podràs posar el ratolí a sobre de qualsevol variable per veure quin valor té en aquell mil·lisegon exacte i avançar línia per línia prement el botó `Step over` (F10).

## 4\. Debugar peticions a l'API (Network Tab)

Quan l'error no està a la teva lògica visual sinó a l'hora de comunicar-te amb el backend (Django/DRF), la pestanya **Network (Xarxa)** de les DevTools és el teu millor aliat.

1.  Obre DevTools i ves a la pestanya **Network**.
2.  Filtra per **Fetch/XHR** (per amagar imatges i estils i veure només les crides a l'API).
3.  Fes l'acció que falla (ex: prémer el botó "Comprar").
4.  Veuràs aparèixer la petició a la llista (normalment en vermell si ha fallat). Fes-hi clic.

**Què has de revisar allà dins?**

  * Pestanya **Headers (Capçaleres):** Comprova que la URL a la qual estàs cridant és la correcta (compte amb les barres diagonals al final `/`) i que l'estatus HTTP és l'esperat (200, 201, 400, 401...).
  * Pestanya **Payload / Request:** Aquí veuràs exactament les dades JSON que el teu Vue ha enviat al backend. Estan ben escrites? Falta algun camp?
  * Pestanya **Response / Preview (Resposta):** Aquí veuràs què t'ha contestat el backend. Si DRF t'ha retornat un error de validació (Status 400), aquí llegiràs exactament per què (ex: `{"titol": ["Aquest camp és obligatori."]}`).

## 5\. Errors comuns a la consola i com llegir-los

No tinguis por del text vermell a la consola (pestanya **Console**). Els errors estan dissenyats per ajudar-te. Llegeix sempre la primera línia i la primera línia del component afectat:

  * `Uncaught TypeError: Cannot read properties of undefined (reading 'titol')`: Això vol dir que estàs intentant accedir a `event.titol` dins del teu *template*, però en aquell moment `event` està buit o és `undefined`. Això passa molt quan demanes dades a l'API: el component es dibuixa *abans* que arribin les dades. *Solució: Usa un `v-if="event"` abans de dibuixar-lo.*
  * `Network Error` (en Axios): El teu frontend no pot contactar amb el backend. El servidor de Django està encès? El port és correcte? Tens problemes de CORS?
  * `[Vue warn]: Extraneous non-emits event listeners...`: Típic avís groc de Vue. Normalment passa si has afegit un `@click` a un component fill (com `<EventItem @click="...">`) però no ho has configurat correctament amb un `defineEmits()` dins d'ell.

## 6\. Referències i enllaços relacionats

  * 🔗 [Guia Oficial de Vue: Depuració (Debugging)](https://www.google.com/search?q=https://vuejs.org/guide/best-practices/debugging.html)
  * 🔗 [Vue DevTools: Repositori i documentació](https://devtools.vuejs.org/)
  * 🔗 [MDN Web Docs: Eines de desenvolupador (Network i Console)](https://developer.mozilla.org/es/docs/Learn/Common_questions/Tools_and_setup/What_are_browser_developer_tools)


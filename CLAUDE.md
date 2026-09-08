# Dr Iggy's — Free Design Tools

Este archivo es el contexto que Claude Code lee automáticamente al abrir esta carpeta. Léelo entero antes de tocar cualquier cosa — hay convenciones y trampas específicas de este proyecto que no son obvias a simple vista.

## Qué es esto

Un hub personal ("Dr Iggy's") de herramientas gratis, sin registro, hecho por y para un usuario no-programador que viene guiando el desarrollo por chat con Claude durante muchas sesiones. El estilo de trabajo hasta ahora: pedidos conversacionales, iteración visual constante, y mucho cuidado en no romper lo que ya funciona.

**Filosofía del proyecto — importante:**
- Todo tiene que seguir siendo **gratis** (ni para el usuario, ni idealmente para el dueño). No propongas soluciones pagas como primera opción.
- El usuario **no sabe programar**. No asumas que puede correr comandos de git/npm/etc. sin que se los expliques paso a paso, uno por vez, literal. Si le das varios comandos juntos, se pierde — pedilos de a uno.
- Cuando algo se puede verificar (renderizar, correr, probar), **verificalo antes de decir que funciona**. Este proyecto tiene un patrón establecido de usar Playwright (ya instalado en el entorno) para renderizar y probar cada cambio antes de entregarlo. No asumas que algo anda por leer el código — corré la app y mirá.

## Arquitectura

**Sin build step, sin framework, sin npm.** Cada página es un único archivo `.html` con `<style>` y `<script>` embebidos. Así se decidió a propósito, para que el usuario pueda editar/subir archivos sueltos sin entender de bundlers. **No introduzcas Vite/React/Webpack/etc. sin que el usuario lo pida explícitamente y entienda el cambio de flujo de trabajo que implica.**

### Archivos

| Archivo | Qué es | Estado |
|---|---|---|
| `index.html` | El hub — lista las herramientas disponibles | Terminado, en producción |
| `cuarto-oscuro.html` | **Free Online Film Scanner** — sube fotos de negativos, las recorta, revela e invierte el color | Terminado, en producción, muy probado |
| `photo-editor.html` | **Lite Photo Editor** — mini editor con capas, selección, pincel, ajustes tipo Lightroom | Recién armado, probado en local con Playwright, **nunca desplegado ni probado con RAW/IA reales** |
| `terms.html` | Términos de servicio | Terminado |
| `server_prod.py` | Backend Flask — sirve los HTML y decodifica archivos RAW vía `rawpy`/LibRaw | Terminado, en producción |
| `requirements.txt` | Dependencias Python | — |
| `Dockerfile` | Empaqueta todo para desplegar | Terminado — **usa `COPY . .` a propósito, no cambies esto a copiar archivos sueltos** (ver sección de trampas) |
| `robots.txt`, `sitemap.xml` | SEO básico | Terminado |
| `server.py` | Versión vieja para correr local sin Docker (no se usa en producción) | Puede estar desactualizada, no es prioridad |

## Identidad visual — no la cambies sin permiso explícito

Todo el sitio comparte una estética deliberada de **Windows XP retro** (ventanas con barra de título en degradado azul, botones biselados grises, tipografía Tahoma, fondo de paisaje SVG con lomas verdes y cielo celeste, bordes marcados). Esto fue una decisión de diseño muy discutida — en un momento se probó reemplazarlo por un estilo minimalista editorial y el usuario **lo rechazó explícitamente** y pidió volver atrás. No propongas "modernizar" la interfaz.

Colores/variables ya establecidos (reusalos, no inventes nuevos sin necesidad):
- Ventanas de herramientas: degradado azul (`--titlebar-1/2/3`: `#3E7BEB → #1E4FC4 → #0F3AA8`)
- Barra superior de marca ("Dr Iggy's" + "← More Tools"): degradado violeta (`--violet-1/2/3`: `#A88CF0 → #7452D6 → #4C2E9E`)
- Fondo de ventana: `#ECE9D8`, borde: `#0A246A`
- Fuente: `Tahoma, 'Segoe UI', Verdana, sans-serif`
- El fondo SVG de lomas+cielo se repite igual en las 4 páginas (buscá `<svg class="bg-scene"` para copiarlo tal cual a cualquier página nueva)

## Convenciones de código específicas de este proyecto

1. **i18n casero**: cada página tiene un objeto `I18N = { en:{...}, es:{...} }` y una función `t(key, vars)`. El idioma se guarda en `localStorage` bajo la clave `drIggyLang` y **se comparte entre todas las páginas** — si cambiás el idioma en una herramienta, tiene que reflejarse en las demás. Los botones de idioma son dos (`EN`/`ES`), no un toggle único.

2. **Botones de ventana funcionales**: `_` (minimizar) sale de pantalla completa, `▢` (maximizar) entra a pantalla completa, `×` es decorativo (no hace nada — los navegadores no dejan cerrar pestañas que no abriste por script, así que ni lo intentes).

3. **El `Dockerfile` usa `COPY . .`, no `COPY *.html .` ni listas de archivos.** Hubo un bug real y doloroso donde se listaban archivos por extensión y un archivo nuevo (`robots.txt`, `sitemap.xml`) no se copiaba al contenedor. No vuelvas a ese patrón.

4. **Despliegue**: la app corre en una VM de Google Cloud (`e2-micro`, capa gratuita), con Docker, detrás de Cloudflare (dominio `driggys.com`, modo SSL "Flexible"). El repo de GitHub tiene un Action (`.github/workflows/deploy.yml`) que hace SSH a la VM y corre `git pull && docker build && docker run` en cada push a `main`. **Ojo con `sudo` en ese script** — cuando se ejecuta sin terminal interactiva (como hace GitHub Actions), `sudo` pide contraseña y falla; el usuario en la VM ya tiene permiso de Docker sin `sudo`, así que el script de deploy no debe usar `sudo` en los comandos de `docker`.

5. **RAW**: el decodificado de archivos RAW (`.cr3`, `.nef`, `.arw`, etc.) pasa por un endpoint `/api/decode-raw` en `server_prod.py`, que usa `rawpy`. El navegador nunca decodifica RAW por su cuenta. Cualquier herramienta nueva que necesite abrir RAW debe pegarle a ese mismo endpoint (ya lo hace `photo-editor.html`, copiado de `cuarto-oscuro.html`).

6. **Traspaso de fotos entre herramientas**: hay un mecanismo con `IndexedDB` (base `drIggysHandoff`, store `images`, clave `pending`) para mandar una foto procesada de una herramienta a otra sin pasar por el servidor ni pedir que el usuario descargue/vuelva a subir. Mirá el botón "Edit in Photo Editor" en `cuarto-oscuro.html` (que escribe en la DB) y el `checkHandoff()` en `photo-editor.html` (que la lee al cargar) para el patrón exacto si agregás más herramientas.

7. **Nada de librerías de IA/ML sin verificar antes con un ejemplo real funcionando.** Hubo una saga larga y dolorosa tratando de meter super-resolución con modelos que resultaron no existir en las rutas documentadas, o eran para otro dominio (anime en vez de fotos reales), etc. Antes de integrar cualquier modelo/librería de IA nueva: buscá un ejemplo de código real y andando (no solo documentación oficial, que puede estar desactualizada), confirmá el nombre exacto del export/import, y probalo con Playwright antes de darlo por bueno. El único caso de IA ya integrado y con evidencia real de que el patrón funciona es `@imgly/background-removal` en `photo-editor.html` (import ES module directo desde jsDelivr).

## Cómo se prueban los cambios en este proyecto

El entorno tiene Playwright con Chromium instalado. El patrón usado durante todo el proyecto:
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1300,'height':900})
    errs = []
    page.on('pageerror', lambda e: errs.append(str(e)))
    page.goto('file:///ruta/al/archivo.html')
    # ...interactuar, hacer click, subir archivos con page.set_input_files()...
    page.screenshot(path='check.png', full_page=True)
    print(errs)
```
Usalo para cualquier cambio de UI o de lógica antes de decir que algo "ya funciona". El usuario no puede leer código para verificar — necesita ver capturas o texto de confirmación real.

**Nota**: `file://` bloquea algunos recursos (CDNs externos como jsDelivr a veces devuelven 403 bajo ese protocolo, IndexedDB puede comportarse distinto entre pestañas del mismo `file://`). Para probar RAW real hace falta el servidor Python corriendo (`python server_prod.py` o el `server.py` local), y para IA real hace falta estar en un origen `http(s)://` de verdad, no `file://`. Avisale esto al usuario si hace falta probar en la VM real en vez de local.

## Git y GitHub

Esta carpeta debería ser un `git clone` real del repositorio de GitHub del usuario (no solo una copia de archivos sueltos) — así podés hacer `git commit`/`git push` normalmente, y cada push a `main` dispara el despliegue automático descripto arriba (GitHub Actions → SSH a la VM → `git pull` + reconstruir Docker). Si notás que esta carpeta no tiene un `.git` (o sea, no es un repo real), avisale al usuario antes de asumir que podés pushear nada.

## Qué falta / próximos pasos conocidos

1. **`photo-editor.html` nunca se probó con RAW real ni con la función de "Remove Background (AI)" funcionando de punta a punta** (solo se armó el código y se probó la parte que no depende de red externa). Antes de darlo por terminado, probalo en un entorno con servidor + internet real.
2. **`photo-editor.html` todavía no está desplegado** — hay que subirlo al repositorio de GitHub (el pipeline de auto-deploy ya existente lo va a levantar solo).
3. El editor de fotos es una v1 acotada a propósito (así lo pidió el usuario): sin guardado de proyecto tipo `.psd`, sin capas con transformación/tamaño propio (todas las capas comparten el tamaño del documento), curva de tonos simplificada (interpolación lineal, no spline), sin marca/nombre de producto definitivo todavía.
4. El usuario puede pedir seguir sumando herramientas al hub — el patrón para agregar una nueva es: crear el `.html` con el mismo esqueleto visual (copiá el `<style>` y el `bg-scene` SVG de cualquier página existente), agregar su tarjeta en `index.html`, y si necesita RAW o cualquier otro endpoint de servidor, reusar `server_prod.py` en vez de crear un backend nuevo.

## Cómo interactuar con este usuario

- Explicaciones simples, sin jerga sin explicar.
- Si algo requiere que el usuario haga algo (subir un archivo, correr un comando, tocar la consola de Google Cloud), dale los pasos de a uno, bien explícitos, y esperá confirmación antes del siguiente.
- Si vas a tocar un archivo grande, mejor hacer ediciones puntuales (`str_replace`-style) que reescribirlo entero de una — ya pasó más de una vez que reescribir de cero introdujo bugs de tags mal cerrados que un editor puntual no hubiera causado.
- Sé honesto si algo no se puede verificar desde tu entorno (por ejemplo, no podés probar el sitio ya desplegado en `driggys.com` a menos que tengas acceso a internet real) — decilo en vez de asumir que algo va a andar.

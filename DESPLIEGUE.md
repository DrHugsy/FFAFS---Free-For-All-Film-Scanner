# Cuarto Oscuro Digital — poner la página en internet, gratis

Ya está todo armado (servidor, límites de seguridad, Docker). Esto es
la lista mínima de pasos que solo vos podés hacer (crear la cuenta,
pegar los comandos).

## Parte 1 — Crear el servidor gratis (una sola vez)

1. Andá a https://www.oracle.com/cloud/free/ y creá una cuenta ("Start
   for free"). Te va a pedir una tarjeta para verificar identidad, pero
   la capa "Always Free" no te cobra si te quedás dentro de esos límites.
2. Adentro de la consola, creá una instancia (botón "Create a VM instance").
   - Imagen: **Ubuntu 22.04** (la que viene por defecto sirve).
   - Shape (tipo de máquina): elegí **VM.Standard.E2.1.Micro** — es la
     chica, pero es la que garantiza que todo instale sin líos (la otra
     opción "Always Free", la ARM, es más potente pero puede darte
     dolores de cabeza con esta librería en particular).
   - Cuando te ofrezca descargar una "SSH key" o generar una, **generala
     y descargala** — es el archivo que vas a usar para entrar a la
     máquina.
   - Anotá la "Public IP Address" que te asigna una vez creada.
3. **Paso que casi todo el mundo se olvida en Oracle**: por defecto el
   firewall de Oracle bloquea todo. Andá a tu instancia → "Subnet" →
   "Security Lists" → la lista por defecto → "Add Ingress Rules", y
   agregá una regla que permita el puerto **80** (y opcionalmente 443)
   desde "0.0.0.0/0". Sin este paso, el servidor va a andar pero nadie
   de afuera va a poder entrar.

## Parte 2 — Conectarte a la máquina

En Windows, con PowerShell (o con PuTTY si preferís interfaz gráfica):

```
ssh -i ruta\a\tu-clave.key ubuntu@TU_IP_PUBLICA
```

## Parte 3 — Instalar Docker (copiar y pegar, una sola vez)

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```
Después de este último comando, cerrá la sesión SSH y volvé a entrar
(para que el permiso de Docker tome efecto).

## Parte 4 — Subir los archivos de la app

Desde tu PC (no desde la sesión SSH), en una terminal nueva, parado en
la carpeta donde tenés estos archivos:

```bash
scp -i ruta\a\tu-clave.key cuarto-oscuro.html server_prod.py Dockerfile requirements.txt ubuntu@TU_IP_PUBLICA:~
```

## Parte 5 — Construir y arrancar (copiar y pegar)

De nuevo en la sesión SSH del servidor:

```bash
docker build -t cuarto-oscuro .
docker run -d --restart unless-stopped -p 80:8000 --name cuarto-oscuro cuarto-oscuro
```

Listo. Entrá desde cualquier navegador a `http://TU_IP_PUBLICA` y
debería estar andando.

## Para actualizar la app más adelante

Repetís la Parte 4 (subir los archivos nuevos) y después:

```bash
docker stop cuarto-oscuro && docker rm cuarto-oscuro
docker build -t cuarto-oscuro .
docker run -d --restart unless-stopped -p 80:8000 --name cuarto-oscuro cuarto-oscuro
```

## Notas

- No hay HTTPS todavía (queda como `http://`, no `https://`). Funciona
  igual, pero el navegador va a avisar "no seguro". Si más adelante
  querés arreglar eso, se puede con un dominio gratis de DuckDNS +
  Let's Encrypt — avisame cuando llegues a ese punto y lo armamos.
- Ninguna foto que suba la gente queda guardada en el servidor: se
  procesa en memoria y se descarta apenas se envía la respuesta.
- Si con el tiempo ves que el servidor va lento (mucha gente a la vez),
  lo más simple es subir de shape en Oracle o de plan en otro proveedor
  — no hay que tocar el código para eso.

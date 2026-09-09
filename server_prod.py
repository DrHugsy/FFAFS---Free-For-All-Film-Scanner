"""
Cuarto Oscuro Digital — servidor de producción.

Igual que el server.py local, pero pensado para correr en un servidor
público en internet, no en tu PC:
  - Límite de tamaño de archivo (evita que alguien te tire abajo el
    servidor mandando un archivo gigante).
  - Límite de pedidos por IP por minuto (evita abuso/spam del servicio).
  - Nunca escribe las fotos de nadie en disco: todo pasa en memoria y se
    descarta apenas responde. Ninguna foto queda guardada en el servidor.
  - Pensado para correr detrás de gunicorn (varios workers), no con el
    servidor de desarrollo de Flask.

No necesitás tocar este archivo para nada de esto — ya viene configurado.
"""
import io
import os

from flask import Flask, request, send_file, send_from_directory, abort, redirect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import rawpy
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = "index.html"  # el hub Hugsy's es la página de inicio; FFAFS vive en cuarto-oscuro.html

app = Flask(__name__, static_folder=None)

# Nadie puede mandar un archivo de más de 80MB (un RAW normal pesa 20-50MB).
app.config["MAX_CONTENT_LENGTH"] = 80 * 1024 * 1024

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute", "300 per hour"],
    storage_uri="memory://",
)

RAW_EXTS = {".cr3", ".cr2", ".crw", ".nef", ".arw", ".raf", ".rw2", ".orf", ".dng", ".pef", ".srw"}
MAX_OUTPUT_DIM = 2400


# Nombres de archivo viejos que se renombraron — si alguien tiene un link o
# marcador guardado con la URL vieja, lo mandamos a la nueva (301).
OLD_SLUG_REDIRECTS = {
    "cuarto-oscuro.html": "/film-scanner",
    "cuarto-oscuro": "/film-scanner",
    "favicon-gen.html": "/favicon-generator",
    "favicon-gen": "/favicon-generator",
}


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, HTML_FILE)


@app.route("/<path:filename>")
def static_files(filename):
    if filename in OLD_SLUG_REDIRECTS:
        return redirect(OLD_SLUG_REDIRECTS[filename], code=301)

    full_path = os.path.abspath(os.path.join(BASE_DIR, filename))
    if not full_path.startswith(BASE_DIR):
        abort(404)
    if os.path.isfile(full_path):
        return send_from_directory(BASE_DIR, filename)

    # URL limpia sin extensión: /film-scanner -> sirve film-scanner.html.
    if not filename.endswith(".html"):
        html_path = full_path + ".html"
        if html_path.startswith(BASE_DIR) and os.path.isfile(html_path):
            return send_from_directory(BASE_DIR, filename + ".html")

    abort(404)


@app.route("/api/decode-raw", methods=["POST"])
@limiter.limit("20 per minute")
def decode_raw():
    if "file" not in request.files:
        return ("Falta el archivo en el pedido.", 400)

    uploaded = request.files["file"]
    ext = os.path.splitext(uploaded.filename or "")[1].lower()
    if ext not in RAW_EXTS:
        return (f"Extensión no soportada: {ext}", 400)

    data = uploaded.read()

    try:
        with rawpy.imread(io.BytesIO(data)) as raw:
            rgb = raw.postprocess(use_camera_wb=True)
    except Exception as e:  # noqa: BLE001 - mostramos el error real al usuario
        return (f"LibRaw no pudo decodificar '{uploaded.filename}': {e}", 422)

    img = Image.fromarray(rgb)

    if max(img.width, img.height) > MAX_OUTPUT_DIM:
        scale = MAX_OUTPUT_DIM / max(img.width, img.height)
        new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        img = img.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    # data, rgb e img se descartan acá; no queda nada guardado en el servidor.
    return send_file(buf, mimetype="image/png")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.errorhandler(413)
def too_large(e):
    return ("El archivo es demasiado grande (máximo 80MB).", 413)


@app.errorhandler(429)
def too_many(e):
    return ("Demasiados pedidos seguidos, esperá un minuto y probá de nuevo.", 429)

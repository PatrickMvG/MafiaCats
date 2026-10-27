import os
import random

from anyio.streams import file
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mafia Cats API")

IMAGE_DIR = "images"

# Statischen Ordner einbinden, damit Bilder per URL abrufbar sind
app.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

def get_images():
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    return [
        f for f in os.listdir(IMAGE_DIR)
        if os.path.splitext(f)[1].lower() in valid_extensions
    ]
@app.get("/")
def home():
    return {"message": "Willkommen bei der Mafia-Katzen-API! Nutze /random oder /random/url oder /cats oder /cats/idnummer"}

# 1. Liefert direkt die Bilddatei aus
@app.get("/random")
def get_random_image():
    images = get_images()
    if not images:
        raise HTTPException(status_code=404, detail="Keine Bilder gefunden")

    selected_image = random.choice(images)
    file_path = os.path.join(IMAGE_DIR, selected_image)
    return FileResponse(file_path)

# 2. Liefert ein JSON-Objekt mit der URL zum Bild
@app.get("/random/url")
def get_random_url(request: Request):
    images = get_images()
    if not images:
        raise HTTPException(status_code=404, detail="Keine Bilder gefunden")
    selected_image = random.choice(images)
    base_url = str(request.base_url).rstrip("/")
    return {
        "file_name": selected_image,
        "url": f"{base_url}/static/{selected_image}",
    }

# Alle verfügbaren Bilder auflisten
@app.get("/cats")
def list_all_cats(request: Request):
    images = sorted(get_images())
    base_url = str(request.base_url).rstrip("/")
    return {
        "total": len(images),
        "cats": [
            {
                "id": idx + 1,
                "filename": filename,
                "url": f"{base_url}/static/{filename}"
            }
            for idx, filename in enumerate(images)
        ]
    }


# Ein bestimmtes Bild anhand seiner ID (1-20) direkt anzeigen
@app.get("/cats/{cat_id}")
def get_cat_by_id(cat_id: int):
    images = sorted(get_images())

    # Prüfen, ob die ID im gültigen Bereich liegt
    if cat_id < 1 or cat_id > len(images):
        raise HTTPException(
            status_code=404,
            detail=f"Katze mit ID {cat_id} nicht gefunden. Gültige IDs: 1 bis {len(images)}."
        )

    selected_image = images[cat_id - 1]
    file_path = os.path.join(IMAGE_DIR, selected_image)
    return FileResponse(file_path)
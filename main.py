import os
import random

from anyio.streams import file
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
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
    return {
        "message": "Willkommen bei der Mafia-Katzen-API!",
        "url": "https://mafiacats.onrender.com/",
        "random" : "Nutze /random für ein random Bild",
        "catsAll": "Nutze /cats um das ganze JSON wiederzugeben",
        "catsSolo":"Nutze /cats/{1-15} um ein einzelnes bild auszugeben"
    }

# 1. Liefert direkt die Bilddatei aus
@app.get("/random")
def get_random_image():
    images = get_images()
    if not images:
        raise HTTPException(status_code=404, detail="Keine Bilder gefunden")

    selected_image = random.choice(images)
    file_path = os.path.join(IMAGE_DIR, selected_image)
    return FileResponse(file_path)

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
                ""
                "url": f"{base_url}/static/{filename}"
            }
            for idx, filename in enumerate(images)
        ]
    }





app.get("/cats/all", response_class=HTMLResponse)
def get_all_cats(request: Request):
    images = sorted(get_images())
    if not images:
        raise HTTPException(status_code=404, detail="Keine Bilder gefunden")

    base_url = str(request.base_url).rstrip("/")

    # Karten für jedes Bild generieren
    cards_html = "".join(
        f"""
        <div class="card">
            <a href="{base_url}/static/{img}" target="_blank">
                <img src="{base_url}/static/{img}" alt="Mafia Katze #{idx + 1}" loading="lazy">
            </a>
            <div class="caption">
                <span class="badge">#{idx + 1}</span>
                <span class="name">{img}</span>
            </div>
        </div>
        """
        for idx, img in enumerate(images)
    )

    # HTML-Seite mit CSS-Grid (3 Spalten)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mafia Cats Galerie</title>
        <style>
            :root {{
                --bg-color: #121212;
                --card-bg: #1e1e1e;
                --text-color: #f1f1f1;
                --accent-color: #e50914;
            }}
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                padding: 2rem 1rem;
            }}
            header {{
                text-align: center;
                margin-bottom: 2.5rem;
            }}
            header h1 {{
                font-size: 2.2rem;
                letter-spacing: 1px;
                margin-bottom: 0.5rem;
            }}
            header p {{
                color: #aaa;
                font-size: 1rem;
            }}
            /* 3-Spalten CSS Grid */
            .gallery-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 1.5rem;
                max-width: 1200px;
                margin: 0 auto;
            }}
            .card {{
                background-color: var(--card-bg);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                display: flex;
                flex-direction: column;
            }}
            .card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 24px rgba(229, 9, 20, 0.25);
            }}
            .card img {{
                width: 100%;
                height: 280px;
                object-fit: cover;
                display: block;
            }}
            .caption {{
                padding: 0.85rem 1rem;
                display: flex;
                align-items: center;
                gap: 0.6rem;
            }}
            .badge {{
                background: var(--accent-color);
                color: #fff;
                font-weight: bold;
                font-size: 0.8rem;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
            }}
            .name {{
                font-size: 0.9rem;
                color: #ddd;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            /* Responsiv: Auf kleineren Bildschirmen anpassen */
            @media (max-width: 900px) {{
                .gallery-grid {{
                    grid-template-columns: repeat(2, 1fr);
                }}
            }}
            @media (max-width: 550px) {{
                .gallery-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Mafia Cats Galerie</h1>
            <p>Insgesamt {len(images)} Katzen im Syndikat</p>
        </header>
        <main class="gallery-grid">
            {cards_html}
        </main>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


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
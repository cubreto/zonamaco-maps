# ZonaMaco 2026 VIP Maps

Interactive maps for ZonaMaco 2026 art week events in Mexico City.

**99 curated events** | **7 days** | **45+ venues** | **Feb 2-8, 2026**

## Quick Preview

- Blue markers = Público (public events)
- Orange markers = Privado (private/invitation only)

## Deploy in 1 Click

### Option 1: GitHub Pages (Easiest - Static)

1. Fork this repo or create new:
```bash
gh repo create zonamaco-maps --public
cd zonamaco-app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/zonamaco-maps.git
git push -u origin main
```

2. Go to repo Settings → Pages → Source: `main` branch, folder: `/static/maps`

3. Your site will be live at: `https://YOUR_USERNAME.github.io/zonamaco-maps/`

### Option 2: Render.com (Free - Recommended)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Settings auto-detected from `render.yaml`
5. Click Deploy

### Option 3: Vercel (Free)

```bash
npm i -g vercel
cd zonamaco-app
vercel
```

### Option 4: Heroku

```bash
heroku create zonamaco-maps
git push heroku main
heroku open
```

### Option 5: Railway.app (Free tier)

1. Go to [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. Select this repo
4. Auto-deploys!

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py

# Open http://localhost:5000
```

## Regenerate Maps

If you need to update events:

```bash
# Edit events in zonamaco_mapper.py
python zonamaco_mapper.py

# Maps regenerated in static/maps/
```

## Project Structure

```
zonamaco-app/
├── app.py                    # Flask web server
├── zonamaco_mapper.py        # Map generator script
├── requirements.txt          # Python dependencies
├── Procfile                  # Heroku config
├── runtime.txt               # Python version
├── vercel.json              # Vercel config
├── render.yaml              # Render.com config
└── static/
    └── maps/
        ├── index.html        # Main navigation
        ├── 2026-02-02_Lunes.html
        ├── 2026-02-03_Martes.html
        ├── 2026-02-04_Miércoles.html
        ├── 2026-02-05_Jueves.html
        ├── 2026-02-06_Viernes.html
        ├── 2026-02-07_Sábado.html
        └── 2026-02-08_Domingo.html
```

## Features

- Interactive Leaflet maps with multiple tile layers
- Color-coded markers by event type
- Venue type icons (Museum, Gallery, Hotel, etc.)
- Timeline sidebar with chronological events
- Animated route between venues
- Search and filter on index page
- Responsive design for mobile

## Tech Stack

- **Maps**: Folium (Leaflet.js wrapper)
- **Backend**: Flask + Gunicorn
- **Styling**: Custom CSS with Goldman Sachs-inspired light theme
- **Icons**: Font Awesome

## License

MIT - Free to use and modify

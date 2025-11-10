from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ---- Spotify Credentials ----
# Spotify Client Id: a69524a6bec24a26a580067a2e0d4105
# Spotify Client Secret: 28b6926ce7fc470b9b7751c825b74008

# Spotify Client Id: 9997674c00f544ddb302edb260395de0
# Spotify Client Secret: d3ce6da2d02143a39a08abb9b195e78d
id = "9997674c00f544ddb302edb260395de0"
secret = "d3ce6da2d02143a39a08abb9b195e78d"

SPOTIFY_CLIENT_ID = id
SPOTIFY_CLIENT_SECRET = secret

# ---- Helper: Get Spotify Access Token ----
def get_spotify_token():
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET),
    )
    auth_response.raise_for_status()
    return auth_response.json()["access_token"]

# ---- Helper: Fetch Songs ----
def fetch_spotify_songs(artist=None, track=None, album=None, genre=None, limit=10):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    search_url = "https://api.spotify.com/v1/search"

    # Build Spotify query string dynamically
    query_parts = []
    if artist:
        query_parts.append(f"artist:{artist}")
    if track:
        query_parts.append(f"track:{track}")
    if album:
        query_parts.append(f"album:{album}")
    if genre:
        query_parts.append(f"genre:{genre}")

    # Fallback to default if no query provided
    query = " ".join(query_parts) if query_parts else "artist:Sumit Goswami"

    params = {
        "q": query,
        "type": "track",
        "limit": limit
    }

    print(f"query : {query} \n params: {params}")

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    print(f"url : {response.url}")
    data = response.json()

    songs = []
    for item in data["tracks"]["items"]:
        # Only include songs with preview or embed URL
        if item.get("id"):
            songs.append({
                "name": item["name"],
                "artist": item["artists"][0]["name"],
                "preview_url": item.get("preview_url"),
                "embed_url": f"https://open.spotify.com/embed/track/{item['id']}"
            })
    return songs

# def fetch_spotify_songs(query="Sumit Goswami", limit=10):
#     token = get_spotify_token()
#     headers = {"Authorization": f"Bearer {token}"}
#     search_url = "https://api.spotify.com/v1/search"

#     params = {
#         "q": f"artist:{query}",
#         "type": "track",
#         "limit": limit
#     }

#     response = requests.get(search_url, headers=headers, params=params)
#     response.raise_for_status()
#     data = response.json()

#     songs = []
#     for item in data["tracks"]["items"]:
#         obj = {
#             "name": item["name"],
#             "artist": item["artists"][0]["name"],
#             "preview_url": item["preview_url"],  # may be None
#             "embed_url": f"https://open.spotify.com/embed/track/{item['id']}"  # ✅ add this
#         }
#         print(f"\n\n {obj} \n\n")
#         songs.append(obj)
#     return songs

# ---- API Route: Home Page ----
from fastapi import Query

@app.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    artist: str = Query(None),
    track: str = Query(None),
    album: str = Query(None),
    genre: str = Query(None),
    limit: int = Query(5)
):
    """
    Fetch songs from Spotify based on optional filters:
    artist, track, album, genre. Default limit is 10.
    """
    songs = fetch_spotify_songs(artist=artist, track=track, album=album, limit=limit)
    return templates.TemplateResponse("index.html", {"request": request, "songs": songs})


# ---- Main entry point ----
if __name__ == "__main__":
    # Runs the FastAPI app on localhost:8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

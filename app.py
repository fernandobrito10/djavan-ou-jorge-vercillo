from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import random

app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    
    # Adicione essa linha para imprimir o status da requisição e a resposta
    print("Status code:", result.status_code)
    print("Resposta:", result.content)

    # Verifique se a resposta foi bem-sucedida antes de tentar decodificar
    if result.status_code != 200:
        raise Exception("Erro na requisição à API do Spotify.")

    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


artist_ids = ["5rrmaoBXZ7Jcs4Qb77j0YA", "783AF57UpgTN2fditDRFSs"]

def get_albums_from_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro ao buscar álbuns: {response.content}")
        return None

    albums = response.json().get("items", [])
    return albums



def get_tracks_from_album(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro ao buscar músicas do álbum: {response.content}")
        return None

    tracks = response.json()["items"]
    
    max_attempts = 10
    for _ in range(max_attempts):
        random_track = random.choice(tracks)
        if random_track.get("preview_url"):
            return random_track
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play-random', methods=["POST"])
def play_random():
    token = get_token()
    artist_id = random.choice(artist_ids)
    print(f"Artista escolhido: {artist_id}")

    albums = get_albums_from_artist(token, artist_id)
    if not albums:
        return "Erro ao obter álbuns do artista."

    album = random.choice(albums)
    print(f"Álbum escolhido: {album['name']}")

    if album:
        track = get_tracks_from_album(token, album["id"])
        if track:
            artista = "Djavan" if artist_id == "5rrmaoBXZ7Jcs4Qb77j0YA" else "Jorge Vercillo"
            return jsonify({
                "preview_url": track["preview_url"],
                "artista": artista,
                "track": track["name"],
                "message": f"Tocando: {track['name']} por {track['artists'][0]['name']}"
            })
    
    return jsonify({"error": "Nenhuma música disponível com preview."})


if __name__ == "__main__":
    app.run(debug=True)
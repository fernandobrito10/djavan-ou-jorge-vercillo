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

def get_random_track_from_artist(token, artist_id):
    # Passo 1: Buscar todos os álbuns do artista
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&market=US&limit=50"
    headers = {"Authorization": f"Bearer {token}"}
    response = get(url, headers=headers)

    if response.status_code != 200:
        return None

    albums = response.json()["items"]

    # Passo 2: Escolher um álbum aleatório
    random_album = random.choice(albums)

    # Passo 3: Buscar todas as músicas do álbum escolhido
    album_id = random_album["id"]
    tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    tracks_response = get(tracks_url, headers=headers)

    if tracks_response.status_code != 200:
        return None

    tracks = tracks_response.json()["items"]

    # Passo 4: Escolher uma música aleatória do álbum
    random_track = random.choice(tracks)
    return random_track


def play_track(token, track_uri):
    url = "https://api.spotify.com/v1/me/player/play"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Verificar se há um dispositivo disponível
    device_url = "https://api.spotify.com/v1/me/player/devices"
    device_response = get(device_url, headers=headers)
    
    devices = device_response.json().get("devices", [])
    if not devices:
        return "Nenhum dispositivo disponível para reprodução."

    # Tocar a música no dispositivo ativo
    data = {"uris": [track_uri]}
    response = post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        return "Tocando música!"
    else:
        return f"Erro ao tocar música. Status: {response.status_code}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play-random', methods=["POST"])
def play_random():
    token = get_token()  # Corrigir a chamada para obter o token

    # Escolher aleatoriamente um dos dois artistas
    artist_id = random.choice(artist_ids)
    
    # Buscar uma música aleatória do artista
    track = get_random_track_from_artist(token, artist_id)
    
    if track and track['preview_url']:
        # Retornar o preview_url para ser tocado na aplicação
        return jsonify({
            "track_name": track['name'],
            "artist_name": track['artists'][0]['name'],
            "preview_url": track['preview_url']
        })
    
    return jsonify({"error": "Erro ao tocar música."})

if __name__ == "__main__":
    app.run(debug=True)
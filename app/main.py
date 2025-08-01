from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import datetime
import os

API_KEY = os.getenv("API_KEY")
templates = Jinja2Templates(directory="templates")
app = FastAPI()

def buscar_jogos():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {"x-apisports-key": API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    sinais = []

    for jogo in data.get("response", []):
        fixture = jogo.get("fixture", {})
        teams = jogo.get("teams", {})
        goals = jogo.get("goals", {})
        league = jogo.get("league", {})
        gols_total = (goals.get("home") or 0) + (goals.get("away") or 0)
        horario = datetime.datetime.fromtimestamp(fixture.get("timestamp", 0)).strftime("%H:%M")
        chance_over = 0.65 if gols_total == 0 else 0.80
        odd_betano = 2.10
        valor = chance_over * odd_betano
        if valor > 1:
            sinais.append({
                "jogo": f"{teams['home']['name']} x {teams['away']['name']}",
                "mercado": "Over 2.5 gols",
                "prob": int(chance_over * 100),
                "odd": odd_betano,
                "valor": round(valor, 2),
                "horario": horario,
                "liga": league.get("name", "")
            })
    return sinais

@app.get("/", response_class=HTMLResponse)
def pagina(request: Request):
    sinais = buscar_jogos()
    return templates.TemplateResponse("index.html", {"request": request, "sinais": sinais})
      


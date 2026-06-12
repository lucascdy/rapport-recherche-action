# Générateur de Rapport de Recherche Action

Application web qui génère des rapports de recherche action au format broker
institutionnel, rédigés par Claude (`claude-sonnet-4-6`).

**Démo en ligne :** https://coudy-rapport-action.onrender.com

## Architecture

- **Front** : page HTML/CSS/JS autonome (`index.html`), sans framework ni build.
- **Back** : mini-serveur FastAPI (`server.py`) qui sert la page et relaie les
  requêtes de génération vers l'API Anthropic. La clé API reste **côté
  serveur** (variable d'environnement `ANTHROPIC_API_KEY`) — elle n'est jamais
  exposée au navigateur.
- **Anti-abus** : limite de 10 générations par heure et par adresse IP.
- **Streaming** : la réponse de Claude est streamée jusqu'au navigateur pour
  éviter les timeouts sur les générations longues.

## Lancement local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
uvicorn server:app --reload
```

Puis ouvrir http://localhost:8000

## Déploiement

Le fichier `render.yaml` décrit le service pour [Render](https://render.com)
(Blueprint). Seule configuration requise : la variable `ANTHROPIC_API_KEY`.

## Stack

HTML / CSS / JavaScript vanilla · FastAPI · API Anthropic (Messages API,
streaming) · Render

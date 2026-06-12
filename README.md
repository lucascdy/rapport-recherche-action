# Générateur de Rapport de Recherche Action

Application web autonome (HTML/CSS/JS, sans serveur) qui génère des rapports de
recherche action au format broker institutionnel, rédigés par Claude
(`claude-sonnet-4-6`).

**Démo en ligne :** https://lucascdy.github.io/rapport-recherche-action/

## Fonctionnement

- L'utilisateur saisit les informations de base de la société et sa clé API
  Anthropic (`sk-ant-...`).
- La clé reste **locale** (stockée dans le navigateur, envoyée uniquement à
  `api.anthropic.com`) — aucun serveur intermédiaire.
- Claude rédige l'analyse complète en français : thèse d'investissement,
  données financières, valorisation, risques.

## Stack

HTML / CSS / JavaScript vanilla · API Anthropic (Messages API, appel direct
navigateur) · Aucune dépendance, aucun build.

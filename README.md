# Stellantis MCP Intelligent Agent - Embedded Configuration Analyzer

## Vue d’ensemble du projet

Ce projet implémente un agent intelligent basé sur le **Model Context Protocol (MCP) Python SDK** combiné à un modèle de langage local exécuté via **Ollama**.

Le système démontre comment un agent IA peut découvrir un outil exposé par un serveur MCP, utiliser cet outil pour accéder à une ressource locale, puis exploiter le résultat obtenu afin de générer une réponse structurée.

L'architecture reproduit le fonctionnement attendu dans l'exercice technique en séparant clairement les responsabilités :

* Le serveur MCP expose un outil unique.
* Le client orchestre les échanges entre le LLM et le serveur MCP.
* Le LLM analyse le contenu récupéré via l'outil et produit le résumé final.
* Aucune plateforme cloud n'est utilisée ; l'ensemble du système fonctionne localement.

---

## Objectif

L'objectif de ce projet est de démontrer :

* L'utilisation du protocole MCP (Model Context Protocol).
* L'intégration d'un modèle local via Ollama.
* La mise en œuvre manuelle du cycle Tool Calling sans LangChain, LlamaIndex ou AutoGen.
* La lecture d'un fichier de configuration industriel.
* La génération d'un résumé structuré en trois points.
* Le respect de l'architecture imposée dans l'énoncé.

---

## Architecture Générale

```text
Utilisateur
     │
     ▼
client.py
     │
     ▼
LLM Local (Ollama)
     │
     ▼
Décision d'utiliser un outil
     │
     ▼
Serveur MCP (server.py)
     │
     ▼
read_file(path)
     │
     ▼
test_data/config.yaml
     │
     ▼
Contenu du fichier
     │
     ▼
LLM
     │
     ▼
Résumé final
```

---

## Structure du Projet

```text
stellantis-mcp-agent/
├── screenshots/
├── test_data/
│   └── config.yaml
├── .gitignore
├── client.py
├── server.py
├── requirements.txt
└── README.md
```

---

## Serveur MCP

Le fichier `server.py` implémente un serveur MCP utilisant le SDK officiel Python.

Le serveur expose un unique outil :

### read_file

Entrée :

```json
{
  "path": "test_data/config.yaml"
}
```

Sortie :

```text
Contenu brut du fichier demandé
```

Fonctionnalités :

* Lecture d'un fichier local.
* Retour du contenu sous forme de chaîne de caractères.
* Gestion des erreurs si le fichier n'existe pas.
* Communication via le transport stdio conformément à l'énoncé.

---

## Client MCP

Le fichier `client.py` joue le rôle d'orchestrateur principal.

Responsabilités :

1. Démarrer automatiquement le serveur MCP.
2. Établir une connexion MCP via stdio.
3. Découvrir les outils disponibles.
4. Envoyer une requête au modèle local.
5. Détecter la demande d'utilisation de l'outil.
6. Exécuter l'outil `read_file`.
7. Récupérer le contenu du fichier.
8. Fournir ce contenu au modèle.
9. Générer le résumé final.
10. Afficher le résultat dans le terminal.

---

## Données de Test (test_data/config.yaml)

Le fichier de configuration réseau de l'ECU (Battery Management System) utilisé pour la validation contient les paramètres suivants :

```yaml
# ECU Network Configuration - BMS Project v2.1

network:
  protocol: CAN-FD
  baudrate: 500000
  node_id: 0x1A
  timeout_ms: 150

logging:
  level: WARNING
  output: /var/log/bms_agent.log
  rotate_every_mb: 50

safety:
  watchdog_enabled: true
  max_retry: 3
  fail_safe_mode: SHUTDOWN
```

## Instructions d'Installation et Exécution (Moins de 5 minutes)

Suivez ces étapes séquentielles pour reproduire l'exécution complète de l'agent en local.

### 1. Préparation du modèle local

Assurez-vous qu'Ollama est actif sur votre machine, puis téléchargez le modèle requis :

```bash
ollama pull qwen2:1.5b
```

### 2. Installation des dépendances Python

```bash
pip install -r requirements.txt
```

### 3. Exécution de l'agent

```bash
python client.py
```

## Format de Sortie Obtenu

```text
===== AGENT FINAL OUTPUT =====

- NETWORK: CAN-FD, baudrate set to 500000, node ID 0x1A, timeout of 150ms
- LOGGING: WARNING level, rotation every 50MB
- SAFETY: Watchdog enabled, maximum retries 3, fail-safe SHUTDOWN
```

## Gestion des Erreurs

Le projet intègre plusieurs mécanismes de robustesse :

* Vérification de l'existence du fichier demandé.
* Gestion des exceptions lors de la lecture.
* Validation des réponses du modèle.
* Contrôle des appels d'outils MCP.
* Fermeture propre du serveur à la fin de l'exécution.

---

## Respect de l'Énoncé

Cette implémentation respecte les exigences imposées :

* Utilisation d'un modèle local inférieur à 4 milliards de paramètres.
* Utilisation du protocole MCP.
* Utilisation du transport stdio.
* Outil unique `read_file`.
* Aucune utilisation de LangChain.
* Aucune utilisation de LlamaIndex.
* Aucune utilisation d'AutoGen.
* Orchestration réalisée manuellement.
* Lecture du fichier via MCP et non directement depuis le client.
* Génération d'un résumé final en trois points.

---

## Conclusion

Ce projet met en œuvre un agent IA local capable d'interagir avec des ressources système à travers le protocole MCP. L'architecture sépare clairement les responsabilités entre le raisonnement du modèle, l'accès aux ressources locales et l'orchestration applicative.

Cette approche reproduit les principes utilisés dans les systèmes industriels modernes où les modèles d'intelligence artificielle doivent accéder à des données réelles via des interfaces contrôlées, sécurisées et traçables.

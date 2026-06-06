# MCP Tool-Enabled LLM Agent (Assistant de lecture de fichiers)

## Vue d’ensemble du projet

Ce projet implémente un agent intelligent basé sur le **Model Context Protocol (MCP) SDK** combiné à un **modèle de langage local (Ollama - Qwen2)**.

Le système démontre comment un agent IA peut :
- décider dynamiquement d’utiliser un outil externe,
- exécuter cet outil de manière sécurisée,
- exploiter le résultat pour générer une réponse structurée.

L’agent permet de :
- démarrer un serveur MCP,
- communiquer avec un LLM local,
- détecter le besoin d’un outil,
- exécuter le tool `read_file` via MCP SDK,
- lire des fichiers locaux de configuration,
- générer un résumé structuré des données.

Ce projet simule une architecture d’agent IA utilisée dans les systèmes industriels, embarqués et les pipelines d’automatisation.

---

## Objectif

L’objectif principal est de construire un agent IA fiable et déterministe capable de :

- utiliser le SDK officiel MCP (Model Context Protocol),
- interagir avec un LLM local (Qwen2 via Ollama),
- exécuter des outils externes au lieu d’inventer des réponses,
- lire des fichiers de configuration structurés (`test_data/config.yaml`),
- produire une sortie strictement formatée (3 bullet points),
- implémenter un pipeline complet de tool-calling.

---

## Architecture du système

Utilisateur → client.py → LLM (Ollama - Qwen2)
                     ↓
             Détection du besoin d’outil
                     ↓
             Serveur MCP (server.py)
                     ↓
             Système de fichiers (config.yaml)
                     ↓
             Retour du contenu du fichier
                     ↓
        Génération du résumé final par le LLM

---

## Serveur MCP (server.py)

Le serveur MCP expose un seul outil :

### Tool : read_file(path: str)

Fonctionnalités :
- lecture d’un fichier local,
- retour du contenu brut sous forme de texte,
- exposition sécurisée via MCP SDK,
- exécution uniquement sur demande du client.

---

## Fonctionnement du client (client.py)

Le client suit un pipeline strict :

1. Démarrer le serveur MCP en sous-processus  
2. Se connecter au serveur via stdio_client  
3. Récupérer la liste des outils disponibles  
4. Envoyer une requête au LLM  
5. Analyser la réponse pour détecter l’outil et le chemin du fichier  
6. Exécuter l’outil `read_file` via MCP  
7. Récupérer le contenu du fichier  
8. Envoyer le contenu au LLM  
9. Forcer une sortie structurée (3 bullet points)  
10. Valider et formater le résultat final  

---

## Fichier d’entrée (test_data/config.yaml)

ECU Network Configuration BMS Project v2.1

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

---

## Format de sortie attendu

- NETWORK : CAN-FD, 500000 baud, node 0x1A, timeout 150ms  
- LOGGING : WARNING level, sortie /var/log/bms_agent.log, rotation 50MB  
- SAFETY : watchdog activé, max retry 3, mode fail-safe SHUTDOWN  

---

## Fonctionnalités principales

- Intégration du SDK officiel MCP  
- Raisonnement IA basé sur des outils  
- Prompt engineering strict  
- Sortie déterministe et structurée  
- Séparation entre LLM et exécution système  
- Accès fichier sécurisé via tool uniquement  

---

## Sécurité et fiabilité

- Le LLM n’a pas accès direct au système de fichiers  
- Toutes les lectures passent par un outil MCP  
- L’exécution des outils est contrôlée par le client  
- Les sorties sont validées et nettoyées  
- Gestion de robustesse en cas d’erreur  

---

## Améliorations possibles

- Ajout de nouveaux outils (write_file, list_dir, search_files)  
- Support du streaming LLM  
- Amélioration du parsing des outils (JSON structuré)  
- Ajout d’un système de logs avancé  
- Conteneurisation avec Docker  
- Passage à une architecture asynchrone complète  

---

## Lancement du projet

python client.py

Conditions requises :
- SDK MCP installé
- Ollama en cours d’exécution
- fichier config.yaml présent dans test_data/

---

## Conclusion

Ce projet démontre une architecture complète d’agent IA basé sur MCP combinant :

- raisonnement via LLM,
- utilisation d’outils externes,
- interaction avec le système de fichiers,
- contrôle strict de la structure des réponses.

Il constitue une base solide pour des systèmes IA industriels utilisés dans l’automatisation, les systèmes embarqués et les agents intelligents.
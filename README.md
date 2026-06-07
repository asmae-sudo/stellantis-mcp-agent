# Stellantis MCP Intelligent Agent - Embedded Configuration Analyzer

## Vue d’ensemble du projet

Ce projet implémente un agent intelligent basé sur le (Model Context Protocol (MCP) Python SDK)combiné au modèle de langage local (Qwen2.5). 

Le système démontre comment un agent IA peut décider de manière autonome d’utiliser un outil système externe, exécuter cet outil de manière sécurisée via un canal de transport standard, et exploiter le résultat pour générer une réponse structurée et déterministe.

Cette architecture découplée simule les exigences de robustesse et de sécurité appliquées aux systèmes industriels et aux architectures embarquées (calculateurs d'automobiles, systèmes de gestion de batterie - BMS).



## Objectif

L’objectif de cet agent est de valider les critères techniques suivants :
- Utilisation exclusive du SDK officiel MCP (Model Context Protocol) pour l'orchestration.
- Interation avec un LLM local d'une taille strictement inférieure à 4 milliards de paramètres (≤ 4B params).
- Exécution d'un outil système réel au lieu de générer des hallucinations textuelles.
- Lecture et analyse d'un fichier de configuration industriel structuré (test_data/config.yaml).
- Production d'une sortie strictement restreinte à 3 points clés, conforme aux exigences de validation.

---

## Architecture du système

                Utilisateur → client.py → LLM (Ollama - Qwen2.5)
                        ↓
                Détection du besoin d’outil (Tool Calling)
                        ↓
                Serveur MCP (server.py)
                        ↓
                Système de fichiers (config.yaml)
                        ↓
                Retour du contenu du fichier
                        ↓
                Génération du résumé final par le LLM
                

## Note Technique : Justification du Choix du Modèle

Initialement prévu avec le modèle `qwen2:1.5b` mentionné à titre d'exemple dans le sujet, l'implémentation utilise explicitement le modèle **`qwen2.5:1.5b`**. 

**Justification technique :** La version antérieure `qwen2:1.5b` sous Ollama ne prend pas nativement en charge le paramètre `tools` via l'API standard d'Ollama, provoquant un rejet systématique de la requête (Erreur HTTP 400 Bad Request). Le modèle mis à jour `qwen2.5:1.5b`, bien que conservant une empreinte mémoire ultra-légère ($1,5$ milliard de paramètres) parfaitement adaptée aux contraintes locales de l'exercice (≤ 4B params), a été spécifiquement entraîné pour le *Tool Calling*. Ce choix garantit un déclenchement 100% autonome et fiable de l'outil MCP.

---

## Configuration du Serveur MCP (server.py)

Le serveur MCP utilise le SDK Python officiel et expose un outil unique via un canal de transport standardisé `stdio` :

### Outil : `read_file`
- **Description** : Permet la lecture sécurisée d'un fichier local.
- **Paramètres d'entrée** : `{ "path": "<relative_path>" }`
- **Sortie** : Contenu brut du fichier sous forme de chaîne de caractères (`string`).
- **Fiabilité** : Intègre une gestion des exceptions pour retourner un message explicite si le fichier demandé est introuvable.

---

## Fonctionnement du Client (client.py)

Le script client réalise l'orchestration manuelle (*wired by hand*, sans framework de haut niveau comme LangChain ou AutoGen) selon le cycle suivant :
1. Lancement du script serveur comme sous-processus de manière asynchrone.
2. Établissement de la session MCP via le canal de transport bidirectionnel standard (`stdin/stdout`).
3. Découverte dynamique des outils exposés par le serveur et conversion de leur schéma au format attendu par Ollama.
4. Envoi de la requête utilisateur initiale au modèle local.
5. Analyse de la réponse du modèle et extraction automatique de la demande d'appel d'outil (`tool_calls`).
6. Exécution de l'action de lecture de fichier par le serveur MCP.
7. Injection du contenu lu dans l'historique des messages pour maintenir le contexte.
8. Second passage au LLM avec des directives système strictes pour verrouiller le formatage de la réponse.

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
  

Instructions d'Installation et Exécution (Moins de 5 minutes)
Suivez ces étapes séquentielles pour reproduire l'exécution complète de l'agent en local.

1. Préparation du modèle local
Assurez-vous que l'application Ollama est active sur votre machine, puis téléchargez le modèle requis depuis votre terminal :

Bash
ollama pull qwen2.5:1.5b
2. Installation des dépendances Python
Installez l'ensemble des bibliothèques logicielles nécessaires stockées dans le fichier de gestion des dépendances :

Bash
pip install -r requirements.txt
3. Exécution de l'agent
Lancez l'orchestrateur principal via la commande unique suivante :

Bash
python client.py
Format de Sortie Obtenu
L'exécution réussie du pipeline produit l'affichage déterministe suivant au sein du terminal :

Plaintext
===== AGENT FINAL OUTPUT =====
- NETWORK: CAN-FD, baudrate set to 500000, node with ID 0x1A, timeout of 150ms
- LOGGING: Log messages at WARNING level and rotated when reaching 50MB in size
- SAFETY: Watchdog feature enabled, maximum retries are 3 times, failure is handled by SHUTDOWN mode


Conclusion
Ce projet démontre la viabilité et l'efficacité du protocole ouvert MCP pour découpler le raisonnement de l'IA de l'exécution des privilèges système. En limitant l'accès aux ressources via des outils contrôlés et en encadrant strictement le cycle de communication, l'architecture garantit une intégration logicielle prévisible, sécurisée et performante, répondant parfaitement aux standards requis par l'industrie.
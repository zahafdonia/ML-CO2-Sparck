# 🚀 Pipeline de Machine Learning Temps Réel – Architecture Kappa

## 📑 Table des Matières
1. Description du Projet  
2. Architecture du Projet  
3. Guide d’Installation  
   - Pré-requis  
   - Clonage du Projet  
   - Démarrage des Conteneurs  
4. Lancement du Pipeline  
   - API de Streaming  
   - Producteur Kafka  
   - Consommateur Spark  
   - Visualisation du RMSE  
   - Prédictions en Temps Réel  
5. Technologies Utilisées  
6. Structure du Projet  
7. Résultats et KPI  

---

## 1. Description du Projet

Ce projet implémente un **pipeline de Machine Learning en temps réel** basé sur l’**architecture Kappa**.  
Il permet de traiter un flux continu de données liées aux émissions de CO₂ des véhicules et d’effectuer :

- La diffusion de données depuis un fichier CSV via une API
- Le streaming des données avec Apache Kafka
- L’entraînement incrémental d’un modèle de Machine Learning avec Apache Spark
- Le suivi en temps réel des performances du modèle
- La prédiction interactive des émissions de CO₂

L’ensemble du système est **entièrement containerisé** et orchestré avec **Docker Compose**.

---

## 2. Architecture du Projet

Le projet suit une **architecture Kappa**, dans laquelle une seule chaîne de traitement streaming est utilisée pour :

- Les données historiques
- Les données temps réel

### Composants principaux :

- **FastAPI** : API de streaming des données CSV
- **Apache Kafka** : transport des messages en temps réel
- **Zookeeper** : coordination de Kafka
- **Apache Spark Structured Streaming** : traitement et entraînement du modèle
- **Scikit-learn** : modèle de régression incrémental (SGDRegressor)
- **Streamlit** : visualisation et interface utilisateur

---

## 3. Guide d’Installation

### 3.1 Pré-requis

- Docker Desktop installé
- Docker Compose disponible
- Au moins 8 Go de RAM recommandés

Vérification :

```bash
- docker --version
- docker-compose --version
### 3.2 Démarrage des Conteneurs

Lancer tous les services avec Docker Compose :

```bash
docker-compose up -d

- Les services suivants sont démarrés automatiquement :

- Zookeeper

- Kafka

- API de streaming

- Producteur Kafka

- Consommateur Spark

- Interface Streamlit

## 4.Lancement du Pipeline
### 4.1 API de Streaming

Endpoint exposé :

GET http://localhost:8000/stream


Fonctionnement :

Lecture du fichier CSV

Diffusion des données ligne par ligne en continu

### 4.2 Producteur Kafka

Rôle du producteur :

Consommer le flux HTTP depuis l’API

Publier les messages dans Kafka

Configuration principale :

Broker : kafka:9092
Topic  : streaming_data


Surveillance :

docker logs kafka-producer -f

### 4.3 Consommateur Spark

Fonctionnalités :

Lecture des données depuis Kafka

Application d’un schéma structuré

Entraînement incrémental du modèle (SGDRegressor)

Calcul du RMSE par batch

Sauvegarde du modèle et des métriques

Surveillance :

docker logs spark-consumer -f

### 4.4 Visualisation du RMSE

Accès à Streamlit :

http://localhost:8501


Fonctionnalités :

Graphe d’évolution du RMSE par batch

KPI : dernier RMSE

Rafraîchissement automatique toutes les 5 secondes

### 4.5 Prédictions en Temps Réel

Fonctionnalités de la page Prédiction :

Saisie des caractéristiques du véhicule

Prédiction instantanée des émissions de CO₂

Rechargement dynamique du modèle entraîné

## 5. Technologies Utilisées
API               : FastAPI
Streaming         : Apache Kafka
Coordination      : Zookeeper
Traitement        : Apache Spark
Machine Learning  : Scikit-learn
Visualisation     : Streamlit
Conteneurisation  : Docker
Orchestration     : Docker Compose

## 6. Structure du Projet
ml-pipeline-spark-kafka/
│
├── api/
│   └── main.py
│
├── producer/
│   └── producer.py
│
├── spark/
│   └── consumer.py
│
├── streamlit/
│   ├── app.py
│   └── pages/
│       └── prediction.py
│
├── data/
│   └── co2_processed.csv
│
├── models/
│   ├── sgd.joblib
│   └── metrics.json
│
├── docker-compose.yml
└── README.md

## 7. Résultats et KPI
- Entraînement incrémental du modèle en streaming
- RMSE calculé et mis à jour à chaque batch
- Visualisation temps réel des performances
- Prédictions interactives via interface web
# Pipeline d’Ingestion IoT Temps Réel et Espace Documentaire Sécurisé

## 1. Présentation du Projet

Ce projet met en œuvre une architecture **serverless** sur **Amazon Web Services (AWS)** destinée à l’ingestion, au traitement et au stockage de données issues de capteurs IoT.

La solution intègre également un espace documentaire privé permettant la centralisation et la gestion sécurisée des documents techniques associés au projet.

L’ensemble de l’infrastructure est déployé à l’aide de **AWS Serverless Application Model (AWS SAM)** et repose exclusivement sur des services managés AWS afin de garantir :

* la scalabilité ;
* la haute disponibilité ;
* la réduction des coûts d’exploitation ;
* la simplicité de maintenance.

---

# 2. Architecture de la Solution

## 2.1 Sous-système A : Pipeline d’Ingestion IoT

Le pipeline de traitement des données IoT s’appuie sur les services suivants :

* **Amazon API Gateway** : réception des données provenant des capteurs ;
* **AWS Lambda** : traitement des données reçues ;
* **Amazon S3** : stockage des données brutes (Data Lake) ;
* **Amazon DynamoDB** : stockage des informations analytiques et des indicateurs calculés.

### Flux de traitement

1. Un capteur IoT envoie un payload JSON à l’API.
2. API Gateway déclenche automatiquement une fonction Lambda.
3. Le payload complet est archivé dans Amazon S3.
4. Les données sont analysées.
5. Les indicateurs calculés sont enregistrés dans DynamoDB.

---

## 2.2 Sous-système B : Espace Documentaire Sécurisé

Un bucket Amazon S3 privé est utilisé pour stocker :

* la documentation technique ;
* les rapports d’architecture ;
* les documents destinés aux équipes de développement et d’exploitation.

Les accès publics sont entièrement désactivés afin de garantir la confidentialité des données.

---

# 3. Structure du Projet

```text
Pipeline-AWS-et-Data-IOT/
├── src/
│   └── index.py
├── tests/
│   └── test_client.py
├── documentation/
│   └── index.html
├── template.yaml
└── README.md
```

### Description des éléments

| Élément                    | Description                             |
| -------------------------- | --------------------------------------- |
| `src/index.py`             | Code source de la fonction Lambda       |
| `tests/test_client.py`     | Script de simulation et de validation   |
| `documentation/index.html` | Documentation technique statique        |
| `template.yaml`            | Infrastructure AWS SAM / CloudFormation |
| `README.md`                | Documentation du projet                 |

---

# 4. Prérequis

Les outils suivants doivent être installés :

* AWS CLI v2
* AWS SAM CLI
* Python 3.11

Configuration des identifiants AWS :

```bash
aws configure
```

Renseigner ensuite les identifiants temporaires fournis par AWS Academy ou Learner Lab.

---

# 5. Déploiement de l’Infrastructure

## Important

Les environnements AWS Academy limitent la création de nouveaux rôles IAM.

Pour contourner cette restriction, le template utilise un paramètre nommé :

```text
StudentRoleARN
```

Ce paramètre permet de réutiliser un rôle IAM déjà disponible dans l’environnement académique.

---

## Étape 1 : Construction du projet

```bash
sam build
```

---

## Étape 2 : Déploiement guidé

```bash
sam deploy --guided
```

Paramètres recommandés :

| Paramètre                            | Valeur                                 |
| ------------------------------------ | -------------------------------------- |
| Stack Name                           | `pipeline-iot-stack-ongatobaye`        |
| AWS Region                           | `eu-west-3`                            |
| StudentRoleARN                       | ARN du rôle IAM fourni par AWS Academy |
| Confirm changes before deploy        | `Y`                                    |
| Allow SAM CLI IAM role creation      | `Y`                                    |
| Save arguments to configuration file | `Y`                                    |

Une fois la configuration sauvegardée :

```bash
sam deploy
```

suffira pour les futurs déploiements.

---

# 6. Ressources Créées

Le déploiement provisionne automatiquement :

* une API Gateway REST ;
* une fonction AWS Lambda Python 3.11 ;
* un bucket S3 pour le Data Lake ;
* un bucket S3 privé pour la documentation ;
* une table DynamoDB en mode On-Demand.

Après le déploiement, l’URL d’ingestion est disponible dans les **Outputs** CloudFormation sous :

```text
ApiGatewayIngestionURL
```

---

# 7. Validation Fonctionnelle

Le fichier :

```bash
tests/test_client.py
```

permet de simuler plusieurs scénarios de fonctionnement.

Avant l’exécution, mettre à jour la variable :

```python
API_URL
```

avec l’URL obtenue dans les Outputs CloudFormation.

Exécution :

```bash
python3 tests/test_client.py
```

---

## Cas de Test 1 : Payload Valide

Objectif :

* Vérifier l’ingestion correcte des données.

Résultat attendu :

* HTTP 201
* Archivage du JSON dans S3
* Mise à jour de DynamoDB

---

## Cas de Test 2 : Température Critique

Objectif :

* Détecter une anomalie de température.

Résultat attendu :

* HTTP 201
* Données stockées
* Compteur d’anomalies mis à jour

---

## Cas de Test 3 : Payload Incomplet

Objectif :

* Vérifier la gestion des erreurs.

Résultat attendu :

* HTTP 400
* Payload archivé pour audit
* Aucune interruption du service

---

## Cas de Test 4 : Consultation des Données

Objectif :

* Vérifier la récupération des données analytiques.

Résultat attendu :

* HTTP 200
* Retour du contenu DynamoDB

---

# 8. Publication de la Documentation

Téléverser la documentation :

```bash
aws s3 cp documentation/index.html s3://tech-doc-629193321657-eu-west-3-v2/index.html
```

L’accès direct au bucket doit retourner :

```text
HTTP 403 AccessDenied
```

ce qui confirme le caractère privé de l’espace documentaire.

---

# 9. Nettoyage des Ressources

Afin d’éviter toute consommation inutile de ressources AWS, les composants créés doivent être supprimés après l’évaluation.

## Étape 1 : Vider les Buckets S3

```bash
aws s3 rm s3://io-raw-data-lake-629193321657-eu-west-3-v2 --recursive

aws s3 rm s3://tech-doc-629193321657-eu-west-3-v2 --recursive
```

---

## Étape 2 : Supprimer la Stack

```bash
sam delete --stack-name pipeline-iot-stack-ongatobaye
```

Lorsque AWS SAM demande confirmation :

```text
Are you sure you want to delete the stack?
```

répondre :

```text
y
```

afin de supprimer :

* la stack CloudFormation ;
* les ressources associées ;
* le bucket temporaire d’artefacts utilisé par AWS SAM.

---

# 10. Technologies Utilisées

| Domaine                | Technologie              |
| ---------------------- | ------------------------ |
| Infrastructure as Code | AWS SAM / CloudFormation |
| Compute                | AWS Lambda               |
| API                    | Amazon API Gateway       |
| Stockage brut          | Amazon S3                |
| Base NoSQL             | Amazon DynamoDB          |
| Monitoring             | Amazon CloudWatch        |
| Langage                | Python 3.11              |

---

# 11. Auteur

**Ngartobaye Oumarou Billy**

Master 1 – Architecture Cloud & Data Engineering

Projet réalisé dans le cadre du module :

**Introduction à AWS Cloud Computing**

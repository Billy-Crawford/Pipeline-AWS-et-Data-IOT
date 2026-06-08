# Pipeline d’Ingestion IoT Temps Réel et Espace Documentaire Sécurisé

## Présentation

Ce projet met en œuvre une architecture serverless sur Amazon Web Services (AWS) destinée à l’ingestion, au traitement et au stockage de données issues de capteurs IoT. L’infrastructure intègre également un espace documentaire privé permettant la centralisation de documents techniques liés au projet.

L’ensemble de la solution est déployé à l’aide d’AWS Serverless Application Model (AWS SAM) et s’appuie sur les services managés d’AWS afin de garantir la scalabilité, la disponibilité et la réduction des coûts d’exploitation.

---

## Architecture

### Sous-système A : Pipeline IoT

Le pipeline de traitement des données IoT repose sur les composants suivants :

* **Amazon API Gateway** : point d’entrée HTTP permettant la réception des données.
* **AWS Lambda** : traitement des données reçues.
* **Amazon S3** : stockage des données brutes dans un Data Lake.
* **Amazon DynamoDB** : stockage des informations analytiques et des indicateurs calculés.

#### Flux de traitement

1. Un capteur envoie un payload JSON à l’API Gateway.
2. La requête déclenche une fonction Lambda.
3. Le payload complet est archivé dans Amazon S3.
4. Les données sont analysées.
5. Les indicateurs calculés sont enregistrés dans DynamoDB.

---

### Sous-système B : Espace documentaire sécurisé

Un bucket Amazon S3 privé est utilisé pour stocker :

* la documentation technique ;
* les rapports d’architecture ;
* les documents destinés aux équipes de développement et d’exploitation.

L’accès public est entièrement désactivé.

---

## Structure du projet

```text
Pipeline-AWS-et-Data-IOT/
├── src/
│   └── index.py
├── tests/
│   └── test_client.py
├── documentation/
│   └── index.html
├── template.yaml
├── samconfig.toml
└── README.md
```

## Prérequis

Les outils suivants doivent être installés :

* AWS CLI v2
* AWS SAM CLI
* Python 3.11

Vérifier également que les identifiants AWS sont correctement configurés :

```bash
aws configure
```

---

## Déploiement

### 1. Construction du projet

```bash
sam build
```

### 2. Déploiement de l’infrastructure

```bash
sam deploy
```

Lors du premier déploiement, il est également possible d’utiliser :

```bash
sam deploy --guided
```

---

## Ressources créées

Le déploiement provisionne automatiquement :

* une API Gateway REST ;
* une fonction AWS Lambda ;
* un bucket S3 pour le Data Lake ;
* un bucket S3 privé pour la documentation ;
* une table Amazon DynamoDB.

Une fois le déploiement terminé, AWS CloudFormation fournit les informations suivantes :

* URL de l’API d’ingestion ;
* nom du bucket documentaire.

---

## Validation fonctionnelle

Le script de test fourni permet de simuler différents scénarios de fonctionnement.

Exécution :

```bash
python3 tests/test_client.py
```

### Cas de test couverts

#### Cas nominal

Payload valide envoyé à l’API.

Résultat attendu :

```text
HTTP 201
```

#### Cas anomalie

Détection d’une température critique.

Résultat attendu :

```text
HTTP 201
```

avec incrémentation du compteur d’anomalies.

#### Cas données incomplètes

Payload ne respectant pas le format attendu.

Résultat attendu :

```text
HTTP 400
```

Le message est conservé pour audit et la tentative est enregistrée.

#### Consultation des données analytiques

Lecture des informations présentes dans DynamoDB.

Résultat attendu :

```text
HTTP 200
```

---

## Publication de la documentation

Exemple d’envoi du rapport technique vers le bucket documentaire :

```bash
aws s3 cp documentation/index.html \
s3://tech-doc-629193321657-eu-west-3-v2/index.html
```

---

## Nettoyage des ressources

Pour supprimer l’ensemble de l’infrastructure :

```bash
sam delete \
--stack-name pipeline-iot-stack-ongatobaye \
--no-prompts
```

Si les buckets S3 contiennent encore des objets, les vider avant suppression :

```bash
aws s3 rm s3://NOM_DU_BUCKET --recursive
```

---

## Technologies utilisées

* AWS SAM
* AWS Lambda
* Amazon API Gateway
* Amazon S3
* Amazon DynamoDB
* AWS CloudFormation
* Python 3.11

---

## Auteur

Projet réalisé dans le cadre du module AWS Cloud Computing – Master 1.

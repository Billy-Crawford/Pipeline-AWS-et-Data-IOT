import json
import os
import boto3 # type: ignore
from datetime import datetime
from decimal import Decimal

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Encodeur personnalisé pour convertir le type Decimal de DynamoDB en JSON lisible
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) if obj % 1 != 0 else int(obj)
        return super(DecimalEncoder, self).default(obj)

def handler(event, context):
    dynamodb_table_name = os.environ.get('DYNAMODB_TABLE')
    table = dynamodb.Table(dynamodb_table_name)
    
    # 1. ROUTE DE LECTURE (GET) : Pour contourner le blocage de ton AWS CLI local
    http_method = event.get('httpMethod', 'POST')
    if http_method == 'GET':
        try:
            response = table.scan()
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps(response.get('Items', []), cls=DecimalEncoder, ensure_ascii=False)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Impossible de lire la table', 'details': str(e)})
            }

    # 2. ROUTE D'INGESTION (POST) - Ton code existant robuste
    request_id = context.aws_request_id
    s3_bucket_name = os.environ.get('S3_BUCKET')
    
    payload = None
    status_traitement = "SUCCES"
    details_erreur = ""
    avg_temperature = 0.0
    error_count = 0

    try:
        body_str = event.get('body', '{}')
        payload = json.loads(body_str)
        
        if not payload or not isinstance(payload, list):
            raise ValueError("Le payload doit etre une liste non vide de mesures IoT.")
            
        total_temp = 0.0
        count_temp = 0
        
        for measure in payload:
            sensor_data = measure.get('sensor_data', {})
            if 'temperature' not in sensor_data:
                raise KeyError(f"Donnee critique 'temperature' manquante pour le device {measure.get('device_id', 'Inconnu')}")
                
            temp = sensor_data.get('temperature')
            if temp is not None:
                total_temp += float(temp)
                count_temp += 1
                
            if sensor_data.get('status') == 'CRITICAL':
                error_count += 1
                
        avg_temperature = total_temp / count_temp if count_temp > 0 else 0.0

    except Exception as e:
        status_traitement = "CORROMPU"
        details_erreur = str(e)
        print(f"ERREUR VALIDATION PAYLOAD : {details_erreur}")

    try:
        if payload is None:
            payload = {"raw_event": body_str}

        now = datetime.utcnow()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        timestamp_str = now.strftime('%Y%m%d_%H%M%S')
        
        s3_key = f"raw-zone/year={year}/month={month}/day={day}/{request_id}_{timestamp_str}.json"
        
        s3.put_object(
            Bucket=s3_bucket_name,
            Key=s3_key,
            Body=json.dumps(payload),
            ContentType='application/json'
        )
        
        table.put_item(
            Item={
                'requestId': request_id,
                'timestamp': now.isoformat(),
                's3_raw_path': f"s3://{s3_bucket_name}/{s3_key}",
                'status_traitement': status_traitement,
                'average_temperature': Decimal(str(round(avg_temperature, 2))),
                'anomaly_count': int(error_count),
                'details_erreur': details_erreur
            }
        )
        
        if status_traitement == "CORROMPU":
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'error': 'Payload corrompu, mais archive dans le Data Lake.',
                    'requestId': request_id,
                    'details': details_erreur
                })
            }
            
        return {
            'statusCode': 201,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'Ingestion effectuee avec succes.',
                'requestId': request_id,
                's3_path': s3_key,
                'metrics': {
                    'avg_temp': round(avg_temperature, 2),
                    'errors_found': error_count
                }
            })
        }

    except Exception as critical_aws_error:
        print(f"ERREUR INFRASTRUCTURE AWS : {str(critical_aws_error)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Erreur interne de stockage.', 'details': str(critical_aws_error)})
        }
    
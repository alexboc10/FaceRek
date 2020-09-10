import boto3
from boto3.dynamodb.conditions import Key
import datetime
import json
import random

# La funzione è avviata ad ogni inserimento di immagini in S3

def detect_faces(bucket, key):

  # Creazione client Rekognition
  rekognition = boto3.client("rekognition")

  # Esecuzione effettiva di Rekognition sull'oggetto specificato
  response = rekognition.detect_faces(
             Image= {
               "S3Object": {
                 "Bucket": bucket,
                 "Name": key
               }
             },
             Attributes=['ALL'])

  # Viene considerato come output solo la sezione 'FaceDetails'
  return response['FaceDetails']

def insert_item(faceDetails, key, table):
  
  # La chiave primaria è 'faceId' ed è scelta in modo casuale. Non è importante
  # in quanto l'elemento caratterizzante è il filename.
  # Per ogni caratteristica valutata viene memorizzato anche il livello di
  # confidenza del rilevamento
  item = {'faceId':random.randint(0,100), 
  'filename':key.split(".")[0],
    'timestamp':int(round(datetime.datetime.now().timestamp()*1000)),
    'ageLow':str(faceDetails[0]["AgeRange"]["Low"]),
    'ageHigh':str(faceDetails[0]["AgeRange"]["High"]),
    'emotionType1':str(faceDetails[0]["Emotions"][0]["Type"]),
    'emotionConf1':str(faceDetails[0]["Emotions"][0]["Confidence"]),
    'emotionType2':str(faceDetails[0]["Emotions"][1]["Type"]),
    'emotionConf2':str(faceDetails[0]["Emotions"][1]["Confidence"]),      
    'genderValue':str(faceDetails[0]["Gender"]["Value"]),
    'genderConf':str(faceDetails[0]["Gender"]["Confidence"])
  }
  
  response = table.put_item(Item=item)
  
def delete_item(items, table):
  table.delete_item(
    Key={
      'faceId': items[0]['faceId'],
      'timestamp': items[0]['timestamp']
      
    })
    
  print("-------DONE-------")
      
def lambda_handler(event, context):

  # Nome del bucket
  bucket = event['Records'][0]['s3']['bucket']['name']
  # Nome dell'oggetto
  key = event['Records'][0]['s3']['object']['key']

  # Client di DynamoDB
  dynamodb = boto3.resource("dynamodb")
      
  table = dynamodb.Table("sdcc-dataimages")   

  # Scansione della tabella di immagini cercando l'oggetto con 
  # il filena,e specificato
  response = table.scan(
        FilterExpression=Key('filename').eq(key.split(".")[0])
        )
        
  # Non è possibile avere più oggetti con medesimo filename
  # Se ne esiste già uno, esso verrà sovrascritto
  if len(response['Items']) > 0:
    print("Filename already exists. It will be overwritten.")
    delete_item(response['Items'], table)

  # Esecuzione di Rekognition per l'analisi dell'immagine
  print("Detecting all the face attributes")
  faceDetails = detect_faces(bucket, key)

  # Inserimento dell'output in DynamoDB
  print("Adding the attributes in DynamoDB")
  insert_item(faceDetails, key, table)
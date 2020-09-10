import json
import boto3
from boto3.dynamodb.conditions import Key

# scan completo della tabella DynamoDB
def getPeople():
    dynamodb = boto3.resource("dynamodb")
                             
    table = dynamodb.Table("sdcc-dataimages")
    
    response = table.scan()
    
    return response

# ricerca dell'oggetto con il filename specificato
def getPerson(first_name):
    
    dynamodb = boto3.resource("dynamodb")
                             
    table = dynamodb.Table("sdcc-dataimages")
    
    response = table.scan(
        FilterExpression=Key('filename').eq(first_name.lower())
    )
    
    if len(response['Items']) < 1:
        return "null"
    else:
        return response['Items'][0]

# Viene restituito un messaggio di errore nel caso in cui il soggetto richiesto
# non sia presente in DynamoDB
def error_response():
    response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":"I don't know this guy. Please try with an existing person."
                },
            }
        }
        
    return response
    
def lambda_handler(event, context):
    # 'intent' rilevato da Amazon Lex
    intent = event["currentIntent"]["name"]
    
    # Richiesta dell'immagine del soggetto indicato dall'utente. 
    ####ATTENZIONE####
    # Nel contesto della console AWS l'immagine viene correttamente visualizzata.
    # Al contrario, nell'interfaccia grafica ciò non avviene: il chatbot
    # restituisce il link all'immagine memorizzata in S3
    ##################
    if intent == "imageIntent":
        first_name = event["currentIntent"]["slots"]["first_name"];
        
        if getPerson(first_name) == "null":
            return error_response()
        
        response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":"This the picture link: " + "https://sdcc-images.s3.eu-central-1.amazonaws.com/{}.jpg".format(event["currentIntent"]["slots"]["first_name"])
                },
                "responseCard": {
                "version": "1",
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                      {
                         "imageUrl":"https://sdcc-images.s3.eu-central-1.amazonaws.com/{}.jpg".format(event["currentIntent"]["slots"]["first_name"])
                      }
                ] 
                }
                
            }
        }
    # Viene restituita la lista di tutti i soggetti memorizzati in DynamoDB
    # Molto utile per l'utente per sapere i soggetti presenti nel sistema
    elif intent == "ListPeople":
        people = getPeople()
        names = ""
        i = 1
        
        for person in people["Items"]:
            if i == 1:
                names = names + person["filename"].capitalize()
            else:
                names = names + ", " + person["filename"].capitalize()
                
            i = i + 1
            
        response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":"I can talk about these people: {}. What would you like to know?".format(names)
                },
            }
        }
        
    return response
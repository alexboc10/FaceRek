import json
import boto3
from boto3.dynamodb.conditions import Key

# La funzione è avviata quando l'utente interagisce con il chatbot
# tramite l'interfaccia web

# Scan completo della tabella di DynamoDB
def getPeople():
    dynamodb = boto3.resource("dynamodb")
                             
    table = dynamodb.Table("sdcc-dataimages")
    
    response = table.scan()
    
    return response
    
# Scan della tabella DynamoDB in cerca dell'oggetto con 'filename' specificato
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
    
# Risposta in ambito di età del soggetto
def ageIntentResponse(result, first_name):
    response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":("{} is between {} and {} years old").format(first_name.capitalize(), result["ageLow"], result["ageHigh"])
                }
            }
        }
        
    return response
# Risposta in ambito di sesso del soggetto
def genderIntentResponse(result, first_name):
    response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":("{} is {} with a confidence of {}%").format(first_name.capitalize(), result["genderValue"], round(float(result["genderConf"]), 2))
                }
            }
        }
        
    return response
    
# Risposta in ambito di emozione del soggetto
def emotionIntentResponse(result, first_name):
    
    if result["genderValue"] == "Male":
        pron = "he"
    else:
        pron = "she"
    
    response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":("I think {} is {} with a confidence of {}%. But it's also possible {} is {} with a confidence of {}%").format(first_name.capitalize(), result["emotionType1"], round(float(result["emotionConf1"]), 2), pron, result["emotionType2"], round(float(result["emotionConf2"]), 2))
                }
            }
        }
        
    return response

# Risposta in ambito di statistiche sul sesso dei soggetti
def genderStats(result):
    male = 0
    female = 0
    
    for person in result['Items']:
        if person["genderValue"] == 'Male':
            male = male + 1
        elif person["genderValue"] == 'Female':
            female = female + 1
            
    return "I know about {} men and {} women!".format(male, female)

# Risposta in ambito di statistiche sull'età dei soggetti
def ageStats(result):
    avgAge = 0.0
    totalValue = 0.0
    count = 0
    
    for person in result['Items']:
        count = count + 1
        totalValue = totalValue + (int(person["ageHigh"]) + int(person["ageLow"]))/2
        
    avgAge = totalValue/count
    
    return "The average age of people I know is {}".format(avgAge)

# Risposta in ambito di statistiche sull'emozione dei soggetti
def emotionStats(result):
    sad = 0
    happy = 0
    surprised = 0
    calm = 0
    angry = 0
    
    for person in result['Items']:
        if person["emotionType1"] == 'SAD':
            sad = sad + 1
        elif person["emotionType1"] == 'HAPPY':
            happy = happy + 1
        elif person["emotionType1"] == 'SURPRISED':
            surprised = surprised + 1
        elif person["emotionType1"] == 'CALM':
            calm = calm + 1
        elif person["emotionType1"] == 'ANGRY':
            angry = angry + 1
            
    return "I know {} sad people, {} happy people, {} surprised people, {} calm people and {} angry people.".format(sad, happy, surprised, calm, angry)

def avgIntentResponse(result, attribute):
    
    if attribute == "gender":
        message = genderStats(result)
    elif attribute == "age":
        message = ageStats(result)
    elif attribute == "emotion":
        message = emotionStats(result)
    else:
        message = "Could you be more specific, please?"
        
    response = {
            "dialogAction": {
                "type":"Close",
                "fulfillmentState":"Fulfilled",
                "message": {
                    "contentType":"SSML",
                    "content":(message)
                }
            }
        }
        
    return response

def lambda_handler(event, context):
    # 'intent' individuato da Amazon Lex, cioè l'ambito di conversazione
    # rilevato da Lex partendo dalla domanda dell'utente
    intent = event["currentIntent"]["name"]

    # Molteplici possibilità di 'intent' e molteplici possibili reazioni
    if intent == "AgeIntent":
        first_name = event["currentIntent"]["slots"]["first_name"];
        result = getPerson(first_name)
        if result == "null":
            return error_response()
            
        response = ageIntentResponse(result, first_name);
    elif intent == "GenderIntent":
        first_name = event["currentIntent"]["slots"]["first_name"];
            
        result = getPerson(first_name);
        if result == "null":
            return error_response()
            
        response = genderIntentResponse(result, first_name);
    elif intent == "EmotionIntent":
        first_name = event["currentIntent"]["slots"]["first_name"];
            
        result = getPerson(first_name);
        if result == "null":
            return error_response()
            
        response = emotionIntentResponse(result, first_name);
    elif intent == "AvgIntent":
        attribute = event["currentIntent"]["slots"]["attribute"];
            
        result = getPeople();
        if result == "null":
            return error_response()
            
        response = avgIntentResponse(result, attribute);
    
    return response
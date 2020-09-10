FaceRek by Alessandro Boccini
Sviluppo completato nel mese di Settembre 2020 in ambiente
Ubuntu 20.04

L'applicazione prevede una logica situata quasi interamente su cloud
ma richiede un'iniziale esecuzione in ambiente Unix.
Il file "run.sh" permette il caricamento delle immagini in formato
jpg (già contenute nella cartella "images" o nuove) nel sistema di
storage di AWS (S3) e l'avvio dell'interfaccia grafica per l'interazione 
con l'applicazione.
Lo script di avvio considera "firefox" come browser di riferimento.
In caso di altra preferenza è necessario modificare il comando alla
penultima riga dello script (as esempio "chrome").
Il file index.html può essere avviato, alternativamente, anche in
modo indipendente dall'esecuzione dello script.

#####IMPORTANTE######
L'esecuzione dello script richiede l'installazione di AWS CLI
di Amazon al fine di interagire con i servizi AWS da riga di comando.
#####################

Si consiglia di fornire privilegi massimi di scrittura, lettura ed
esecuzione ad i file dell'applicazione per evitare possibili problemi.

La cartella "lambda-handlers" contiene le 3 funzioni eseguite in
AWS Lambda per gestire l'interazione tra utente e applicazione.
Esse saranno eseguite completamente in ambiente remoto tramite
la tecnologia del "serverless computing".
La funzione categorize si occupa di trasferire le immagini al
servizio "Rekognition" per poi memorizzar l'output in
DynamoDB.
Le funzioni vision e imageResponse si occupano della gestione
della logica dell'assistente testuale implementato con Amazon
Lex.

I file da caricare con lo script devono avere estensione "jpg".

Nella cartella "images" ci sono 10 immagini. Per cambiare l'input è
possibile aggiungere altri file "jpg" alla cartella o caricare,
immagine per immagine, tramite lo script.

L'applicazione richiede di mantenere i path relativi originali
per il corretto funzionamento.

Das Interface erlaubt den Zugriff auf buzzit-Funktionen mit Hilfe von HTTP POST und GET.
Dabei exstieren folgende Möglichkeiten:

1. `HTTP GET http://<Service-URL>/messaging/circlemessage/getall/json`

2. `HTTP POST http://<Service-URL>/messaging/circlemessage/new/json`


--

Im folgenden werden die beiden Möglichkeiten erklärt:

* `HTTP GET http://<URL>/messaging/circlemessage/getall/json` erlaubt den Zugriff auf alle Posts des eingeloggten Users. Dabei sind als GET Parameter der Benutzername und das Passwort des einzuloggenden Users zu übergeben.
Ein Beispiel Aufruf sieht wie folgt aus:
`HTTP GET http://example.com/messaging/circlemessage/getall/json?username=TestUser&password=test123`
Hierbei erhält der Client JSON Daten zurück.
Diese sind wie folgt definiert:
Wenn ein Fehler auftritt:

`{
    "error" : "<ERROR MESSAGE>", 
    "result" : false // optional
}`

Sonst:

`{
    "data" : [
        {"answer_to" : <null, wenn der Post keine Antwort ist, sonst die ID des original Posts>,
         "created" : <DateTime - Zeitpunkt, zu dem der Post erstellt wurde, Format: YYYY-MM-DD\THH:mm:ss\Z>,
         "creator" : <ID des Erstellers>,    
         "id" : <ID des Posts>,    
         "mentions" : [<ID des erwähnten Benutzers>, ...],       
         "message_ptr": <=== ID des Posts>,
         "original_message": <null, wenn dies kein Repost ist, sonst ID des original Posts>,       
         "public" : <true, wenn die Nachricht öffentlich ist, false sonst>,       
         "text" : <string, Text des Posts>,          
         "themes" : [<string, Text eines erwähnten Themas>, ...],    
        },
        ...
    ],
    "result" : true
}`


--

* `HTTP POST http://<Service-URL>/messaging/circlemessage/new/json`
Hierbei kann ein neuer Post erstellt werden.
POST DATA muss die folgenden Informationen enthalten (Es handelt sich dabei um Formulardaten):
<ul>
<li>username  --- der Benutzername des einzuloggenden Benutzers.</li>
<li>- password  --- das Passwort des Benutzers.</li>
<li>- text      --- Der Zu Postende Text. Maximal 140 Zeichen.</li>
</ul>

Der Client erhält JSON Daten zurück:
Wenn Fehler auftreten:
`{
    "result": false,
    "data": {
        "error": "<ERROR MESSAGE>"
    }
}`
Wenn alles gut lief:
`{
    "result": true,
    "data": {}
}`
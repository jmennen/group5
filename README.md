[![Stories in Ready](https://badge.waffle.io/jmennen/group5.png?label=ready&title=Ready)](https://waffle.io/jmennen/group5)
# group5
Das Repository von Gruppe 5 des Praktikums Soziale Netzwerke an der TU Berlin



######**Projektziel:**
>*Das Ziel des Projektes ist das Erstellen eines neuen sozialen Netzwerkes, das auf die Web Application Framework Django aufbaut und über den Browser erreichbar ist. Das Soziale Netzwerk soll die Möglichkeit zur Kontrolle der Sichtbarkeit der eigenen Veröffentlichungen biete und mit anderen Sozialen Netzwerken interagieren können.*

--

######**Demoinstallation und Interface**
Eine Demoinstallation is unter folgendem Link erreichbar:
http://ec2-52-18-19-172.eu-west-1.compute.amazonaws.com/

Die Dokumentation des Interface der Demoinstallation ist unter folgendem Link zu finde:
https://github.com/jmennen/group5/wiki/Interface

######**Projektteam** 
Name | Aufgabenbereich | E-Mail
:----- | :---------------------------------- | :--------------------------------
Cheng Chen | Frontend Entwicklung | chengchen@hotmail.de
David Skowronek | Technische Leitung | dskowronek.ds@gmail.com
Dong Yang | Backend Entwicklung | fabian082yang@hotmail.com
Florian Stelzer | Backend Entwicklung | florian.stelzer@web.de
Jan Mennen | Dokumentation, Gruppenleiter | jan.mennen@campus.tu-berlin.de
Qi Yang | Frontend Entwicklung | flouza@hotmail.de


--

######**Dokumentation** 
* Die readme-Datei dieses Repositories als zentraler Übersichtspunkt
* Die Github Issues dieses Repositories
 - Dort finden Sie alle unsere Stories (Label "story"). Das Label "ready" markiert stories welche im aktuellen Sprintplan sind.
 - In den Beschreibungen (oder Kommentaren) der Issues sind detailiertere Informationen zu den Stories zu finden.
 - Change Requests sind mit dem Label CHANGE versehen. Die Beschreibung der Änderung findet in den Kommentaren statt.
 - Auch einsehbar unter: https://waffle.io/jmennen/group5
* Das Github Wiki dieses Repositories. Dort finden Sie die Dokumentation aller Funktionen des sozialen Netzwerks Buzzit.
* Das Google Docs Sheet:
 - Dort zu finden sind die Tasks für sämtliche Sprints mit einem Status und eventuell dem Fertigstellungsdatum.
 - Das Glossar
 - Zu finden unter: https://docs.google.com/spreadsheets/d/1N_UW9WGyGDWDz0Np6o5HEIzIVfv1p_poOpYCRMQkPLY/edit?usp=sharing
* Der Ordner Dokumentation in diesem Github Repository:
 - Hier sind alle Arten von Diagrammen zu finden (Klassendiagramm, Usecase, Kontextdiagramm) 

--

######**Lizenz**
Dieses Projekt steht unter der BSD-Lizenz. Siehe Licence.md

--

######**Tools used**
* Django
* Bootstrap
* Noty
* Sumoselect

--

######**Dependencies**
* python 3.4
* django 1.8
* python Pillow 
* python mySQLClient
* python bleach

--

######**How to use this?**
<ul>
<li>Install Python (3.3+) incl. PIP or find the packages another way</li>
<li>Install Django (pip install django) -- The Django Framework</li>
<li>Install Pillow (pip install pillow) with jpeg support -- Image Manipulation Library</li>
<li>Install MySQLClient (pip install mysqlclient) -- MySQL DB-Connector</li>
<li>Install Bleach (pip install bleach)</li>
<li>Download this project</li>
<li>Create a folder pp in the parent folder of the django project called "buzzit".
<li>Create a file mysql.py in the folder "buzzit/buzzit" (where the settings file is). This file should contain the information about your MySQL Database
<li>Register a user called "SYSTEM". 
<li>Have Fun</li>
</ul>

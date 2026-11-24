# Übergabe: Risiko-Partie (Blau gegen Schwarz)

Stand erfasst am 2026-11-24 aus 6 Fotos. Die Daten stehen maschinenlesbar in `state.json` (Gebiete, Besitzer, Armeen, Kontinentboni, Nachbarschaften).

## Ziel
Aus dem aktuellen Spielstand soll eine Excel-Datei entstehen. Sie soll Statistik, Verstärkungsberechnung und Manöverempfehlungen für beide Seiten enthalten, außerdem ein Schemabild des Bretts. Die Datei ist noch **nicht** erstellt.

## Spielsituation
- 2 Spieler: **Blau** und **Schwarz**. Die gelben Figuren sind unbenutzter Vorrat.
- Figurenwerte: Infanterie 1, Reiter 5, Kanone 10. Auf dem Brett steht keine Kanone.
- Es sind 42 Gebiete besetzt, kein Gebiet ist neutral. Blau hat 20 Gebiete, Schwarz 22.
- Unbekannt: wer am Zug ist, die Handkarten (auf einem Foto liegen 3 Gebietskarten am Rand) und ob schon Kartensätze eingelöst wurden.

## Armeen (vom Nutzer bestätigt, alle Werte geprüft)

**Blau: 20 Gebiete, 52 Armeen**
- Nordamerika (komplett, Bonus 5): Alaska 5, Nordwest-Territorium 3, Grönland 1, Alberta 1, Ontario 1, Ostkanada 1, Weststaaten 2, Oststaaten 1, Mittelamerika 3
- Südamerika (komplett, Bonus 2): Venezuela 1, Peru 1, Brasilien 10, Argentinien 1
- Europa (komplett, Bonus 5): Island 1, Großbritannien 2, Skandinavien 2, Nordeuropa 2, Westeuropa 7, Südeuropa 2, Russland 5

**Schwarz: 22 Gebiete, 69 Armeen**
- Afrika (komplett, Bonus 3): Nordafrika 3, Ägypten 1, Ostafrika 6, Zentralafrika 2, Südafrika 2, Madagaskar 5
- Asien (komplett, Bonus 7): Naher Osten 5, Afghanistan 10, Ural 3, Sibirien 5, Jakutien 1, Kamtschatka 2, Irkutsk 1, Mongolei 3, China 2, Indien 5, Siam 3, Japan 3
- Australien (komplett, Bonus 2): Indonesien 4, Neuguinea 1, Westaustralien 1, Ostaustralien 1

Reiter-Gebiete: Alaska, Russland, Madagaskar, Naher Osten, Sibirien je 1 Reiter. Brasilien, Afghanistan je 2 Reiter. Westeuropa und Ostafrika je 1 Reiter plus Infanterie.

## Verstärkung in der nächsten Runde
Formel: `max(3, floor(Gebiete / 3)) + Kontinentboni (+ Kartensätze, unbekannt)`
- Blau: floor(20/3) = 6, plus 5 + 2 + 5 = **18**
- Schwarz: floor(22/3) = 7, plus 3 + 7 + 2 = **19**

## Kontaktzonen (Gebiete, in denen Blau und Schwarz aneinandergrenzen)
- Brasilien (Blau, 10) gegen Nordafrika (Schwarz, 3)
- Westeuropa (Blau, 7) gegen Nordafrika (3)
- Südeuropa (Blau, 2) gegen Nordafrika (3), Ägypten (1), Naher Osten (5)
- Russland (Blau, 5) gegen Ural (3), Afghanistan (10), Naher Osten (5)
- Alaska (Blau, 5) gegen Kamtschatka (Schwarz, 2)

Die Karte ist ein Standard-Risiko-Brett. Die Nachbarschaften in `state.json` sind aus dem Standardbrett abgeleitet und sollten einmal gegen das reale Brett geprüft werden (Verbindungen über die Meere, vor allem Alaska–Kamtschatka, Grönland–Island, Brasilien–Nordafrika, Südeuropa–Ägypten und Naher Osten–Ostafrika).

## Geplanter Excel-Aufbau
Alles mit lebenden Formeln, Eingaben in blau, Arial, Zahlen im deutschen Stil.
1. **Gebiete**: Spalten Gebiet, Kontinent, Besitzer, Armeen, Bemerkung. Hier werden die Daten gepflegt, alles andere rechnet daraus.
2. **Statistik**: Gebiete und Armeen je Spieler und Kontinent, Kontinentbesitz, Verstärkung pro Spieler (mit Eingabezelle für Kartenbonus), Armeenanteil, Grenzstärke.
3. **Manöver**: je Grenzpaar (Angreifer, Verteidiger, Armeen) die Erfolgswahrscheinlichkeit eines Angriffs, erwartete Verluste und ein Ranking der besten Angriffe und Verstärkungsziele für beide Seiten. Hilfsmittel: Würfelwahrscheinlichkeiten im Risiko (Angreifer maximal 3 Würfel, Verteidiger maximal 2 Würfel, bei Gleichstand gewinnt der Verteidiger) und eine Monte-Carlo-Simulation in Python, deren Ergebnisse als Tabelle eingefügt werden können.
4. **Brett-Schema**: ein schematisches Bild des Bretts mit Gebieten, Farben und Armeezahlen (zum Beispiel mit matplotlib gezeichnet und als Bild eingebettet, oder als Zellraster mit farbigen Zellen).

## Bekannte Unsicherheiten
- Die Armeezahlen wurden zuerst aus den Fotos geschätzt und danach vom Nutzer korrigiert und bestätigt. Sie gelten als zuverlässig.
- Die Zahlen für die Gebiete, die der Nutzer nicht einzeln genannt hat, hat er mit "der Rest stimmt" bestätigt.
- Zugfolge, Karten und die Siegbedingung (Weltherrschaft oder Missionen) sind unbekannt.

## Vorschlag für den ersten Schritt in Claude Code
Lies `state.json`, baue daraus mit openpyxl die Datei `risiko_stand.xlsx` mit den vier Reitern, prüfe sie mit LibreOffice auf Formelfehler und schreibe die Manöver-Wahrscheinlichkeiten über eine kleine Simulation oder die exakte Rekursion.

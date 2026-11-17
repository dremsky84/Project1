# Konzept: AYTO-Rechner (Arbeitstitel, Vorschlag)

## Idee
Eine Android-App, die bei "Are You The One?" die möglichen Perfect-Match-Paarungen mathematisch eingrenzt. Der Nutzer trägt die Ergebnisse der Truth Booths und der Matching Ceremonies ein. Die App berechnet daraus alle noch möglichen Lösungen, die Wahrscheinlichkeit jedes Paares und den besten nächsten Tipp bzw. das beste nächste Truth-Booth-Paar (Vorschlag).

## Zielplattform und Technik
- Vorschlag: Native Android-App mit Kotlin und Jetpack Compose. Gründe: Ergebnis ist direkt eine APK, die Berechnung läuft schnell und offline, keine Zusatz-Laufzeit nötig.
- Vorschlag: Rechenkern als eigenes, UI-freies Kotlin-Modul. So lässt er sich am PC mit Unit-Tests prüfen.
- Vorschlag: Build der APK über GitHub Actions (Repo `dremsky84/Project1`), weil diese Umgebung kein Android-SDK hat (geprüft: `sdkmanager`, `adb` fehlen; Java und Gradle sind vorhanden).

## Kernmechaniken
Regeln der Show (Stand der Recherche, siehe Quellen unten):
- 10 Frauen und 10 Männer; Produktion legt vorab geheim eine perfekte Zuordnung fest. Finden alle ihre Matches innerhalb von 10 Matching Ceremonies, wird das Preisgeld (1 Mio. $) geteilt.
- **Truth Booth:** Ein gewähltes Paar wird geprüft. Antwort nur "Perfect Match" oder "kein Match". Ein bestätigtes Paar steht fest, ein verneintes Paar scheidet aus.
- **Matching Ceremony:** Alle bilden eine komplette Paarung. Ergebnis ist nur die Anzahl richtiger Paare ("Lichter"), nicht welche.
- **Blackout:** 0 Lichter (ohne bereits bestätigte Matches) kostet Preisgeld: $250.000 in Staffeln 3 und 4, 50 % in Staffel 5. Für spätere Staffeln nicht verifiziert.
- Staffelvarianten: Manche Staffeln haben 11 Matches (eine Person hat zwei Matches). Staffel 8 war ohne Geschlechtergrenzen (beliebige Paare unter 20 Personen).

Berechnung (Vorschlag):
1. Alle 10! = 3.628.800 Zuordnungen sind anfangs möglich.
2. Jede Truth-Booth-Info und jede Ceremony (Treffer-Anzahl) filtert diese Menge. Die Prüfung ist pro Zuordnung billig; 3,6 Mio. passen als kompakte Arrays in den Speicher eines Handys.
3. Aus den übrigen Lösungen entsteht eine 10x10-Wahrscheinlichkeitsmatrix (Anteil der Lösungen, in denen Paar X–Y vorkommt).
4. Empfehlung nächster Ceremony-Tipp: eine noch mögliche Lösung, die die erwartete Restmenge minimiert bzw. die Entropie maximiert (wie bei Mastermind).
5. Empfehlung Truth Booth: Paar mit Wahrscheinlichkeit nahe 50 % bzw. maximalem Informationsgewinn.
6. Anzeige "Anzahl verbleibender Lösungen" und Hinweis, wenn Eingaben widersprüchlich sind (0 Lösungen).

## Steuerung
Touch: Namen der Kandidaten eintragen, Paare per Antippen auswählen, Ergebnisse per Zahlenfeld eingeben (Vorschlag).

## Bildschirme
Vorschlag:
1. Start/Setup: Namen der Frauen und Männer eintragen, Variante wählen.
2. Ceremony eintragen: komplette Paarung wählen und Lichter-Anzahl eingeben.
3. Truth Booth eintragen: Paar und Ergebnis.
4. Wahrscheinlichkeitsmatrix: Heatmap 10x10 mit Prozentwerten.
5. Empfehlung: bester nächster Tipp und bestes Truth-Booth-Paar.
6. Verlauf: Liste aller Eingaben mit Rückgängig.

## Build und Auslieferung
- Code und Rechenkern-Tests werden hier erstellt und getestet (Java/Gradle vorhanden).
- Die APK wird per GitHub Actions gebaut und als Artefakt bereitgestellt (Vorschlag), da lokal kein Android-SDK existiert. Ob du die APK am Handy oder PC herunterlädst, ist eine offene Frage.
- Einen lokalen APK-Build mit eigenem SDK nur, falls du am PC arbeitest und das SDK dort hast.

## Umfang Version 0.1
Vorschlag:
- Variante 10x10 ohne Zusatzperson.
- Eingabe von Truth Booths und Ceremonies, Filterung aller Lösungen, Wahrscheinlichkeitsmatrix, einfacher Tipp-Vorschlag (höchste Wahrscheinlichkeiten).
- Speicherung des Verlaufs lokal auf dem Gerät.
- Nicht in 0.1: 11er-Variante, Staffel 8 (ohne Geschlechtergrenzen, 654 Mio. Paarungen, braucht Sampling statt Aufzählung), Entropie-Optimierung, Preisgeld-Rechner.

## Annahmen
- Du willst die klassische Variante (zwei Gruppen à 10).
- Die App wird manuell mit Daten aus der Sendung gefüttert, keine Anbindung an Streamingdienste.
- Deutsche Oberfläche.
- Keine Veröffentlichung im Play Store, nur eine APK zum Installieren.

## Offene Fragen
1. Arbeitest du gerade am PC oder am Handy? (Bestimmt, wie die APK gebaut und geliefert wird.)
2. Welche Staffel/Version schaust du (US, deutsche Ausgabe, mit 11 Matches, Staffel 8)?
3. Soll die App nur rechnen oder auch den Preisgeld-Verlust bei Blackouts anzeigen?
4. Name der App und gewünschter Look (Vorschlag: dunkles Design mit Heatmap)?
5. Soll v0.1 zuerst nur die Kernrechnung enthalten (siehe oben)?

## Quellen der Recherche
Regeldetails stammen aus Websuchen. Wikipedia war aus dieser Umgebung nicht abrufbar. Ein Truth-Booth-Limit pro Folge und die Regeln der Staffeln 6–9 sowie der deutschen Version sind nicht verifiziert.

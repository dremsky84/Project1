# Konzept: AytO Matcher

## Idee
"AytO Matcher" ist eine Android-App für die deutsche Ausgabe von "Are You The One?" mit 11 Frauen und 10 Männern. Der Nutzer trägt die Ergebnisse der Truth Booths und der Matching Ceremonies ein. Die App berechnet daraus alle noch möglichen Lösungen, die Wahrscheinlichkeit jedes Paares und einen Vorschlag für den nächsten Tipp (Vorschlag).

## Zielplattform und Technik
- Vorschlag: Native Android-App mit Kotlin und Jetpack Compose. Grund: Ergebnis ist direkt eine APK, die Berechnung läuft offline und schnell.
- Vorschlag: Der Rechenkern ist ein eigenes Kotlin-Modul ohne UI, damit ich ihn hier mit Unit-Tests prüfen kann.
- Vorschlag: Die APK wird über GitHub Actions gebaut, weil du am Handy arbeitest und hier kein Android-SDK vorhanden ist (geprüft: `sdkmanager` und `adb` fehlen).

## Kernmechaniken
Regeln (deine Angaben, ergänzt durch Recherche):
- 11 Frauen, 10 Männer. Jede Frau hat genau ein Perfect Match. Genau ein Mann hat zwei Perfect Matches, alle anderen Männer eines. Damit gibt es 10 × C(11,2) × 9! = 199.584.000 mögliche Lösungen am Anfang.
- **Truth Booth:** Ein Paar wird geprüft, Antwort nur Match oder kein Match.
- **Matching Ceremony:** Alle bilden Paare, Ergebnis ist nur die Anzahl der Treffer, nicht welche.
- Ein Preisgeld-Rechner ist nicht Teil der App.
- Annahme, bitte bestätigen: In einer Ceremony wird jede Frau genau einem Mann zugeordnet, ein Mann darf dabei zwei Frauen haben. Das Ergebnis ist die Trefferzahl 0 bis 11.

Berechnung (Vorschlag):
1. Eine Lösung ordnet jeder Frau genau einen Mann zu, sodass jeder Mann mindestens eine Frau hat.
2. Truth-Booth-Ergebnisse und Ceremony-Trefferzahlen sind Bedingungen an diese Zuordnungen.
3. 199,6 Mio. Lösungen passen nicht als Liste in den Handyspeicher. Deshalb durchsucht die App den Lösungsraum per Backtracking mit frühem Abbruch: Sobald eine Teilzuordnung eine Bedingung sicher verletzt, wird der ganze Zweig verworfen. Dabei zählt sie, wie oft jedes Paar in gültigen Lösungen vorkommt.
4. Daraus entsteht eine 11×10-Wahrscheinlichkeitsmatrix und die Zahl der verbleibenden Lösungen.
5. Wird die Rechenzeit bei wenig Vorwissen zu lang, wechselt die App auf Zufallsstichproben und kennzeichnet die Werte als Schätzung.
6. Tipp-Vorschlag in v0.1: die gültige Zuordnung mit den höchsten Wahrscheinlichkeiten. Truth-Booth-Vorschlag: Paar mit Wahrscheinlichkeit nahe 50 %.
7. Widersprüchliche Eingaben (0 Lösungen) werden gemeldet.

## Steuerung
Touch: Namen eintragen, Paare per Antippen wählen, Trefferzahl über ein Zahlenfeld eingeben.

## Bildschirme
Vorschlag, dunkles Design mit Heatmap:
1. Setup: Namen der 11 Frauen und 10 Männer.
2. Ceremony eintragen: jede Frau einem Mann zuordnen, Trefferzahl eingeben.
3. Truth Booth eintragen: Paar und Ergebnis.
4. Wahrscheinlichkeitsmatrix als Heatmap mit Prozentwerten.
5. Empfehlung: nächster Tipp und nächstes Truth-Booth-Paar.
6. Verlauf mit Rückgängig.

## Build und Auslieferung
- Du arbeitest am Handy. Ich schreibe Code und Rechenkern-Tests hier und prüfe den Rechenkern mit den Tests.
- Die APK baut GitHub Actions im Repo `dremsky84/Project1`. Vorschlag: Das Ergebnis wird als GitHub Release mit APK veröffentlicht, damit du sie direkt am Handy herunterladen und installieren kannst. Die APK wäre eine Debug-APK, du musst "Installation aus unbekannten Quellen" erlauben.
- Ich kann die APK hier nicht auf einem Gerät testen. Ob sie baut und läuft, sehen wir erst im Actions-Lauf und auf deinem Handy.

## Umfang Version 0.1
Vorschlag:
- Setup, Eingabe von Truth Booths und Ceremonies, Backtracking-Suche, Wahrscheinlichkeitsmatrix, einfacher Tipp-Vorschlag, lokaler Verlauf.
- Nicht in 0.1: Entropie-Optimierung des Tipps, Stichproben-Fallback (falls die Suche schnell genug ist), andere Staffelvarianten.

## Annahmen
- Es gibt keine weiteren Regeln als die oben genannten. Ich konnte die Regeln der deutschen Ausgabe nicht verifizieren, Wikipedia war nicht abrufbar.
- Die App wird manuell mit Daten aus der Sendung gefüttert.
- Deutsche Oberfläche, nur zum Installieren per APK, kein Play Store.

## Offene Fragen
1. Stimmt meine Annahme zur Ceremony (jede Frau genau einem Mann zugeordnet, ein Mann darf zwei bekommen, Ergebnis 0 bis 11 Treffer)? Falls anders: wie läuft sie in der deutschen Ausgabe ab?
2. Ist bekannt, welcher Mann das Doppel-Match hat, oder wird das erst durch die Booths klar?
3. Gibt es in der deutschen Ausgabe einen Truth Booth pro Folge, und wie viele Ceremonies gibt es?
4. Freigabe: Soll ich auf Basis dieses Konzepts mit Version 0.1 beginnen?

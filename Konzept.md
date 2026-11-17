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
- **Matchbox** (das Gegenstück zur Truth Booth): Ein Paar, das nach seinem Date von der Gruppe gewählt wird, wird geprüft. Antwort nur Match oder kein Match.
- **Matching Night** (am Ende jeder Doppelfolge): Es werden genau 10 Paare gebildet. Jeder Mann bekommt genau eine Frau, eine Frau bleibt ohne Partner. Das Ergebnis ist die Zahl der Lichter (0 bis 10), nicht welche Paare leuchten.
- Per Matchbox bestätigte Paare verlassen das Haus. Ab dann sind sie in jeder weiteren Matching Night immer ein leuchtendes Licht. Die übrigen Männer und Frauen bilden die restlichen Paare. Wird in der Matchbox das Doppel-Match bestätigt, verlässt auch die dritte Person, also die zweite Frau des Mannes, das Haus. Dann sind es zwei dauerhaft leuchtende Lichter, und der Rest ist eine normale 9×9-Zuordnung mit nur noch 9! = 362.880 Lösungen.
- Es gibt 10 Matching Nights. Nur wenn in der 10. Matching Night alle zehn Lichter angehen, gewinnt die Gruppe 200.000 €. Ein Abend ohne Treffer kostet 50.000 €. Einen Preisgeld-Rechner baut die App nicht.
- Quelle: RTL+-Seite zu Staffel 7 (Auszug von dir).

Berechnung (Vorschlag):
1. Eine Lösung ordnet jeder Frau genau einen Mann zu, sodass jeder Mann mindestens eine Frau hat.
2. Matchbox-Ergebnisse und Lichter-Anzahlen der Matching Nights sind Bedingungen an diese Zuordnungen. Eine Matching Night zählt, wie viele ihrer 10 Paare in der echten Lösung vorkommen. Der Mann mit dem Doppel-Match kann in einer Night nur eine seiner beiden Frauen bekommen.
3. 199,6 Mio. Lösungen passen nicht als Liste in den Handyspeicher. Deshalb durchsucht die App den Lösungsraum per Backtracking mit frühem Abbruch: Sobald eine Teilzuordnung eine Bedingung sicher verletzt, wird der ganze Zweig verworfen. Dabei zählt sie, wie oft jedes Paar in gültigen Lösungen vorkommt.
4. Daraus entsteht eine 11×10-Wahrscheinlichkeitsmatrix und die Zahl der verbleibenden Lösungen.
5. Wird die Rechenzeit bei wenig Vorwissen zu lang, wechselt die App auf Zufallsstichproben und kennzeichnet die Werte als Schätzung.
6. Tipp-Vorschlag in v0.1: die gültige Zuordnung mit den höchsten Wahrscheinlichkeiten. Truth-Booth-Vorschlag: Paar mit Wahrscheinlichkeit nahe 50 %.
7. Widersprüchliche Eingaben (0 Lösungen) werden gemeldet.

## Steuerung
Touch: Namen eintragen, Paare per Antippen wählen, Lichter-Anzahl über ein Zahlenfeld eingeben.

## Bildschirme
Vorschlag, dunkles Design mit Heatmap:
1. Setup: Namen der 11 Frauen und 10 Männer.
2. Matching Night eintragen: jedem Mann eine Frau zuordnen (die übrige Frau wird automatisch als "ohne Partner" angezeigt), Lichter-Anzahl 0 bis 10 eingeben.
3. Matchbox eintragen: Paar und Ergebnis (kein Match, Match oder Doppel-Match mit Angabe der zweiten Frau).
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
- Es gibt keine weiteren Regeln als die oben genannten. Die Regeln der deutschen Ausgabe stützen sich auf die RTL+-Seite, die du mir gezeigt hast, und auf deine Angaben.
- Wer das Doppel-Match hat, ist anfangs unbekannt (deine Angabe). Die App rechnet das mit.
- Die Lichter-Anzahl, die du eingibst, ist die Zahl, die in der Show angezeigt wird, einschließlich der bestätigten Paare. Die App zieht deren Lichter selbst ab und trägt bestätigte Paare automatisch in jede Matching Night ein.
- Die App wird manuell mit Daten aus der Sendung gefüttert.
- Deutsche Oberfläche, nur zum Installieren per APK, kein Play Store.

## Offene Fragen
1. Freigabe: Soll ich auf Basis dieses Konzepts mit Version 0.1 beginnen?

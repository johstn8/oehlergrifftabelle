Prompt für ChatGPT Codex – Klarinetten-Grifftabelle automatisch erzeugen
=======================================================================

Hinweis an Codex  
Ziel ist ein vollständig lauffähiges Python-Skript (Dateiname generate_clarinet_chart.py), das aus einer JSON-Datei eine druckfertige PDF-Grifftabelle (Oehler-Klarinette in B) erstellt.  
Eine einzige Datei, einzige Fremdbibliothek: reportlab (pip install reportlab).  
Code bitte gründlich kommentieren (Deutsch) und am Ende eine kurze Bedienungsanleitung plus Beispiel-JSON angeben.

--------------------------------------------------------------------
1  Funktionsumfang
--------------------------------------------------------------------
- Skript wird per CLI aufgerufen:  
  python generate_clarinet_chart.py fingering.json ausgabe.pdf

- Eingabedatei ist JSON, Reihenfolge der Einträge = Reihenfolge der Diagramme im PDF  
  Beispielobjekt:  
    {
      "note": "Fis / Ges",
      "staff_offset": -5,
      "fingering": [0,1,1,1,1,1,0,0]
    }

- Datenfelder  
  • note: String, Text über dem Diagramm (z. B. Fis / Ges)  
  • staff_offset: Integer, Halbtonschritte relativ zur untersten Notenlinie  
    0 = unterste Linie, +1 = erster Zwischenraum, +2 = zweite Linie usw.; negative Werte für tiefe Töne  
  • fingering: Liste von acht Ganzzahlen (0 oder 1)  
    Reihenfolge von oben nach unten:  
      - LH-Pinky  
      - LH 1  
      - LH 2  
      - LH 3  
      - RH 1  
      - RH 2  
      - RH 3  
      - RH-Pinky  
    1 bedeutet geschlossene Klappe (schwarzer Punkt), 0 bedeutet offen (weißer Kreis)

- PDF-Layout  
  • Seitenformat A4 hoch, Ränder 20 mm  
  • Raster mit 4 Spalten, beliebig viele Zeilen, automatischer Seitenumbruch  
  • Jede Zelle enthält  
      - Titel (fetter Notenname)  
      - Notensystem mit fünf Linien plus Note (schwarze Ellipse, leicht geneigt)  
      - Rechte Spalte mit acht Griffkreisen; Punkt gefüllt oder leer gemäß fingering-Liste

- Zeichnen mit reportlab  
  • Verwende Canvas-Methoden line, circle, ellipse, drawString  
  • Einheiten mm über reportlab.lib.units.mm  
  • Schriftarten Helvetica und Helvetica-Bold

- Fehlerbehandlung  
  • Prüfe Zahl der CLI-Argumente, Existenz von Dateien, JSON-Schema und Länge der fingering-Liste  
  • Deutschsprachige Fehlermeldungen

- Dokumentation und Demo  
  • Umfangreicher Docstring im Kopf der Datei  
  • Wird das Skript ohne CLI-Argumente gestartet, soll es eine Demo erzeugen:  
      - Beispiel-JSON schreiben (demo_fingering.json)  
      - PDF rendern (clarinet_chart_demo.pdf)

--------------------------------------------------------------------
2  Details zum Zeichnen
--------------------------------------------------------------------
- Notensystem  
  x_staff und y_staff mittig in der Zelle  
  fünf Linien, Abstand staff_spacing = 1.6 mm

- Notenkopf  
  horizontal zentriert über x_staff + staff_width / 2  
  vertikal y_staff + staff_offset × staff_spacing / 2  
  Ellipse etwa 3.8 mm breit, 2.8 mm hoch, schwarz gefüllt

- Griffkreise  
  x_circles rechts in der Zelle  
  oberster Kreis etwa 10 mm über Systemmittelpunkt  
  vertikaler Abstand circle_gap = 7 mm  
  Radius etwa 2.8 mm  
  Rahmen schwarz; Kreis gefüllt, wenn Wert 1

- Titel  
  Textgröße 12 pt fett  
  zentriert, etwa 4 mm über der obersten Systemlinie

--------------------------------------------------------------------
3  Beispiel-JSON für Demo-Run
--------------------------------------------------------------------
[
  {"note":"E","staff_offset":-7,"fingering":[1,1,1,1,1,1,1,0]},
  {"note":"F","staff_offset":-6,"fingering":[0,1,1,1,1,1,1,0]},
  {"note":"Fis/Ges","staff_offset":-5,"fingering":[0,1,1,1,1,1,0,0]},
  {"note":"G","staff_offset":-4,"fingering":[0,1,1,1,0,0,0,0]},
  {"note":"Gis/As","staff_offset":-3,"fingering":[1,1,1,0,0,0,0,1]},
  {"note":"A","staff_offset":-2,"fingering":[0,1,1,0,0,0,0,0]},
  {"note":"Ais/B","staff_offset":-1,"fingering":[1,1,0,0,0,0,0,1]},
  {"note":"H","staff_offset":0,"fingering":[0,1,0,0,0,0,0,0]},
  {"note":"C","staff_offset":1,"fingering":[0,0,1,1,1,0,0,0]},
  {"note":"Cis/Des","staff_offset":2,"fingering":[1,0,1,1,1,0,0,1]},
  {"note":"D","staff_offset":3,"fingering":[0,0,1,1,0,0,0,0]},
  {"note":"Dis/Es","staff_offset":4,"fingering":[1,0,1,0,0,0,0,1]}
]

--------------------------------------------------------------------
4  Mini-How-To (soll Codex nach dem Code ausgeben)
--------------------------------------------------------------------
- Voraussetzungen  
  python -m pip install reportlab

- PDF erzeugen  
  python generate_clarinet_chart.py klarinette.json chart.pdf

- Ohne Argumente starten  
  Skript legt demo_fingering.json an  
  Skript erzeugt clarinet_chart_demo.pdf

--------------------------------------------------------------------
5  Qualitätskriterien
--------------------------------------------------------------------
- Lesbarkeit: klare Struktur, sprechende Funktionsnamen  
- Dokumentation: ausführliche Kommentare und Docstring  
- Robustheit: JSON-Validierung, verständliche Fehlermeldungen  
- Layout: exakte Positionierung, gleichmäßiges Raster  
- Portabilität: reines Python ab 3.8, einzige Abhängigkeit reportlab

--------------------------------------------------------------------
Bitte ausschließlich den vollständigen Python-Quelltext (eine Datei) liefern, danach Bedienungsanleitung und Beispiel-JSON als Textausschnitt.

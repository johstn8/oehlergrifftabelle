# Klarinetten-Grifftabelle

Dieses Repository enthält das Skript `generate_clarinet_chart.py`. Es liest Griffdaten für die Oehler-Klarinette aus einer JSON-Datei und erzeugt daraus eine PDF-Grifftabelle.

## Voraussetzungen
- Python 3.8 oder neuer
- [reportlab](https://pypi.org/project/reportlab/) installieren:
  ```bash
  python -m pip install reportlab
  ```

## Verwendung
Eine PDF-Tabelle erzeugen Sie mit:
```bash
python generate_clarinet_chart.py eingabe.json ausgabe.pdf
```

Wird das Skript ohne Argumente gestartet, schreibt es eine Beispiel-JSON `demo_fingering.json` und rendert daraus `clarinet_chart_demo.pdf`.

## JSON-Format
Die Eingabedatei enthält eine Liste von Objekten mit folgenden Feldern:
- `note`: Textbezeichnung des Tons
- `staff_offset`: Lage der Note in Halbtonschritten relativ zur untersten Notenlinie
- `fingerings`: Liste von Griffvarianten. Jeder Griff besteht aus acht Werten (0 = offen, 1 = geschlossen) in der Reihenfolge:
  LH-Pinky, LH&nbsp;1, LH&nbsp;2, LH&nbsp;3, RH&nbsp;1, RH&nbsp;2, RH&nbsp;3, RH-Pinky

Ein Minimalbeispiel:
```json
[
  {
    "note": "Fis/Ges",
    "staff_offset": -5,
    "fingerings": [[0, 1, 1, 1, 1, 1, 0, 0]]
  }
]
```

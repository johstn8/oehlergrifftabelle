"""Klarinetten-Grifftabelle automatisch erzeugen
=================================================

Dieses Skript liest eine JSON-Datei mit Griff-Informationen für die
Oehler-Klarinette in B und erstellt daraus eine druckfertige
Grifftabelle im PDF-Format. Es genügt ein einziger Aufruf:

    python generate_clarinet_chart.py eingabe.json ausgabe.pdf

Wird das Skript ohne Argumente gestartet, erzeugt es eine Demo-Datei
(demo_fingering.json) sowie eine Beispiel-PDF (clarinet_chart_demo.pdf).

Das JSON muss eine Liste von Objekten enthalten, die jeweils folgende
Schlüssel besitzen:

    note         Text über dem Diagramm (z. B. "Fis / Ges")
    staff_offset Halbtonschritte relativ zur untersten Notenlinie
    fingerings   Liste von Griff-Listen. Jede Griff-Liste besteht aus acht
                 0/1-Werten (geschlossene Klappen)

Ein Eintrag sieht somit beispielsweise so aus:

    {
        "note": "Fis / Ges",
        "staff_offset": -5,
        "fingerings": [[0, 1, 1, 1, 1, 1, 0, 0]]
    }

Einzige benötigte Fremdbibliothek ist reportlab.

"""

import json
import sys
from pathlib import Path
from typing import List, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

# Konstanten für das Seitenlayout
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm
COLUMNS = 4
ROW_HEIGHT = 65 * mm
STAFF_SPACING = 1.6 * mm
STAFF_WIDTH = 20 * mm
NOTE_WIDTH = 3.8 * mm
NOTE_HEIGHT = 2.8 * mm
CIRCLE_RADIUS = 2.8 * mm
CIRCLE_GAP = 7 * mm
TOP_CIRCLE_OFFSET = 10 * mm
TITLE_OFFSET = 4 * mm
FINGERING_SPACING = 10 * mm


class FingeringEntry(Dict[str, object]):
    """Typhilfe für einzelne Griffdaten."""


def validate_data(data: object) -> List[FingeringEntry]:
    """Prüft die JSON-Daten auf korrektes Schema.

    Args:
        data: Ergebnis von ``json.load``.

    Returns:
        Liste von ``FingeringEntry``.

    Raises:
        ValueError: falls das Format ungültig ist.
    """
    if not isinstance(data, list):
        raise ValueError("JSON muss eine Liste von Objekten enthalten")

    result: List[FingeringEntry] = []
    for i, entry in enumerate(data, 1):
        if not isinstance(entry, dict):
            raise ValueError(f"Eintrag {i} ist kein Objekt")
        if "note" not in entry or "staff_offset" not in entry:
            raise ValueError(f"Eintrag {i} fehlt ein erforderliches Feld")
        if "fingerings" not in entry and "fingering" not in entry:
            raise ValueError(f"Eintrag {i} muss 'fingerings' oder 'fingering' enthalten")
        note = entry["note"]
        staff_offset = entry["staff_offset"]
        fingerings_raw = entry.get("fingerings")
        if fingerings_raw is None:
            fingerings_raw = [entry["fingering"]]
        if not isinstance(note, str):
            raise ValueError(f"Eintrag {i}: 'note' muss ein String sein")
        if not isinstance(staff_offset, int):
            raise ValueError(f"Eintrag {i}: 'staff_offset' muss Integer sein")

        fingerings: List[List[int]] = []
        if not isinstance(fingerings_raw, list) or len(fingerings_raw) == 0:
            raise ValueError(f"Eintrag {i}: 'fingerings' muss eine nichtleere Liste sein")
        for j, fingering in enumerate(fingerings_raw, 1):
            if not (isinstance(fingering, list) and len(fingering) == 8 and all(v in (0, 1) for v in fingering)):
                raise ValueError(
                    f"Eintrag {i}, Griff {j}: Muss Liste von 8 Werten 0 oder 1 sein"
                )
            fingerings.append(list(fingering))

        result.append({"note": note, "staff_offset": staff_offset, "fingerings": fingerings})
    return result


def draw_cell(c: Canvas, x: float, y: float, width: float, height: float, entry: FingeringEntry) -> None:
    """Zeichnet ein einzelnes Griffdiagramm.

    Parameters:
        c: Aktuelles Canvas-Objekt
        x: linke untere X-Koordinate der Zelle
        y: linke untere Y-Koordinate der Zelle
        width: Breite der Zelle
        height: Höhe der Zelle
        entry: Datensatz für diese Zelle
    """

    # Mittelpunkt des Notensystems in der Zelle
    x_center = x + width / 2
    y_center = y + height / 2

    # Notennamen (Titel)
    c.setFont("Helvetica-Bold", 12)
    title_y = y_center + 2 * STAFF_SPACING + TITLE_OFFSET
    c.drawCentredString(x_center, title_y, entry["note"])

    # Notensystem zeichnen
    x_staff = x_center - STAFF_WIDTH / 2
    for i in range(5):
        y_line = y_center + (i - 2) * STAFF_SPACING
        c.line(x_staff, y_line, x_staff + STAFF_WIDTH, y_line)

    # Notenkopf zeichnen (leicht geneigt)
    bottom_line = y_center - 2 * STAFF_SPACING
    note_y = bottom_line + entry["staff_offset"] * (STAFF_SPACING / 2)
    note_x = x_center
    c.saveState()
    c.translate(note_x, note_y)
    c.rotate(-20)
    c.ellipse(-NOTE_WIDTH / 2, -NOTE_HEIGHT / 2, NOTE_WIDTH / 2, NOTE_HEIGHT / 2, stroke=1, fill=1)
    c.restoreState()

    # Griffkreise rechts in der Zelle; bei mehreren Griffen nebeneinander
    fingerings = entry["fingerings"]
    spacing = FINGERING_SPACING
    start_x = x + width - CIRCLE_RADIUS - 2 * mm - (len(fingerings) - 1) * spacing
    for col, fingering in enumerate(fingerings):
        circle_x = start_x + col * spacing
        for idx, closed in enumerate(fingering):
            circle_y = y_center + TOP_CIRCLE_OFFSET - idx * CIRCLE_GAP
            c.circle(circle_x, circle_y, CIRCLE_RADIUS, stroke=1, fill=int(closed))


def generate_pdf(data: List[FingeringEntry], output_path: Path) -> None:
    """Erzeugt das PDF mit allen Griffdiagrammen."""
    c = Canvas(str(output_path), pagesize=A4)
    page_width, page_height = PAGE_WIDTH, PAGE_HEIGHT
    usable_width = page_width - 2 * MARGIN
    usable_height = page_height - 2 * MARGIN
    rows_per_page = int(usable_height // ROW_HEIGHT) or 1
    cells_per_page = rows_per_page * COLUMNS
    col_width = usable_width / COLUMNS

    for idx, entry in enumerate(data):
        if idx and idx % cells_per_page == 0:
            c.showPage()
        pos_in_page = idx % cells_per_page
        row = pos_in_page // COLUMNS
        col = pos_in_page % COLUMNS
        x = MARGIN + col * col_width
        y = page_height - MARGIN - (row + 1) * ROW_HEIGHT
        draw_cell(c, x, y, col_width, ROW_HEIGHT, entry)

    c.save()


def load_json(path: Path) -> List[FingeringEntry]:
    """Liest und validiert die JSON-Datei."""
    if not path.exists():
        raise FileNotFoundError(f"Datei '{path}' existiert nicht")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return validate_data(data)


def demo_data() -> List[FingeringEntry]:
    """Gibt eine kleine Demo-Sammlung von Griffen zurück."""
    return [
        {
            "note": "E",
            "staff_offset": -7,
            "fingerings": [
                [1, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 1, 1],
            ],
        },
        {
            "note": "F",
            "staff_offset": -6,
            "fingerings": [
                [0, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 1, 1, 1, 1, 1, 1],
            ],
        },
        {
            "note": "Fis/Ges",
            "staff_offset": -5,
            "fingerings": [[0, 1, 1, 1, 1, 1, 0, 0]],
        },
        {
            "note": "G",
            "staff_offset": -4,
            "fingerings": [[0, 1, 1, 1, 0, 0, 0, 0]],
        },
        {
            "note": "Gis/As",
            "staff_offset": -3,
            "fingerings": [[1, 1, 1, 0, 0, 0, 0, 1]],
        },
        {
            "note": "A",
            "staff_offset": -2,
            "fingerings": [[0, 1, 1, 0, 0, 0, 0, 0]],
        },
        {
            "note": "Ais/B",
            "staff_offset": -1,
            "fingerings": [[1, 1, 0, 0, 0, 0, 0, 1]],
        },
        {
            "note": "H",
            "staff_offset": 0,
            "fingerings": [[0, 1, 0, 0, 0, 0, 0, 0]],
        },
        {
            "note": "C",
            "staff_offset": 1,
            "fingerings": [[0, 0, 1, 1, 1, 0, 0, 0]],
        },
        {
            "note": "Cis/Des",
            "staff_offset": 2,
            "fingerings": [[1, 0, 1, 1, 1, 0, 0, 1]],
        },
        {
            "note": "D",
            "staff_offset": 3,
            "fingerings": [[0, 0, 1, 1, 0, 0, 0, 0]],
        },
        {
            "note": "Dis/Es",
            "staff_offset": 4,
            "fingerings": [[1, 0, 1, 0, 0, 0, 0, 1]],
        },
    ]


def run_demo() -> None:
    """Erzeugt Demo-JSON und Demo-PDF."""
    demo_json = Path("demo_fingering.json")
    demo_pdf = Path("clarinet_chart_demo.pdf")
    data = demo_data()
    with demo_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    generate_pdf(data, demo_pdf)
    print("Demo-Dateien erzeugt:")
    print(f"  JSON: {demo_json}")
    print(f"  PDF : {demo_pdf}")


def main(args: List[str]) -> None:
    """Haupteinstiegspunkt des Skripts."""
    if len(args) == 0:
        run_demo()
        return
    if len(args) != 2:
        print(
            "Fehler: Bitte genau zwei Argumente angeben: JSON-Datei und Ausgabe-PDF",
            file=sys.stderr,
        )
        sys.exit(1)

    json_path = Path(args[0])
    pdf_path = Path(args[1])
    try:
        data = load_json(json_path)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Fehler beim Einlesen der JSON-Datei: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        generate_pdf(data, pdf_path)
    except Exception as e:  # Allgemeiner Fehler beim PDF-Schreiben
        print(f"Fehler beim Erzeugen des PDFs: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

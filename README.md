# QR-Code Scanner für Versandetiketten

Eine Desktop-Anwendung zum Scannen von QR-Codes auf Versandetiketten und Extrahieren von relevanten Informationen wie Auftragsnummer, Paketnummer und Kundenname.

## Funktionen

- QR-Code-Erkennung über Webcam oder Bilddateien
- Extraktion von Auftragsnummer, Paketnummer und Kundenname
- Historie der gescannten QR-Codes
- Export der Scan-Ergebnisse als CSV
- Einfache und intuitive Benutzeroberfläche

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Pip (Python-Paketmanager)
- Auf Windows: Microsoft Visual C++ Redistributable (für OpenCV und pyzbar)

### Installationsschritte

1. Repository klonen oder herunterladen:
   ```
   git clone https://github.com/ihr-benutzername/qr-scanner-app.git
   cd qr-scanner-app
   ```

2. Abhängigkeiten installieren:
   ```
   pip install -r requirements.txt
   ```

3. Auf Windows: Stellen Sie sicher, dass die benötigten DLLs für pyzbar verfügbar sind. Details finden Sie auf der [pyzbar-Seite](https://github.com/NaturalHistoryMuseum/pyzbar/).

## Verwendung

1. Anwendung starten:
   ```
   python main.py
   ```

2. Kamera auswählen und starten oder QR-Code aus Datei scannen
3. Gescannte Daten werden automatisch extrahiert und angezeigt
4. Daten können in CSV exportiert werden

## Projektstruktur

```
qr_scanner_app/
├── main.py                  # Haupteinstiegspunkt der Anwendung
├── requirements.txt         # Abhängigkeiten
├── README.md                # Dokumentation
├── src/
│   ├── __init__.py
│   ├── gui/                 # GUI-Komponenten
│   │   ├── __init__.py
│   │   ├── main_window.py   # Haupt-GUI-Fenster
│   │   ├── scanner_widget.py # QR-Code Scanner Bereich
│   │   └── data_widget.py   # Daten-Anzeige Bereich
│   ├── scanner/             # Scanner-Komponenten
│   │   ├── __init__.py
│   │   ├── camera.py        # Kamerasteuerung
│   │   └── decoder.py       # QR-Code Dekodierungslogik
│   └── data/                # Daten-Komponenten
│       ├── __init__.py
│       ├── parser.py        # QR-Code Daten Parser
│       └── storage.py       # Speicherung der Scan-Ergebnisse
├── tests/
│   ├── __init__.py
│   ├── test_scanner.py
│   └── test_parser.py
└── resources/
    └── icons/              # GUI-Icons
```

## Anpassungen und Erweiterungen

Die Anwendung kann leicht an verschiedene Arten von QR-Codes und Etiketten angepasst werden:

- Ändern Sie die Parsing-Logik in `src/data/parser.py`, um verschiedene QR-Code-Formate zu unterstützen
- Erweitern Sie die GUI für zusätzliche Funktionen
- Integrieren Sie externe Barcode-Scanner über die USB-Schnittstelle

## Lizenz

MIT Lizenz
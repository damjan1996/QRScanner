#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QR-Code Analyse-Skript
----------------------
Einfaches Skript zur Analyse von QR-Codes in Bildern
"""

import os
import sys
import cv2
import argparse
from pyzbar.pyzbar import decode
import re


def decode_qr_code(image_path):
    """Decodiert QR-Codes in einem Bild"""
    # Bild laden
    print(f"Analysiere: {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print(f"Fehler: Bild {image_path} konnte nicht geladen werden")
        return []

    # Bild in Graustufen konvertieren (bessere Erkennungsrate)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # QR-Codes decodieren
    qr_codes = decode(gray)

    results = []
    for qr in qr_codes:
        # QR-Code-Daten extrahieren
        raw_data = qr.data.decode('utf-8', errors='ignore')

        # Standardwerte
        auftrags_nr = ""
        paket_nr = ""
        kunden_name = ""

        # Spezielles durch ^ getrenntes Format (hat höchste Priorität)
        if '^' in raw_data:
            parts = raw_data.split('^')

            # Wir benötigen mindestens 4 Teile für Auftragsnummer und Paketnummer
            if len(parts) >= 4:
                # Auftragsnummer ist im zweiten Feld (Index 1)
                auftrags_nr = parts[1]

                # Paketnummer ist im vierten Feld (Index 3)
                paket_nr = parts[3]

                # Falls verfügbar, Kundennummer oder ID im dritten Feld (Index 2)
                if len(parts) > 2:
                    kunden_name = f"Kunden-ID: {parts[2]}"
        else:
            # Auftragsnummer versuchen zu extrahieren
            auftrags_nr_match = re.search(r'[A-Z]{2}-\d+', raw_data)
            if auftrags_nr_match:
                auftrags_nr = auftrags_nr_match.group(0)

            # Paketnummer versuchen zu extrahieren
            paket_nr_match = re.search(r'\d{10,}', raw_data)
            if paket_nr_match:
                paket_nr = paket_nr_match.group(0)

            # Kundenname versuchen zu extrahieren
            if "KUNDENNAME:" in raw_data:
                parts = raw_data.split("KUNDENNAME:")
                if len(parts) > 1:
                    kunden_name = parts[1].strip()
                    # Bis zum nächsten Schlüsselwort oder Ende nehmen
                    end_markers = ["PAKET-NR", "AUFTRAG", "\n"]
                    for marker in end_markers:
                        if marker in kunden_name:
                            kunden_name = kunden_name.split(marker)[0].strip()

            # Zusätzlicher Versuch für Referenz-Format
            if not auftrags_nr:
                referenz_match = re.search(r'Referenz:\s+([A-Z0-9-]+)', raw_data)
                if referenz_match:
                    auftrags_nr = referenz_match.group(1)

            # Nach "Tracking: XXX" oder ähnlichen Patterns suchen
            if not paket_nr:
                tracking_match = re.search(r'Tracking:\s+(\d+)', raw_data)
                if tracking_match:
                    paket_nr = tracking_match.group(1)

        # Ergebnis speichern
        result = {
            "raw_data": raw_data,
            "auftrags_nr": auftrags_nr,
            "paket_nr": paket_nr,
            "kunden_name": kunden_name
        }

        results.append(result)

    return results


def print_results(results):
    """Gibt die Analyseergebnisse aus"""
    if not results:
        print("Keine QR-Codes gefunden")
        return

    print("\nGefundene QR-Codes:")
    print("-" * 40)

    for i, result in enumerate(results):
        print(f"QR-Code #{i + 1}:")
        print(f"  Auftragsnummer: {result['auftrags_nr'] or 'Nicht gefunden'}")
        print(f"  Paketnummer: {result['paket_nr'] or 'Nicht gefunden'}")
        print(f"  Kundenname: {result['kunden_name'] or 'Nicht gefunden'}")
        print(f"  Rohdaten: {result['raw_data']}")
        print("-" * 40)


def parse_arguments():
    """Parst die Kommandozeilenargumente"""
    parser = argparse.ArgumentParser(description="QR-Code-Analyseprogramm")

    parser.add_argument("images", nargs="+", help="Bilder mit QR-Codes")

    return parser.parse_args()


def main():
    """Hauptfunktion"""
    args = parse_arguments()

    # Alle angegebenen Bilder analysieren
    for image_path in args.images:
        if not os.path.exists(image_path):
            print(f"Datei nicht gefunden: {image_path}")
            continue

        results = decode_qr_code(image_path)
        print_results(results)


if __name__ == "__main__":
    main()
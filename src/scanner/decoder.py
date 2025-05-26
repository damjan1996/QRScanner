#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QR-Code Decoder für den QR-Code Scanner
"""

import cv2
import numpy as np
from pyzbar.pyzbar import decode
import re


class QRDecoder:
    """Klasse zum Decodieren von QR-Codes"""

    def __init__(self):
        """Initialisiert den QR-Code Decoder"""
        self.last_positions = []

    def decode_image(self, image):
        """
        Decodiert QR-Codes in einem Bild

        Args:
            image: Das zu decodierende Bild

        Returns:
            list: Liste der decodierten QR-Codes mit Positionsdaten
        """
        self.last_positions = []
        decoded_objects = []

        try:
            # Bild in Graustufen konvertieren (bessere Erkennungsrate)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # QR-Codes decodieren
            qr_codes = decode(gray)

            for qr in qr_codes:
                # Polygon um den QR-Code ermitteln
                points = qr.polygon
                if points and len(points) > 0:
                    # In numpy-Array konvertieren
                    hull = np.array([point for point in points], dtype=np.int32)
                    hull = hull.reshape((-1, 1, 2))
                    self.last_positions.append(hull)

                # Daten aus dem QR-Code extrahieren
                raw_data = qr.data.decode('utf-8', errors='ignore')
                qr_data = self._parse_qr_data(raw_data)

                # Rohdaten hinzufügen
                qr_data["raw_data"] = raw_data

                decoded_objects.append(qr_data)
        except Exception as e:
            # Bei Fehlern während der Verarbeitung, Fehler loggen (in einer realen Anwendung)
            print(f"Fehler bei der QR-Code-Decodierung: {e}")

        return decoded_objects

    def get_last_positions(self):
        """
        Gibt die Positionen der zuletzt erkannten QR-Codes zurück

        Returns:
            list: Liste der Positionen
        """
        return self.last_positions

    def _parse_qr_data(self, data):
        """
        Extrahiert Informationen aus den QR-Code-Daten

        Args:
            data: Die zu parsenden Daten

        Returns:
            dict: Extrahierte Informationen
        """
        result = {
            "auftrags_nr": "",
            "paket_nr": "",
            "kunden_name": ""
        }

        # Spezielles durch ^ getrenntes Format (hat höchste Priorität)
        if '^' in data:
            parts = data.split('^')

            # Wir benötigen mindestens 4 Teile für Auftragsnummer und Paketnummer
            if len(parts) >= 4:
                # Auftragsnummer ist im zweiten Feld (Index 1)
                result["auftrags_nr"] = parts[1]

                # Paketnummer ist im vierten Feld (Index 3)
                result["paket_nr"] = parts[3]

                # Falls verfügbar, Kundennummer oder ID im dritten Feld (Index 2)
                if len(parts) > 2:
                    result["kunden_name"] = f"Kunden-ID: {parts[2]}"

                # Bei diesem Format die weiteren Prüfungen überspringen
                return result

        # Versuch, die Auftragsnummer zu extrahieren
        # Basierend auf den Beispielbildern, Muster "NL-XXXXXXX" oder ähnlich
        auftrags_nr_match = re.search(r'[A-Z]{2}-\d+', data)
        if auftrags_nr_match:
            result["auftrags_nr"] = auftrags_nr_match.group(0)

        # Versuch, die Paketnummer zu extrahieren
        # Langer numerischer Code, wie in den Beispielbildern
        paket_nr_match = re.search(r'\d{10,}', data)
        if paket_nr_match:
            result["paket_nr"] = paket_nr_match.group(0)

        # Versuch, den Kundennamen zu extrahieren
        # Dies ist schwieriger und hängt vom Format der QR-Code-Daten ab
        # Hier ein einfacher Ansatz basierend auf den Beispielbildern
        if "KUNDENNAME:" in data:
            parts = data.split("KUNDENNAME:")
            if len(parts) > 1:
                kunden_name = parts[1].strip()
                # Bis zum nächsten Schlüsselwort oder Ende nehmen
                end_markers = ["PAKET-NR", "AUFTRAG", "\n"]
                for marker in end_markers:
                    if marker in kunden_name:
                        kunden_name = kunden_name.split(marker)[0].strip()
                result["kunden_name"] = kunden_name

        # Zusätzliche Suche für andere Formate
        # Nach "Referenz: XXX" oder ähnlichen Patterns suchen
        if not result["auftrags_nr"]:
            referenz_match = re.search(r'Referenz:\s+([A-Z0-9-]+)', data)
            if referenz_match:
                result["auftrags_nr"] = referenz_match.group(1)

        # Nach "Tracking: XXX" oder ähnlichen Patterns suchen
        if not result["paket_nr"]:
            tracking_match = re.search(r'Tracking:\s+(\d+)', data)
            if tracking_match:
                result["paket_nr"] = tracking_match.group(1)

        return result
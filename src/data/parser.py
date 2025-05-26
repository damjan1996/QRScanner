#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parser für QR-Code-Daten von Versandetiketten
"""

import re
import json
import logging


class ShippingLabelParser:
    """Parser für die Daten von Versandetiketten"""

    def __init__(self):
        """Initialisiert den Parser"""
        self.logger = logging.getLogger("ShippingLabelParser")

    def parse_qr_content(self, content):
        """
        Parst den Inhalt eines QR-Codes von einem Versandetikett

        Args:
            content: Der zu parsende Inhalt

        Returns:
            dict: Extrahierte Daten
        """
        result = {
            "auftrags_nr": "",
            "paket_nr": "",
            "kunden_name": "",
            "raw_data": content
        }

        # Versuch, die Daten in verschiedenen Formaten zu parsen

        # 0. Spezielles durch ^ getrenntes Format (hat höchste Priorität)
        if '^' in content:
            delimited_result = self._parse_delimited_format(content)
            if delimited_result["auftrags_nr"] or delimited_result["paket_nr"]:
                return delimited_result

        # 1. Versuch: JSON-Format
        if self._try_parse_json(content, result):
            return result

        # 2. Versuch: URL-Format
        if self._try_parse_url(content, result):
            return result

        # 3. Versuch: Schlüssel-Wert-Format
        if self._try_parse_key_value(content, result):
            return result

        # 4. Versuch: Reguläre Ausdrücke für bekannte Muster
        self._try_parse_regex(content, result)

        return result

    def _parse_delimited_format(self, content):
        """
        Parst Daten im Format mit ^ als Trennzeichen:
        typ^auftragsnummer^kundennummer^paketnummer^anzahl^artikelnummer

        Args:
            content: Der zu parsende Inhalt

        Returns:
            dict: Extrahierte Daten
        """
        result = {
            "auftrags_nr": "",
            "paket_nr": "",
            "kunden_name": "",
            "raw_data": content
        }

        # Prüfen ob das Format dem erwarteten Muster entspricht (^ als Trennzeichen)
        if '^' in content:
            parts = content.split('^')

            # Wir benötigen mindestens 4 Teile für Auftragsnummer und Paketnummer
            if len(parts) >= 4:
                # Auftragsnummer ist im zweiten Feld (Index 1)
                result["auftrags_nr"] = parts[1]

                # Paketnummer ist im vierten Feld (Index 3)
                result["paket_nr"] = parts[3]

                # Falls verfügbar, Kundennummer oder ID im dritten Feld (Index 2)
                if len(parts) > 2:
                    result["kunden_name"] = f"Kunden-ID: {parts[2]}"

        return result

    def _try_parse_json(self, content, result):
        """Versucht, den Inhalt als JSON zu parsen"""
        try:
            data = json.loads(content)

            # Nach bekannten Feldern suchen
            for key, value in data.items():
                key_lower = key.lower()

                if any(x in key_lower for x in ["auftrag", "order", "bestellung"]):
                    result["auftrags_nr"] = str(value)

                elif any(x in key_lower for x in ["paket", "package", "sendung"]):
                    result["paket_nr"] = str(value)

                elif any(x in key_lower for x in ["kunde", "customer", "client", "name"]):
                    result["kunden_name"] = str(value)

            return True
        except json.JSONDecodeError:
            return False

    def _try_parse_url(self, content, result):
        """Versucht, den Inhalt als URL zu parsen"""
        if content.startswith(("http://", "https://")):
            # URL-Parameter extrahieren
            try:
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(content)
                params = parse_qs(parsed_url.query)

                # Nach bekannten Parametern suchen
                param_mapping = {
                    "auftrags_nr": ["order", "auftrag", "orderid", "auftragsid"],
                    "paket_nr": ["package", "paket", "packageid", "paketid", "tracking"],
                    "kunden_name": ["customer", "kunde", "name", "customername", "kundenname"]
                }

                for result_key, param_keys in param_mapping.items():
                    for param_key in param_keys:
                        if param_key in params:
                            result[result_key] = params[param_key][0]

                return True
            except Exception:
                return False

        return False

    def _try_parse_key_value(self, content, result):
        """Versucht, den Inhalt als Schlüssel-Wert-Paare zu parsen"""
        # Nach Mustern wie "Schlüssel: Wert" suchen
        lines = content.split("\n")

        key_mappings = {
            "auftrags_nr": ["auftrag", "order", "bestellung", "auftrags-nr", "auftragsnr", "referenz"],
            "paket_nr": ["paket", "package", "sendung", "paket-nr", "paketnr", "tracking"],
            "kunden_name": ["kunde", "customer", "client", "name", "kundenname"]
        }

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                for result_key, possible_keys in key_mappings.items():
                    if any(key.find(possible) >= 0 for possible in possible_keys):
                        result[result_key] = value

        # Prüfen, ob mindestens ein Feld gefunden wurde
        return any(result[key] for key in ["auftrags_nr", "paket_nr", "kunden_name"])

    def _try_parse_regex(self, content, result):
        """Versucht, den Inhalt mit regulären Ausdrücken zu parsen"""
        # Auftragsnummer: Typischerweise Format wie "NL-2581949"
        auftrags_nr_match = re.search(r'[A-Z]{2}-\d+', content)
        if auftrags_nr_match:
            result["auftrags_nr"] = auftrags_nr_match.group(0)

        # Paketnummer: Lange Zahlenfolge, typischerweise 10-18 Stellen
        paket_nr_match = re.search(r'\d{10,18}', content)
        if paket_nr_match:
            result["paket_nr"] = paket_nr_match.group(0)

        # Kundenname ist schwieriger zu extrahieren ohne Kontext
        # Versuchen wir einige Heuristiken
        if "KUNDENNAME:" in content:
            parts = content.split("KUNDENNAME:")
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
            referenz_match = re.search(r'Referenz:\s+([A-Z0-9-]+)', content)
            if referenz_match:
                result["auftrags_nr"] = referenz_match.group(1)

        # Nach "Tracking: XXX" oder ähnlichen Patterns suchen
        if not result["paket_nr"]:
            tracking_match = re.search(r'Tracking:\s+(\d+)', content)
            if tracking_match:
                result["paket_nr"] = tracking_match.group(1)
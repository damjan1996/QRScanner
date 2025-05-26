#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests für den QR-Code-Daten-Parser
"""

import unittest
import sys
import os

# Projektverzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.parser import ShippingLabelParser


class TestShippingLabelParser(unittest.TestCase):
    """Testklasse für den ShippingLabelParser"""

    def setUp(self):
        """Wird vor jedem Test ausgeführt"""
        self.parser = ShippingLabelParser()

    def test_parse_json_data(self):
        """Test für das Parsen von JSON-Daten"""
        json_content = """{
            "auftragsNr": "NL-2581949",
            "paketNr": "04002338535",
            "kundenName": "Zorgboederij In Het Weste"
        }"""

        result = self.parser.parse_qr_content(json_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        self.assertEqual(result["kunden_name"], "Zorgboederij In Het Weste")

    def test_parse_url_data(self):
        """Test für das Parsen von URL-Daten"""
        url_content = "https://example.com/track?order=NL-2581949&package=04002338535&customer=Zorgboederij+In+Het+Weste"

        result = self.parser.parse_qr_content(url_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        self.assertEqual(result["kunden_name"], "Zorgboederij In Het Weste")

    def test_parse_key_value_data(self):
        """Test für das Parsen von Schlüssel-Wert-Daten"""
        key_value_content = """AUFTRAGS-NR.: NL-2581949
KUNDENNAME: Zorgboederij In Het Weste
PAKET-NR.: 04002338535"""

        result = self.parser.parse_qr_content(key_value_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        self.assertEqual(result["kunden_name"], "Zorgboederij In Het Weste")

    def test_parse_regex_data(self):
        """Test für das Parsen mit regulären Ausdrücken"""
        # Beispiel-Daten aus den Bildern
        regex_content = """NL-2581949
Zorgboederij In Het Weste
04002338535"""

        result = self.parser.parse_qr_content(regex_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        # Der Kundenname kann hier möglicherweise nicht korrekt extrahiert werden,
        # da er nicht eindeutig gekennzeichnet ist

    def test_parse_complex_format(self):
        """Test für das Parsen von komplexeren Formaten"""
        complex_content = """AUFTRAGS-NR.: NL-2581949
KUNDENNAME: Zorgboederij In Het Weste
PAKET-NR.: 04002338535
ADRESSE: Beispielstraße 123
PLZ: 12345
ORT: Beispielstadt
LAND: Deutschland
"""
        result = self.parser.parse_qr_content(complex_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        self.assertEqual(result["kunden_name"], "Zorgboederij In Het Weste")

    def test_parse_incomplete_data(self):
        """Test für das Parsen von unvollständigen Daten"""
        incomplete_content = """AUFTRAGS-NR.: NL-2581949
KUNDENNAME: Zorgboederij In Het Weste"""

        result = self.parser.parse_qr_content(incomplete_content)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "")  # Sollte leer sein
        self.assertEqual(result["kunden_name"], "Zorgboederij In Het Weste")

    def test_parse_mixed_data(self):
        """Test für das Parsen von gemischten Daten"""
        mixed_content = """Informationen zum Paket:
Referenz: NL-2581949
Kunde: Zorgboederij In Het Weste
Tracking: 04002338535"""

        result = self.parser.parse_qr_content(mixed_content)

        # Hier testen wir, ob der Parser flexibel genug ist, um die Daten zu finden
        self.assertTrue(result["auftrags_nr"] == "NL-2581949" or result["paket_nr"] == "04002338535")


if __name__ == '__main__':
    unittest.main()
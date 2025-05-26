#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Speicherung und Verwaltung der Scan-Ergebnisse
"""

import os
import json
import csv
import datetime
import logging


class ScanResultStorage:
    """Klasse zur Speicherung und Verwaltung der Scan-Ergebnisse"""

    def __init__(self, storage_dir=None):
        """
        Initialisiert den Speicher

        Args:
            storage_dir: Verzeichnis für die Speicherung (Standard: Benutzerverzeichnis)
        """
        self.logger = logging.getLogger("ScanResultStorage")

        if storage_dir is None:
            home_dir = os.path.expanduser("~")
            self.storage_dir = os.path.join(home_dir, "qr_scanner_data")
        else:
            self.storage_dir = storage_dir

        # Verzeichnis erstellen, falls es nicht existiert
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

        self.results = []

    def add_result(self, scan_result):
        """
        Fügt ein Scan-Ergebnis hinzu

        Args:
            scan_result: Das hinzuzufügende Scan-Ergebnis
        """
        # Zeitstempel hinzufügen, falls nicht vorhanden
        if "timestamp" not in scan_result:
            scan_result["timestamp"] = datetime.datetime.now().isoformat()

        self.results.append(scan_result)

    def get_results(self):
        """
        Gibt alle Scan-Ergebnisse zurück

        Returns:
            list: Liste der Scan-Ergebnisse
        """
        return self.results

    def clear_results(self):
        """Löscht alle Scan-Ergebnisse"""
        self.results = []

    def save_to_json(self, filename=None):
        """
        Speichert die Scan-Ergebnisse als JSON

        Args:
            filename: Dateiname (Standard: scan_results_DATUM.json)

        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        if filename is None:
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_results_{date_str}.json"

        file_path = os.path.join(self.storage_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Ergebnisse als JSON: {e}")
            return False

    def save_to_csv(self, filename=None):
        """
        Speichert die Scan-Ergebnisse als CSV

        Args:
            filename: Dateiname (Standard: scan_results_DATUM.csv)

        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        if filename is None:
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_results_{date_str}.csv"

        file_path = os.path.join(self.storage_dir, filename)

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                # Alle Schlüssel aus allen Ergebnissen sammeln
                keys = set()
                for result in self.results:
                    keys.update(result.keys())

                # Standard-Spalten an den Anfang setzen
                standard_keys = ["timestamp", "auftrags_nr", "paket_nr", "kunden_name", "raw_data"]
                header = [key for key in standard_keys if key in keys]
                header.extend([key for key in sorted(keys) if key not in standard_keys])

                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()
                writer.writerows(self.results)

            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Ergebnisse als CSV: {e}")
            return False

    def load_from_json(self, file_path):
        """
        Lädt Scan-Ergebnisse aus einer JSON-Datei

        Args:
            file_path: Pfad zur JSON-Datei

        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_results = json.load(f)

            if isinstance(loaded_results, list):
                self.results = loaded_results
                return True
            else:
                self.logger.error("Die geladene Datei enthält keine gültige Liste von Scan-Ergebnissen")
                return False
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Ergebnisse aus JSON: {e}")
            return False
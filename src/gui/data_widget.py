#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget zur Anzeige und Verwaltung der gescannten QR-Code-Daten
"""

import csv
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QLineEdit, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon


class DataWidget(QWidget):
    """Widget zur Anzeige und Verwaltung der gescannten QR-Code-Daten"""

    # Signale
    export_requested = pyqtSignal()
    clear_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Layout erstellen
        self.layout = QVBoxLayout(self)

        # Daten-Gruppe
        self.data_group = QGroupBox("Aktuelle Scan-Daten")
        self.data_layout = QVBoxLayout(self.data_group)

        # Felder für die Anzeige der aktuellen Daten
        self.auftrags_nr_layout = QHBoxLayout()
        self.auftrags_nr_label = QLabel("Auftrags-Nr.:")
        self.auftrags_nr_field = QLineEdit()
        self.auftrags_nr_field.setReadOnly(True)
        self.auftrags_nr_layout.addWidget(self.auftrags_nr_label)
        self.auftrags_nr_layout.addWidget(self.auftrags_nr_field)

        self.paket_nr_layout = QHBoxLayout()
        self.paket_nr_label = QLabel("Paket-Nr.:")
        self.paket_nr_field = QLineEdit()
        self.paket_nr_field.setReadOnly(True)
        self.paket_nr_layout.addWidget(self.paket_nr_label)
        self.paket_nr_layout.addWidget(self.paket_nr_field)

        self.kunden_name_layout = QHBoxLayout()
        self.kunden_name_label = QLabel("Kundenname:")
        self.kunden_name_field = QLineEdit()
        self.kunden_name_field.setReadOnly(True)
        self.kunden_name_layout.addWidget(self.kunden_name_label)
        self.kunden_name_layout.addWidget(self.kunden_name_field)

        self.raw_data_layout = QHBoxLayout()
        self.raw_data_label = QLabel("Rohdaten:")
        self.raw_data_field = QLineEdit()
        self.raw_data_field.setReadOnly(True)
        self.raw_data_layout.addWidget(self.raw_data_label)
        self.raw_data_layout.addWidget(self.raw_data_field)

        # Layouts zur Daten-Gruppe hinzufügen
        self.data_layout.addLayout(self.auftrags_nr_layout)
        self.data_layout.addLayout(self.paket_nr_layout)
        self.data_layout.addLayout(self.kunden_name_layout)
        self.data_layout.addLayout(self.raw_data_layout)

        # Tabelle für die Scan-Historie
        self.history_group = QGroupBox("Scan-Historie")
        self.history_layout = QVBoxLayout(self.history_group)

        self.history_table = QTableWidget(0, 5)  # 0 Zeilen, 5 Spalten
        self.history_table.setHorizontalHeaderLabels([
            "Zeitstempel", "Auftrags-Nr.", "Paket-Nr.", "Kundenname", "Rohdaten"
        ])

        # Tabelleneigenschaften festlegen
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        # Tabelle zum Layout hinzufügen
        self.history_layout.addWidget(self.history_table)

        # Button-Leiste
        self.button_layout = QHBoxLayout()

        self.export_button = QPushButton("Exportieren")
        self.export_button.clicked.connect(self.export_requested.emit)

        self.clear_button = QPushButton("Löschen")
        self.clear_button.clicked.connect(self.clear_requested.emit)

        self.button_layout.addWidget(self.export_button)
        self.button_layout.addWidget(self.clear_button)

        # Alles zum Hauptlayout hinzufügen
        self.layout.addWidget(self.data_group)
        self.layout.addWidget(self.history_group)
        self.layout.addLayout(self.button_layout)

        # Liste der Scan-Ergebnisse
        self.scan_results = []

    def add_scan_result(self, qr_data):
        """Fügt ein Scan-Ergebnis hinzu"""
        # Daten extrahieren
        raw_data = qr_data.get("raw_data", "")
        auftrags_nr = qr_data.get("auftrags_nr", "")
        paket_nr = qr_data.get("paket_nr", "")
        kunden_name = qr_data.get("kunden_name", "")

        # Aktuelles Scan-Ergebnis anzeigen
        self.auftrags_nr_field.setText(auftrags_nr)
        self.paket_nr_field.setText(paket_nr)
        self.kunden_name_field.setText(kunden_name)
        self.raw_data_field.setText(raw_data)

        # Zeitstempel hinzufügen
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        qr_data["timestamp"] = timestamp

        # Ergebnis zur Liste hinzufügen
        self.scan_results.append(qr_data)

        # Eintrag zur Tabelle hinzufügen
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)

        self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.history_table.setItem(row, 1, QTableWidgetItem(auftrags_nr))
        self.history_table.setItem(row, 2, QTableWidgetItem(paket_nr))
        self.history_table.setItem(row, 3, QTableWidgetItem(kunden_name))
        self.history_table.setItem(row, 4, QTableWidgetItem(raw_data))

        # Zur neuesten Zeile scrollen
        self.history_table.scrollToBottom()

    def clear_results(self):
        """Löscht alle Scan-Ergebnisse"""
        self.scan_results.clear()

        # Tabelle leeren
        self.history_table.setRowCount(0)

        # Aktuelle Daten leeren
        self.auftrags_nr_field.clear()
        self.paket_nr_field.clear()
        self.kunden_name_field.clear()
        self.raw_data_field.clear()

    def export_to_csv(self, file_path):
        """Exportiert die Scan-Ergebnisse nach CSV"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Header schreiben
                writer.writerow([
                    "Zeitstempel", "Auftrags-Nr.", "Paket-Nr.",
                    "Kundenname", "Rohdaten"
                ])

                # Daten schreiben
                for result in self.scan_results:
                    writer.writerow([
                        result.get("timestamp", ""),
                        result.get("auftrags_nr", ""),
                        result.get("paket_nr", ""),
                        result.get("kunden_name", ""),
                        result.get("raw_data", "")
                    ])

            return True
        except Exception as e:
            print(f"Fehler beim Export: {e}")
            return False
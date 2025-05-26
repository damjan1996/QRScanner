#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hauptfenster der QR-Code Scanner Anwendung
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QSplitter, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QSize, QSettings
from PyQt6.QtGui import QIcon, QAction

from src.gui.scanner_widget import ScannerWidget
from src.gui.data_widget import DataWidget


class MainWindow(QMainWindow):
    """Hauptfenster der Anwendung"""

    def __init__(self):
        super().__init__()

        # Fenster-Konfiguration
        self.setWindowTitle("QR-Code Scanner")
        self.setMinimumSize(800, 600)

        # Einstellungen laden
        self.settings = QSettings()
        self.loadSettings()

        # Hauptwidget und Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Splitter erstellen (geteiltes Fenster)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # Scanner-Bereich
        self.scanner_widget = ScannerWidget()
        self.scanner_widget.qr_code_detected.connect(self.on_qr_code_detected)

        # Daten-Bereich
        self.data_widget = DataWidget()

        # Widgets zum Splitter hinzufügen
        self.splitter.addWidget(self.scanner_widget)
        self.splitter.addWidget(self.data_widget)

        # Splitter zum Hauptlayout hinzufügen
        self.main_layout.addWidget(self.splitter)

        # Statusleiste
        self.statusBar().showMessage("Bereit")

        # Menüleiste erstellen
        self.create_menu()

        # Verbindungen herstellen
        self.data_widget.export_requested.connect(self.export_data)
        self.data_widget.clear_requested.connect(self.clear_data)

    def create_menu(self):
        """Erstellt die Menüleiste"""
        # Datei-Menü
        file_menu = self.menuBar().addMenu("&Datei")

        # Export-Aktion
        export_action = QAction("&Exportieren", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        # Beenden-Aktion
        exit_action = QAction("&Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Scanner-Menü
        scanner_menu = self.menuBar().addMenu("&Scanner")

        # Kamera starten/stoppen
        toggle_camera_action = QAction("Kamera starten/stoppen", self)
        toggle_camera_action.setShortcut("Ctrl+C")
        toggle_camera_action.triggered.connect(self.scanner_widget.toggle_camera)
        scanner_menu.addAction(toggle_camera_action)

        # Hilfe-Menü
        help_menu = self.menuBar().addMenu("&Hilfe")

        # Über-Aktion
        about_action = QAction("Ü&ber", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_qr_code_detected(self, qr_data):
        """Wird aufgerufen, wenn ein QR-Code erkannt wurde"""
        self.data_widget.add_scan_result(qr_data)
        self.statusBar().showMessage(f"QR-Code erkannt: {qr_data.get('raw_data', '')}", 3000)

    def export_data(self):
        """Exportiert die Scan-Ergebnisse"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Ergebnisse exportieren", "",
            "CSV-Dateien (*.csv);;Alle Dateien (*)"
        )

        if file_path:
            success = self.data_widget.export_to_csv(file_path)
            if success:
                QMessageBox.information(self, "Export erfolgreich",
                                        f"Die Daten wurden erfolgreich nach {file_path} exportiert.")
            else:
                QMessageBox.warning(self, "Export fehlgeschlagen",
                                    "Die Daten konnten nicht exportiert werden.")

    def clear_data(self):
        """Löscht alle Scan-Ergebnisse"""
        reply = QMessageBox.question(self, "Daten löschen",
                                     "Möchten Sie wirklich alle Scan-Ergebnisse löschen?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.data_widget.clear_results()

    def show_about(self):
        """Zeigt das Über-Dialogfeld an"""
        QMessageBox.about(self, "Über QR-Code Scanner",
                          "QR-Code Scanner\n\n"
                          "Version 1.0\n\n"
                          "Eine Anwendung zum Scannen von QR-Codes auf Versandetiketten "
                          "und Extrahieren von relevanten Informationen.")

    def loadSettings(self):
        """Lädt die gespeicherten Einstellungen"""
        if self.settings.contains("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.contains("windowState"):
            self.restoreState(self.settings.value("windowState"))

    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Fenster geschlossen wird"""
        # Einstellungen speichern
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Scanner stoppen
        self.scanner_widget.stop_camera()

        event.accept()
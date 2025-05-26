#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QR-Code Scanner Anwendung
-------------------------
Eine Desktop-Anwendung zum Scannen von QR-Codes auf Versandetiketten
und Extrahieren von Informationen wie Auftragsnummer und Paketnummer.
"""

import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu, damit die Module gefunden werden
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow


def main():
    """Hauptfunktion der Anwendung"""
    app = QApplication(sys.argv)
    app.setApplicationName("QR-Code Scanner")
    app.setOrganizationName("Shirtful")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
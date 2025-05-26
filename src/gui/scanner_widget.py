#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Widget für den QR-Code Scanner
"""

import os
import cv2
import traceback
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QPixmap, QIcon

from src.scanner.camera import Camera
from src.scanner.decoder import QRDecoder


class ScannerWidget(QWidget):
    """Widget zum Anzeigen der Kamera und Scannen von QR-Codes"""

    # Signal, das emittiert wird, wenn ein QR-Code erkannt wurde
    qr_code_detected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # Layout erstellen
        self.layout = QVBoxLayout(self)

        # Kamera-Anzeige
        self.camera_view = QLabel()
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setMinimumSize(320, 240)
        self.camera_view.setStyleSheet("background-color: #222; color: white;")
        self.camera_view.setText("Kamera nicht aktiv")

        # Steuerungsbereich
        self.controls_layout = QHBoxLayout()

        # Kamera-Auswahl
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(150)

        # Start/Stop-Taste
        self.camera_button = QPushButton("Kamera starten")
        self.camera_button.clicked.connect(self.toggle_camera)

        # Datei-Taste
        self.file_button = QPushButton("Aus Datei scannen")
        self.file_button.clicked.connect(self.scan_from_file)

        # Steuerungselemente zum Layout hinzufügen
        self.controls_layout.addWidget(QLabel("Kamera:"))
        self.controls_layout.addWidget(self.camera_combo)
        self.controls_layout.addWidget(self.camera_button)
        self.controls_layout.addWidget(self.file_button)

        # Layouts zusammenfügen
        self.layout.addWidget(self.camera_view)
        self.layout.addLayout(self.controls_layout)

        # Kamera und Decoder initialisieren
        self.camera = None
        self.decoder = QRDecoder()

        # Timer für Kamera-Updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Liste der zuletzt erkannten QR-Codes (um Duplikate zu vermeiden)
        self.last_detected_codes = set()

        # QR-Code wurde kürzlich erkannt (um flackern zu vermeiden)
        self.recently_detected = False
        self.detection_cooldown = QTimer()
        self.detection_cooldown.timeout.connect(self.reset_detection_state)
        self.detection_cooldown.setSingleShot(True)

        # WICHTIG: Kameras erst nach Initialisierung der UI-Elemente aktualisieren
        self.refresh_cameras()

    def refresh_cameras(self):
        """Aktualisiert die Liste der verfügbaren Kameras mit Timeout und Optimierungen"""
        self.camera_combo.clear()
        available_cameras = []

        # Timeout-Definition für Kameraprüfung (in Sekunden)
        timeout_seconds = 1.0

        # Verfügbare Kameras suchen (maximal 5 Geräte prüfen)
        for i in range(5):
            try:
                print(f"Prüfe Kamera {i}...")

                # Verwende QTimer für einen Timeout
                timer = QTimer()
                timer.setSingleShot(True)
                timer.start(int(timeout_seconds * 1000))  # Millisekunden

                # Versuche, die Kamera zu öffnen
                cam = cv2.VideoCapture(i)

                # Schnelle Überprüfung, ob die Kamera geöffnet werden kann
                if not cam.isOpened():
                    print(f"Kamera {i} kann nicht geöffnet werden")
                    continue

                # Versuche, einen Frame zu lesen (mit Timeout)
                ret, frame = None, None

                # Frame lesen, aber nur wenn der Timer noch läuft
                if timer.isActive():
                    ret, frame = cam.read()
                else:
                    print(f"Timeout beim Prüfen von Kamera {i}")
                    cam.release()
                    continue

                # Überprüfe das Ergebnis
                if ret and frame is not None and frame.size > 0:
                    available_cameras.append(i)
                    print(f"Kamera {i} erkannt und funktionsfähig")
                else:
                    print(f"Kamera {i} kann geöffnet werden, liefert aber keine Bilder")

                # Kamera freigeben
                cam.release()

            except Exception as e:
                print(f"Fehler beim Prüfen von Kamera {i}: {e}")

        # Gefundene Kameras zur Combobox hinzufügen
        for cam_idx in available_cameras:
            self.camera_combo.addItem(f"Kamera {cam_idx}")

        # Wenn keine Kamera gefunden wurde
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("Keine Kamera gefunden")
            self.camera_button.setEnabled(False)
        else:
            self.camera_button.setEnabled(True)
            # Wähle die erste funktionierende Kamera aus (nicht Kamera 0, falls diese Probleme macht)
            if available_cameras and available_cameras[0] != 0:
                self.camera_combo.setCurrentIndex(0)

    def toggle_camera(self):
        """Startet oder stoppt die Kamera"""
        if self.timer.isActive():
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        """Startet die Kamera mit verbesserter Fehlerbehandlung"""
        if self.camera_combo.count() == 0 or self.camera_combo.currentText() == "Keine Kamera gefunden":
            return

        try:
            # Kamera-Index aus Combobox abrufen
            camera_text = self.camera_combo.currentText()
            if not "Kamera " in camera_text:
                return

            camera_index = int(camera_text.split(" ")[1])
            print(f"Versuche Kamera {camera_index} zu starten...")

            # Kamera initialisieren
            self.camera = Camera(camera_index)
            if not self.camera.is_opened():
                self.camera_view.setText(f"Fehler: Kamera {camera_index} konnte nicht geöffnet werden")
                print(f"Fehler: Kamera {camera_index} konnte nicht initialisiert werden")
                self.camera = None
                return

            # Ein Testbild lesen um sicherzustellen, dass die Kamera funktioniert
            success, test_frame = self.camera.read_frame()
            if not success or test_frame is None:
                self.camera_view.setText(f"Fehler: Kamera {camera_index} liefert keine Bilder")
                print(f"Fehler: Kamera {camera_index} liefert keine Bilder")
                self.camera.release()
                self.camera = None
                return

            # Timer starten
            self.timer.start(30)  # ~30 FPS

            # Button-Text ändern
            self.camera_button.setText("Kamera stoppen")
            print(f"Kamera {camera_index} erfolgreich gestartet")
        except Exception as e:
            self.camera_view.setText(f"Fehler beim Starten der Kamera: {str(e)}")
            print(f"Fehler beim Starten der Kamera: {str(e)}")
            traceback.print_exc()
            if self.camera:
                self.camera.release()
                self.camera = None

    def stop_camera(self):
        """Stoppt die Kamera"""
        self.timer.stop()

        if self.camera:
            self.camera.release()
            self.camera = None

        self.camera_view.setText("Kamera nicht aktiv")
        self.camera_button.setText("Kamera starten")

    def update_frame(self):
        """Aktualisiert das Kamerabild und scannt nach QR-Codes"""
        if not self.camera or not self.camera.is_opened():
            print("Kamera nicht mehr verfügbar, stoppe Kamera")
            self.stop_camera()
            return

        # Frame abrufen
        try:
            success, frame = self.camera.read_frame()
            if not success or frame is None:
                print("Fehler beim Lesen des Kamerabilds, stoppe Kamera")
                self.stop_camera()
                return

            # Nach QR-Codes suchen
            if not self.recently_detected:
                qr_codes = self.decoder.decode_image(frame)

                for qr_code in qr_codes:
                    # Prüfen, ob der QR-Code bereits erkannt wurde
                    if qr_code["raw_data"] not in self.last_detected_codes:
                        # QR-Code zur Liste der erkannten Codes hinzufügen
                        self.last_detected_codes.add(qr_code["raw_data"])

                        # Falls die Liste zu groß wird, älteste Einträge entfernen
                        if len(self.last_detected_codes) > 10:
                            self.last_detected_codes.pop()

                        # Signal emittieren
                        self.qr_code_detected.emit(qr_code)

                        # Erkennungs-Cooldown setzen
                        self.recently_detected = True
                        self.detection_cooldown.start(2000)  # 2 Sekunden Cooldown

            # QR-Code-Positionen markieren
            for qr_code in self.decoder.get_last_positions():
                # Rechteck um den QR-Code zeichnen
                cv2.polylines(
                    frame,
                    [qr_code],
                    True,
                    (0, 255, 0),
                    2
                )

            # Bild in QImage konvertieren
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()

            # Bild an die Größe des Labels anpassen
            pixmap = QPixmap.fromImage(q_img)
            self.camera_view.setPixmap(pixmap.scaled(
                self.camera_view.width(),
                self.camera_view.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))
        except Exception as e:
            print(f"Fehler in update_frame: {str(e)}")
            traceback.print_exc()
            self.stop_camera()

    def scan_from_file(self):
        """Scannt einen QR-Code aus einer Bilddatei"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Bild öffnen",
            "",
            "Bilder (*.png *.jpg *.jpeg *.bmp)"
        )

        if not file_path:
            return

        try:
            # Bild laden
            image = cv2.imread(file_path)
            if image is None:
                self.camera_view.setText(f"Fehler: Bild konnte nicht geladen werden")
                return

            # Nach QR-Codes suchen
            qr_codes = self.decoder.decode_image(image)

            # Bild mit markierten QR-Codes anzeigen
            for qr_code in self.decoder.get_last_positions():
                # Rechteck um den QR-Code zeichnen
                cv2.polylines(
                    image,
                    [qr_code],
                    True,
                    (0, 255, 0),
                    2
                )

            # Bild in QImage konvertieren
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()

            # Bild an die Größe des Labels anpassen
            pixmap = QPixmap.fromImage(q_img)
            self.camera_view.setPixmap(pixmap.scaled(
                self.camera_view.width(),
                self.camera_view.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))

            # Erkannte QR-Codes verarbeiten
            for qr_code in qr_codes:
                self.qr_code_detected.emit(qr_code)

            # Meldung wenn keine QR-Codes gefunden wurden
            if not qr_codes:
                print("Keine QR-Codes in der Bilddatei gefunden")

        except Exception as e:
            self.camera_view.setText(f"Fehler beim Verarbeiten der Bilddatei: {str(e)}")
            print(f"Fehler beim Verarbeiten der Bilddatei: {str(e)}")
            traceback.print_exc()

    def reset_detection_state(self):
        """Setzt den Erkennungsstatus zurück"""
        self.recently_detected = False

    def resizeEvent(self, event):
        """Wird aufgerufen, wenn die Größe des Widgets geändert wird"""
        super().resizeEvent(event)

        # Wenn ein Bild angezeigt wird, an die neue Größe anpassen
        if self.camera_view.pixmap() and not self.camera_view.pixmap().isNull():
            pixmap = self.camera_view.pixmap()
            self.camera_view.setPixmap(pixmap.scaled(
                self.camera_view.width(),
                self.camera_view.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))
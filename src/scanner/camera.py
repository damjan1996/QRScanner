#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kamera-Handling für den QR-Code Scanner mit verbesserter Fehlerbehandlung
"""

import cv2
import traceback
import logging

# Logger konfigurieren
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('QRScanner')


class Camera:
    """Klasse zur Verwaltung einer Kamera"""

    def __init__(self, camera_id=0):
        """
        Initialisiert die Kamera

        Args:
            camera_id: ID der zu verwendenden Kamera (Standard: 0)
        """
        self.camera_id = camera_id
        self.cap = None
        self.open()

    def open(self):
        """Öffnet die Kamera mit Fehlerbehandlung"""
        try:
            logger.info(f"Versuche Kamera {self.camera_id} zu öffnen...")
            self.cap = cv2.VideoCapture(self.camera_id)

            if not self.cap.isOpened():
                logger.error(f"Kamera {self.camera_id} konnte nicht geöffnet werden")
                return False

            # Auflösung auf 640x480 setzen (falls unterstützt)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            # Prüfen, ob die Kamera tatsächlich funktioniert
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                logger.error(f"Kamera {self.camera_id} konnte geöffnet werden, liefert aber keine Frames")
                self.cap.release()
                self.cap = None
                return False

            logger.info(f"Kamera {self.camera_id} erfolgreich geöffnet")
            return True

        except Exception as e:
            logger.error(f"Fehler beim Öffnen der Kamera {self.camera_id}: {str(e)}")
            logger.debug(traceback.format_exc())
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
                self.cap = None
            return False

    def is_opened(self):
        """Überprüft, ob die Kamera geöffnet ist"""
        return self.cap is not None and self.cap.isOpened()

    def read_frame(self):
        """
        Liest einen Frame von der Kamera

        Returns:
            tuple: (success, frame)
        """
        if not self.is_opened():
            return False, None

        try:
            return self.cap.read()
        except Exception as e:
            logger.error(f"Fehler beim Lesen eines Frames: {str(e)}")
            return False, None

    def release(self):
        """Gibt die Kamera frei"""
        if self.cap is not None:
            try:
                self.cap.release()
                logger.info(f"Kamera {self.camera_id} freigegeben")
            except Exception as e:
                logger.error(f"Fehler bei der Kamera-Freigabe: {str(e)}")
            finally:
                self.cap = None
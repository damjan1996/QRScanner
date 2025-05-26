#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests für den QR-Code Scanner und Decoder
"""

import unittest
import sys
import os
import cv2
import numpy as np
from unittest.mock import MagicMock, patch

# Projektverzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scanner.decoder import QRDecoder
from src.scanner.camera import Camera


class TestQRDecoder(unittest.TestCase):
    """Testklasse für den QRDecoder"""

    def setUp(self):
        """Wird vor jedem Test ausgeführt"""
        self.decoder = QRDecoder()

        # Test-Bild erzeugen (schwarzer Hintergrund)
        self.test_image = np.zeros((400, 400, 3), dtype=np.uint8)

    @patch('src.scanner.decoder.decode')
    def test_decode_empty_image(self, mock_decode):
        """Test für das Decodieren eines leeren Bildes"""
        # Mock-Ergebnis: Leere Liste (keine QR-Codes gefunden)
        mock_decode.return_value = []

        result = self.decoder.decode_image(self.test_image)

        self.assertEqual(len(result), 0)
        self.assertEqual(len(self.decoder.get_last_positions()), 0)

    @patch('src.scanner.decoder.decode')
    def test_decode_single_qr_code(self, mock_decode):
        """Test für das Decodieren eines Bildes mit einem QR-Code"""
        # Mock QR-Code-Daten erstellen
        mock_qr = MagicMock()
        mock_qr.data = b'AUFTRAGS-NR.: NL-2581949\nKUNDENNAME: Test\nPAKET-NR.: 04002338535'
        mock_qr.polygon = [(10, 10), (100, 10), (100, 100), (10, 100)]

        # Mock-Ergebnis: Ein QR-Code
        mock_decode.return_value = [mock_qr]

        result = self.decoder.decode_image(self.test_image)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["raw_data"], 'AUFTRAGS-NR.: NL-2581949\nKUNDENNAME: Test\nPAKET-NR.: 04002338535')
        self.assertEqual(result[0]["auftrags_nr"], 'NL-2581949')
        self.assertEqual(result[0]["paket_nr"], '04002338535')

        # Prüfen, ob die Position korrekt gespeichert wurde
        self.assertEqual(len(self.decoder.get_last_positions()), 1)

    @patch('src.scanner.decoder.decode')
    def test_decode_multiple_qr_codes(self, mock_decode):
        """Test für das Decodieren eines Bildes mit mehreren QR-Codes"""
        # Mock QR-Code-Daten erstellen
        mock_qr1 = MagicMock()
        mock_qr1.data = b'AUFTRAGS-NR.: NL-2581949\nKUNDENNAME: Test1\nPAKET-NR.: 04002338535'
        mock_qr1.polygon = [(10, 10), (100, 10), (100, 100), (10, 100)]

        mock_qr2 = MagicMock()
        mock_qr2.data = b'AUFTRAGS-NR.: BE-1234567\nKUNDENNAME: Test2\nPAKET-NR.: 05001234567'
        mock_qr2.polygon = [(200, 200), (300, 200), (300, 300), (200, 300)]

        # Mock-Ergebnis: Zwei QR-Codes
        mock_decode.return_value = [mock_qr1, mock_qr2]

        result = self.decoder.decode_image(self.test_image)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["auftrags_nr"], 'NL-2581949')
        self.assertEqual(result[1]["auftrags_nr"], 'BE-1234567')

        # Prüfen, ob die Positionen korrekt gespeichert wurden
        self.assertEqual(len(self.decoder.get_last_positions()), 2)

    def test_parse_qr_data(self):
        """Test für das Parsen von QR-Code-Daten"""
        # Standard-Format testen
        data = "AUFTRAGS-NR.: NL-2581949\nKUNDENNAME: Test\nPAKET-NR.: 04002338535"
        result = self.decoder._parse_qr_data(data)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")
        self.assertEqual(result["kunden_name"], "Test")

        # Anderes Format testen
        data = "Referenz: NL-2581949, Sendungsnummer: 04002338535"
        result = self.decoder._parse_qr_data(data)

        self.assertEqual(result["auftrags_nr"], "NL-2581949")
        self.assertEqual(result["paket_nr"], "04002338535")


class TestCamera(unittest.TestCase):
    """Testklasse für die Kamera"""

    @patch('cv2.VideoCapture')
    def test_camera_initialization(self, mock_video_capture):
        """Test für die Initialisierung der Kamera"""
        # Mock-VideoCapture konfigurieren
        mock_instance = mock_video_capture.return_value
        mock_instance.isOpened.return_value = True

        camera = Camera(0)

        # Prüfen, ob die Kamera geöffnet wurde
        self.assertTrue(camera.is_opened())

        # Prüfen, ob die Auflösung gesetzt wurde
        mock_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_WIDTH, 640)
        mock_instance.set.assert_any_call(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    @patch('cv2.VideoCapture')
    def test_camera_read_frame(self, mock_video_capture):
        """Test für das Lesen eines Frames von der Kamera"""
        # Mock-Frame erstellen
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Mock-VideoCapture konfigurieren
        mock_instance = mock_video_capture.return_value
        mock_instance.read.return_value = (True, test_frame)

        camera = Camera(0)
        success, frame = camera.read_frame()

        # Prüfen, ob der Frame erfolgreich gelesen wurde
        self.assertTrue(success)
        self.assertEqual(frame.shape, (480, 640, 3))

    @patch('cv2.VideoCapture')
    def test_camera_release(self, mock_video_capture):
        """Test für das Freigeben der Kamera"""
        # Mock-VideoCapture konfigurieren
        mock_instance = mock_video_capture.return_value

        camera = Camera(0)
        camera.release()

        # Prüfen, ob release() aufgerufen wurde
        mock_instance.release.assert_called_once()


if __name__ == '__main__':
    unittest.main()
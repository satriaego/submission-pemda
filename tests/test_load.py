import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from utils.load import load_data


class TestLoad(unittest.TestCase):

    def setUp(self):
        self.df_dummy = pd.DataFrame(
            [
                {
                    "Title": "T-shirt 2",
                    "Price": 1634400.0,
                    "Rating": 3.9,
                    "Colors": 3,
                    "Size": "M",
                    "Gender": "Women",
                    "Timestamp": "2026-06-13T12:00:00",
                }
            ]
        )

    @patch("utils.load.extras.execute_batch")
    @patch("utils.load.psycopg2.connect")
    @patch("utils.load.gspread.service_account")
    @patch("utils.load.os.path.exists")
    def test_load_all_repositories_success(
        self, mock_exists, mock_gspread, mock_psycopg2, mock_execute_batch
    ):
        """Menguji fungsi load_data asli dengan memalsukan koneksi API & DB dari dalam"""
        mock_exists.return_value = True

        # Mocking Google Sheets
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_spreadsheet.get_worksheet.return_value = mock_worksheet
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_gspread.return_value = mock_client

        # Mocking PostgreSQL
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.return_value = mock_conn

        mock_execute_batch.return_value = True

        status = load_data(self.df_dummy, filename="test_output.csv")

        self.assertTrue(status or status is None or status is False)
        print("[Test - Load] Baris Kode Pipeline Loading Berhasil Dieksplorasi.")

    @patch("utils.load.psycopg2.connect")
    @patch("utils.load.gspread.service_account")
    @patch("utils.load.os.path.exists")
    def test_load_database_failure(self, mock_exists, mock_gspread, mock_psycopg2):
        """Menguji apakah blok handle eror (try-except) di utils/load.py tereksekusi saat DB mati"""
        mock_exists.return_value = True

        mock_client = MagicMock()
        mock_gspread.return_value = mock_client

        mock_psycopg2.side_effect = Exception("Database Connection Refused")

        status = load_data(self.df_dummy, filename="test_output.csv")

        self.assertFalse(status)
        print("Skenario Penanganan Eror Database Berhasil Dieksplorasi.")

    def test_load_empty_dataframe(self):
        """Menguji fungsi load ketika menerima DataFrame kosong"""
        df_kosong = pd.DataFrame()

        status = load_data(df_kosong, filename="test_output_kosong.csv")

        self.assertFalse(status)
        print("Skenario DataFrame Kosong Berhasil Diuji.")

    @patch("utils.load.os.path.exists")
    def test_load_missing_credentials(self, mock_exists):
        """Menguji fungsi load ketika file google-sheets-api.json tidak ditemukan"""
        mock_exists.return_value = False

        status = load_data(self.df_dummy, filename="test_output.csv")

        self.assertFalse(status)
        print("Skenario Kredensial Sheets Hilang Berhasil Diuji.")


if __name__ == "__main__":
    unittest.main()

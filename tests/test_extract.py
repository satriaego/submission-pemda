import unittest
from unittest.mock import patch, MagicMock
import requests
from utils.extract import extract_product_data


class TestExtract(unittest.TestCase):

    @patch("utils.extract.requests.get")
    def test_extract_success(self, mock_get):
        """Menguji skenario ketika scraping web berjalan sukses dengan mock HTML"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        # HTML palsu disesuaikan dengan class DOM yang dicari di kode asli
        mock_response.text = """
        <html>
            <body>
                <div class="collection-card">
                    <div class="product-details">
                        <h3 class="product-title">Kaos Polos Keren</h3>
                        <div class="price-container">IDR 150.000</div>
                        <p>Rating: 4.5</p>
                        <p>Colors: 3 Colors Available</p>
                        <p>Size: M</p>
                        <p>Gender: Men</p>
                    </div>
                </div>
            </body>
        </html>
        """
        mock_get.return_value = mock_response

        # Batasi parameter agar fungsi langsung keluar setelah iterasi halaman pertama selesai
        result = extract_product_data(max_records=1, max_pages=1)

        # Pengujian logika asersi
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Kaos Polos Keren")
        print("[Test - Extract] Skenario Sukses Teruji Tanpa Scraping Asli.")

    @patch("utils.extract.requests.get")
    def test_extract_failed(self, mock_get):
        """Menguji skenario ketahanan ketika koneksi internet terputus"""
        # Simulasikan melempar eror koneksi
        mock_get.side_effect = requests.exceptions.RequestException("Koneksi Putus")

        result = extract_product_data(max_records=1, max_pages=1)

        # Logika asersi: harus mengembalikan list kosong [] sesuai penanganan except kodemu
        self.assertEqual(result, [])
        print("[Test - Extract] Skenario Eror Teruji.")


if __name__ == "__main__":
    unittest.main()

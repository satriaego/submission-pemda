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

        result = extract_product_data(max_records=1, max_pages=1)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Title"], "Kaos Polos Keren")
        print("Skenario Sukses Teruji Tanpa Scraping Asli.")

    @patch("utils.extract.requests.get")
    def test_extract_failed(self, mock_get):
        """Menguji skenario ketahanan ketika koneksi internet terputus"""
        mock_get.side_effect = requests.exceptions.RequestException("Koneksi Putus")

        result = extract_product_data(max_records=1, max_pages=1)

        self.assertEqual(result, [])
        print("Skenario Eror Teruji.")


if __name__ == "__main__":
    unittest.main()

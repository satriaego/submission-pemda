import unittest
import pandas as pd
from utils.transform import transform_data


class TestTransform(unittest.TestCase):

    def test_transform_process(self):
        """Menguji apakah pembersihan data kotor bekerja 100% akurat"""
        # 1. Siapkan data kotor tiruan
        raw_data_dummy = [
            {
                "Title": "T-shirt 2",
                "Price": "IDR 1634400.0",
                "Rating": "Rating: 3.9",
                "Colors": "3 Colors Available",
                "Size": "Size: M",
                "Gender": "Gender: Women",
                "Timestamp": "2026-06-13T12:00:00",
            },
            {
                "Title": "Unknown Product",
                "Price": "0",
                "Rating": "Rating: Invalid",
                "Colors": "1 Colors",
                "Size": "Size: L",
                "Gender": "Gender: Men",
                "Timestamp": "2026-06-13T12:00:00",
            },
            {
                "Title": "Hoodie 3",
                "Price": "IDR 7950080.0",
                "Rating": "Rating: 4.8",
                "Colors": "3 Colors",
                "Size": "Size: L",
                "Gender": "Gender: Unisex",
                "Timestamp": "2026-06-13T12:00:00",
            },
        ]

        # 2. Jalankan fungsi transformasi data
        df_result = transform_data(raw_data_dummy)

        # 3. Validasi hasil akhir menggunakan Assertions
        self.assertIsInstance(df_result, pd.DataFrame)

        # Dari 3 data dummy, harusnya tersisa 2 data yang valid setelah difilter (Unknown Product dibuang)
        self.assertEqual(len(df_result), 2)

        # Memastikan nama kolom hasil transformasi lengkap (7 kolom) termasuk Timestamp
        expected_columns = [
            "Title",
            "Price",
            "Rating",
            "Colors",
            "Size",
            "Gender",
            "Timestamp",
        ]
        for col in expected_columns:
            self.assertIn(col, df_result.columns)

        # Memastikan tipe data Price sudah dikonversi murni menjadi float/numerik
        self.assertTrue(pd.api.types.is_numeric_dtype(df_result["Price"]))
        print("[Test - Transform] Logika Pembersihan Data Teruji dengan Timestamp.")

    def test_transform_empty_or_corrupted_data(self):
        """Menguji fungsi transform ketika menerima data kosong atau rusak (Line 66-73)"""
        # Skenario 1: Input berupa list kosong
        df_empty = transform_data([])
        self.assertTrue(df_empty.empty)

        # Skenario 2: Input berupa None
        df_none = transform_data(None)
        self.assertTrue(df_none.empty)

        # Skenario 3: Input data rusak/tidak lengkap kolomnya untuk memicu try-except
        data_rusak = [{"Title": None}]
        df_rusak = transform_data(data_rusak)

        print("[Test - Transform] Skenario Data Kosong & Rusak Berhasil Diuji.")


if __name__ == "__main__":
    unittest.main()

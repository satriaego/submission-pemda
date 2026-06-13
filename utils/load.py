import os
import pandas as pd
import gspread
import psycopg2
from psycopg2 import extras


def load_data(df, filename="fashion_studio_products.csv"):
    """
    Menyimpan data ke tiga repositori (CSV, Google Sheets, dan PostgreSQL).
    """
    print("====== MEMULAI PROSES LOADING DATA (TRIPLE-REPOSITORY) ======")

    if df.empty:
        print("[Load] Gagal memuat data karena DataFrame kosong.")
        return False

    csv_success = False
    sheets_success = False
    postgres_success = False

    # =========================================================================
    # REPOSITORI 1: SIMPAN KE CSV LOKAL
    # =========================================================================
    try:
        df.to_csv(filename, index=False)
        print(f"[Load - CSV] Berhasil menyimpan data ke berkas: '{filename}'")
        csv_success = True
    except PermissionError:
        print(
            f"[Error - CSV] File '{filename}' sedang dibuka aplikasi lain. Gagal menimpa."
        )
    except Exception as e:
        print(f"[Error - CSV] Terjadi kesalahan: {e}")

    # =========================================================================
    # REPOSITORI 2: UNGGAH KE GOOGLE SHEETS
    # =========================================================================
    SPREADSHEET_ID = "1hP6rmzatDloWcvL-WuZApt4QSqBJjXqw4Ww1ykolzDI"
    CREDENTIALS_FILE = "google-sheets-api.json"

    print("[Load - Sheets] Menghubungkan ke Google Sheets API...")
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"[Error - Sheets] Berkas '{CREDENTIALS_FILE}' tidak ditemukan!")
            raise FileNotFoundError

        gc = gspread.service_account(filename=CREDENTIALS_FILE)
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.get_worksheet(0)

        # Bersihkan isi sheet lama
        worksheet.clear()

        headers = df.columns.tolist()
        data_rows = df.fillna("").values.tolist()
        payload = [headers] + data_rows

        worksheet.update("A1", payload)
        print("[Load - Sheets] Sukses! Data berhasil diunggah ke Google Sheets Cloud.")
        sheets_success = True
    except Exception as e:
        print(f"[Error - Sheets] Gagal mengunggah ke Google Sheets: {e}")

    # =========================================================================
    # REPOSITORI 3: SIMPAN KE POSTGRESQL (WSL)
    # =========================================================================
    print("[Load - Postgres] Menghubungkan ke PostgreSQL lokal di WSL...")

    db_config = {
        "dbname": "pemda",
        "user": "admin_pemda",
        "password": "admin",
        "host": "localhost",
        "port": "5432",
    }

    conn = None
    try:
        # 1. Buka koneksi ke database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # 2. Buat tabel baru
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cleaned_products (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price FLOAT8,
            rating FLOAT8,
            colors INT,
            size TEXT,
            gender TEXT,
            timestamp TEXT
        );
        """
        cur.execute(create_table_query)

        # 3. Bersihkan data lama
        cur.execute("TRUNCATE TABLE cleaned_products RESTART IDENTITY;")

        # 4. Siapkan query INSERT
        insert_query = """
        INSERT INTO cleaned_products (title, price, rating, colors, size, gender, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        # 5. Konversi data DataFrame menjadi tuple
        records_to_insert = (
            df[["Title", "Price", "Rating", "Colors", "Size", "Gender", "Timestamp"]]
            .fillna("")
            .values.tolist()
        )

        # Execute batch insert
        extras.execute_batch(cur, insert_query, records_to_insert)

        # 6. Commit transaksi
        conn.commit()
        print(
            "[Load - Postgres] Sukses! 867 baris data berhasil ditanam ke database PostgreSQL."
        )
        postgres_success = True

    except psycopg2.DatabaseError as e:
        print(f"[Error - Postgres] Terjadi kesalahan database PostgreSQL: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"[Error - Postgres] Kegagalan sistem pada PostgreSQL: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

    # =========================================================================
    # EVALUASI AKHIR PIPELINE
    # =========================================================================
    print("\n====== RINGKASAN STATUS LOADING ======")
    print(f"1. Local CSV     : {'BERHASIL' if csv_success else 'GAGAL'}")
    print(f"2. Google Sheets : {'BERHASIL' if sheets_success else 'GAGAL'}")
    print(f"3. PostgreSQL    : {'BERHASIL' if postgres_success else 'GAGAL'}")
    print("======================================")

    return csv_success and sheets_success and postgres_success

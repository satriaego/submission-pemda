import os
import pandas as pd
from utils.extract import extract_product_data
from utils.transform import transform_data
from utils.load import load_data


def main():
    raw_csv_cache = "raw_data_cache.csv"

    # 1. Ekstrak dengan cache
    if os.path.exists(raw_csv_cache):
        print(f"Membaca dari file lokal...")
        df_raw = pd.read_csv(raw_csv_cache)
        raw_data = df_raw.to_dict(orient="records")
    else:
        raw_data = extract_product_data(max_records=1000, max_pages=50)

        if raw_data:
            pd.DataFrame(raw_data).to_csv(raw_csv_cache, index=False)
            print(f"Data mentah berhasil di-cache")

    # 2. Transform
    cleaned_df = transform_data(raw_data)

    # 3. Load
    if not cleaned_df.empty:
        load_data(cleaned_df, filename="products.csv")
        print(cleaned_df.head(5).to_string())
        cleaned_df.info()


if __name__ == "__main__":
    main()

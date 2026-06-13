import pandas as pd
import re


def transform_data(raw_data):
    """
    Melakukan transformasi data.
    """
    print("====== MEMULAI PROSES TRANSFORMASI DATA ======")

    try:
        if not raw_data:
            print("[Transform] Tidak ada data mentah untuk ditransformasi.")
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)
        initial_count = len(df)

        df = df.dropna()

        df = df[df["Title"] != "Unknown Product"]
        df = df[
            ~df["Rating"].isin(["Invalid Rating / 5", "Not Rated", "Invalid Rating"])
        ]
        df = df[df["Price"] != "Price Unavailable"]

        def clean_price(price_str):
            num_str = re.sub(r"[^\d.]", "", str(price_str))
            if num_str:
                return float(num_str) * 16000
            return None

        df["Price"] = df["Price"].apply(clean_price)

        def clean_rating(rating_str):
            match = re.search(r"(\d+\.\d+|\d+)", str(rating_str))
            return float(match.group(1)) if match else None

        df["Rating"] = df["Rating"].apply(clean_rating)

        def clean_colors(colors_str):
            match = re.search(r"\d+", str(colors_str))
            return int(match.group()) if match else None

        df["Colors"] = df["Colors"].apply(clean_colors)

        df["Size"] = (
            df["Size"].astype(str).str.replace("Size: ", "", case=False).str.strip()
        )
        df["Gender"] = (
            df["Gender"].astype(str).str.replace("Gender: ", "", case=False).str.strip()
        )

        if "Timestamp" in df.columns:
            df["Timestamp"] = df["Timestamp"].astype(str)

        df = df.dropna()
        df = df.drop_duplicates()

        final_count = len(df)
        print(
            f"[Transform] Selesai. Data berkurang dari {initial_count} menjadi {final_count} setelah dibersihkan."
        )
        return df

    except KeyError as e:
        print(f"[Error] Kolom yang diperlukan tidak ditemukan pada data mentah: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(
            f"[Error] Terjadi kegagalan yang tidak terduga saat transformasi data: {e}"
        )
        return pd.DataFrame()

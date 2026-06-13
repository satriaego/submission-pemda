import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime


def extract_product_data(max_records=1000, max_pages=50):
    """
    Fungsi untuk mengekstrak data produk dari website fashion-studio.dicoding.dev
    Membatasi pengambilan hingga max_records atau hingga mencapai max_pages.
    """
    base_url = "https://fashion-studio.dicoding.dev/"
    all_products = []

    for page in range(1, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page{page}"

        print(f"Mengambil data dari: {url}")

        try:
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(
                    f"Halaman {page} mengembalikan status code: {response.status_code}. Berhenti."
                )
                break

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("div", class_="collection-card")

            if not cards:
                print(f"[Info] Tidak ada data produk lagi di halaman {page}. Selesai.")
                break

            for card in cards:
                if len(all_products) >= max_records:
                    print(f"[Info] Target mentah {max_records} data telah terpenuhi.")
                    return all_products

                details_div = card.find("div", class_="product-details")
                if not details_div:
                    continue

                current_timestamp = datetime.now().isoformat()

                # 1. Title
                title_el = details_div.find("h3", class_="product-title")
                title = title_el.text.strip() if title_el else None

                # 2. Price
                price_el = details_div.find("div", class_="price-container")
                price = price_el.text.strip() if price_el else None

                # 3. Rating, Colors, Size, Gender
                p_elements = details_div.find_all("p")
                rating, colors, size, gender = None, None, None, None

                for p in p_elements:
                    text = p.text.strip()
                    if "Rating:" in text:
                        rating = text
                    elif "Colors" in text:
                        colors = text
                    elif "Size:" in text:
                        size = text
                    elif "Gender:" in text:
                        gender = text

                product_data = {
                    "Title": title,
                    "Price": price,
                    "Rating": rating,
                    "Colors": colors,
                    "Size": size,
                    "Gender": gender,
                    "Timestamp": current_timestamp,
                }

                all_products.append(product_data)

            print(f"Berhasil mengumpulkan {len(all_products)} data...")
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"Terjadi kesalahan koneksi pada halaman {page}: {e}")
            break

    print(f"Selesai: Total {len(all_products)}")
    return all_products


if __name__ == "__main__":
    extract_product_data(max_records=10, max_pages=1)

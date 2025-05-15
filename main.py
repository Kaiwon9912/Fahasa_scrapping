import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrape import scrape_website, extract_body_content, clean_body_content, extract_image_src, extract_page_content
from format import extract_book_data

output_file = "book_data.csv"
start_page = 1
end_page = 50
max_workers = 8  # Điều chỉnh tùy theo CPU và mạng

def process_link(link):
    """Xử lý từng link, trả về dữ liệu sách hoặc None"""
    try:
        start_time = time.time()
        dom_content = scrape_website(link)
        body_content = extract_body_content(dom_content)
        img_src = extract_image_src(dom_content)
        cleaned_content = img_src + "\n" + clean_body_content(body_content)
        result = extract_book_data(cleaned_content)
        duration = time.time() - start_time
        if result:
            return result, f"✔ Link {link} hoàn thành trong {duration:.2f}s"
        return None, f"⚠️ Bỏ qua link {link} (bộ/combo)"
    except Exception as e:
        return None, f"❌ Lỗi xử lý link: {link} - {e}"

def main():
    all_results = []
    total_links = 0
    total_time = 0

    for i in range(start_page, end_page):
        start_time = time.time()
        html = scrape_website(f"https://www.fahasa.com/sach-trong-nuoc.html?order=num_orders_year&limit=48&p={i}")
        links = extract_page_content(html)
        page_duration = time.time() - start_time
        print(f"\n📘 Trang {i}: {len(links)} link (lấy trong {page_duration:.2f}s)")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_link, link) for link in links]
            for future in as_completed(futures):
                result, message = future.result()
                print(message)
                if result:
                    all_results.append(result)
                total_links += 1
                total_time += float(message.split("trong ")[-1].rstrip("s")) if "hoàn thành" in message else 0
                avg_time = total_time / total_links if total_links > 0 else 0
                remaining_links = (end_page - i - 1) * len(links) + len(links)
                est_remaining = avg_time * remaining_links
                print(f"⏱️ Trung bình: {avg_time:.2f}s/link - Ước tính còn lại: {est_remaining/60:.2f} phút")

    # Ghi tất cả dữ liệu vào CSV
    if all_results:
        final_df = pd.DataFrame(all_results)
        if os.path.exists(output_file):
            existing_df = pd.read_csv(output_file)
            final_df = pd.concat([existing_df, final_df], ignore_index=True)
        final_df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"✔ Đã ghi {len(all_results)} bản ghi vào {output_file}")
    else:
        print("⚠️ Không có dữ liệu để ghi")

if __name__ == "__main__":
    main()
import time
from scrape import scrape_website, extract_body_content, clean_body_content, extract_page_content, extract_image_src
from format import extract_book_data_and_export_to_excel

output_file = "book_data.csv"
start_page = 1
end_page = 10

total_links = 0
total_time = 0

for i in range(start_page, end_page):
    html = scrape_website(f"https://www.fahasa.com/sach-trong-nuoc.html?order=num_orders_year&limit=48&p={i}")
    links = extract_page_content(html)

    print(f"\n📘 Trang {i}: {len(links)} link")

    for idx, link in enumerate(links, start=1):
        link_start = time.time()

        try:
            dom_content = scrape_website(link)
            body_content = extract_body_content(dom_content)
            img_src = extract_image_src(dom_content)
            cleaned_content = img_src + "\n" + clean_body_content(body_content)
            print(cleaned_content)
            extract_book_data_and_export_to_excel(cleaned_content, output_file)

        except Exception as e:
            print(f"❌ Lỗi xử lý link: {link} - {e}")
            continue

        link_end = time.time()
        duration = link_end - link_start
        total_time += duration
        total_links += 1
        avg_time = total_time / total_links

        # Ước tính còn lại
        remaining_links = (end_page - i - 1) * len(links) + (len(links) - idx)
        est_remaining = avg_time * remaining_links

        print(f"⏱️ Link {idx}/{len(links)} trên trang {i} mất {duration:.2f}s - Trung bình: {avg_time:.2f}s/link - Ước tính còn lại: {est_remaining/60:.2f} phút\n")

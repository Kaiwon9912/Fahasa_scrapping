import re
import pandas as pd
import os

def extract_book_data_and_export_to_excel(text, output_file):
    result = {}

    lines = text.strip().split('\n')
    if lines:
        # Dòng đầu là cover image URL
        result["cover_url"] = lines[0].strip()
    if len(lines) > 1:
        # Dòng thứ hai là tên sản phẩm
        result["title"] = lines[1].strip()

    # Giá bán (special price)
    special_price = re.search(r"Special Price\s+([\d\.]+)\s?đ", text)
    if special_price:
        raw_price = special_price.group(1)
        clean_price = raw_price.replace(".", "")  # Xóa dấu chấm
        result["price"] = clean_price


    # Các trường cố định
    fields = {
        "Tên Nhà Cung Cấp": "provider",
        "Tác giả": "author",
        "NXB": "publisher",
        "Năm XB": "published_year",
        "Kích Thước Bao Bì": "size",
        "Số trang": "pages",
        "Hình thức": "cover_type"
    }

    for field in fields:
        pattern = fr"{field}\s*\n(.*?)\n"
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            if fields[field] == "published_year":
                result[fields[field]] = int(value)
            else:
                result[fields[field]] = value

    # Mô tả sản phẩm
    desc_match = re.search(r"Mô tả sản phẩm(.*?)Xem thêm", text, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1).strip()
        result["description"] = re.sub(r"\n{2,}", "\n", desc)

    # Tạo DataFrame cho dòng mới
    new_row = pd.DataFrame([result])

    # Nếu file đã tồn tại, đọc và nối thêm dữ liệu mới
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        final_df = pd.concat([existing_df, new_row], ignore_index=True)
    else:
        final_df = new_row

    # Ghi lại toàn bộ file
    final_df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"✔ Đã thêm dữ liệu vào file {output_file}")

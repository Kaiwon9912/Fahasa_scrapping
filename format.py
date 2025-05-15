import re
import pandas as pd
import os

CATEGORY_MAP = {
    "Thiếu nhi": 1,
    "Giáo khoa - Tham khảo": 2,
    "Văn học": 3,
    "Manga - Comic": 4,
    "Tâm lý - Kỹ năng sống": 5,
    "Sách học ngoại ngữ": 6,
    "Kinh Tế": 7,
    "Lịch Sử - Địa Lý - Tôn Giáo": 8,
    "Khoa học kỹ thuật": 9,
    "Nuôi Dạy Con": 10,
    "Chính Trị - Pháp Lý - Triết Học": 11,
    "Tiểu Sử Hồi Ký": 12,
    "Đam mỹ": 13,
    "Văn Hóa - Nghệ Thuật - Du Lịch": 14,
    "Nữ Công Gia Chánh": 15,
    "Phong Thủy - Kinh Dịch": 16,
    "Từ điển": 17,
    "Âm Nhạc - Mỹ Thuật - Thời Trang": 18,
    "Thể Dục Thể thao - Giải Trí": 19,
    "Báo - Tạp Chí": 20,
    "Giáo trình": 21,
    "Làm Vườn - Thú Nuôi": 22,
    "Mystery Box": 23
}



def extract_book_data_and_export_to_excel(text, output_file):
    result = {}

    lines = text.strip().split('\n')


    if len(lines) >= 1:
        result["cover_url"] = lines[0]

    if len(lines) >= 2:
        category = lines[1]
        result["category"] = category
        result["category_id"] = CATEGORY_MAP.get(category)

    if len(lines) >= 4:
        title_line = lines[3]
        if any(x in title_line for x in ["Bộ", "Combo"]):
            print("Bỏ qua bộ và combo")
            return
        result["title"] = title_line


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

import requests
from bs4 import BeautifulSoup
import random
import time

def scrape_website(website):
    """Lấy HTML của trang web bằng requests"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        time.sleep(random.uniform(0.5, 1.5))  # Random delay để tránh bị chặn
        response = requests.get(website, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu từ {website}: {e}")
        return ""

def extract_body_content(html_content):
    """Trích xuất nội dung body từ HTML"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    content_divs = soup.select(
        "div.block-info-detail-mobile, div.block-product-view-mobile, "
        "div.block-info-detail-2-mobile, div.breadcrumbs li[class='1']"
    )
    return "".join(str(div) for div in content_divs) if content_divs else ""

def clean_body_content(body_content):
    """Làm sạch nội dung, loại bỏ khoảng trắng thừa"""
    if not body_content:
        return ""
    soup = BeautifulSoup(body_content, "lxml")
    cleaned_content = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

def extract_image_src(html_content):
    """Trích xuất src của hình ảnh từ HTML"""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "lxml")
    container = soup.find("div", class_="product-view-image-product fhs_img_frame_container")
    if container:
        img_tag = container.find("img")
        if img_tag:
            return img_tag.get("data-src") or img_tag.get("src") or ""
    return ""

def extract_page_content(html_content):
    """Trích xuất các link sản phẩm từ HTML"""
    if not html_content:
        return []
    soup = BeautifulSoup(html_content, "lxml")
    containers = soup.find_all("div", class_="product images-container")
    return [a["href"] for container in containers for a in container.find_all("a", href=True)]
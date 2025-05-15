from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Đường dẫn ChromeDriver
CHROMEDRIVER_PATH = r"chromedriver.exe"

def scrape_website(website):
    """Mở trình duyệt Chrome và lấy HTML của trang web"""
    print(f"🔍 Đang truy cập: {website}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Chạy không hiển thị trình duyệt
    chrome_options.add_argument("--no-sandbox")  # Bỏ hạn chế sandbox
    chrome_options.add_argument("--enable-unsafe-webgl")  # Cho phép WebGL
    chrome_options.add_argument("--disable-dev-shm-usage")  # Giảm bộ nhớ chia sẻ
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Tắt tải ảnh
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Tránh bị nhận diện là bot
    chrome_options.add_argument("--disable-extensions")  # Tắt extension để chạy nhanh hơn
    chrome_options.add_argument("--disable-popup-blocking")  # Tắt chặn popup
    chrome_options.add_argument("--disable-remote-fonts")  # Tắt tải font từ web
    chrome_prefs = {
        "profile.default_content_setting_values": {
            "images": 2,  # Không tải ảnh
            "stylesheet": 2,  # Không tải CSS
            "notifications": 2,  # Tắt thông báo
            "geolocation": 2  # Tắt yêu cầu vị trí
        }
    }
    chrome_options.experimental_options["prefs"] = chrome_prefs

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(website)
        html = driver.page_source.strip()  # Loại bỏ khoảng trắng đầu/cuối
        if not html:
            raise ValueError("⚠️ Không thể lấy dữ liệu: Nội dung rỗng!")
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu từ {website}: {e}")
        html = ""  # Trả về chuỗi rỗng nếu có lỗi
    finally:
        driver.quit()

    return html

def extract_body_content(html_content):
    """Trích xuất nội dung body từ HTML"""
    soup = BeautifulSoup(html_content, "html.parser")

    # Tìm tất cả các div có 1 trong 2 class
    content_divs = soup.select("div.block-info-detail-mobile, div.block-product-view-mobile, div.block-info-detail-2-mobile" )

    if not content_divs:
        return ""

    # Gộp toàn bộ HTML lại
    combined_html = "".join(str(div) for div in content_divs)

    return combined_html


def clean_body_content(body_content):
    """Làm sạch nội dung, loại bỏ script, style, header, footer, nav và các div có class 'header' hoặc 'footer'."""
    soup = BeautifulSoup(body_content, "html.parser")
    img_src=""
    container = soup.find("div", class_="product-view-image-product fhs_img_frame_container")
    if container:
        img_tag = container.find("img")
        if img_tag:
            img_src= img_tag.get("data-src") or img_tag.get("src")

    # Lấy nội dung văn bản và làm sạch khoảng trắng
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content





def extract_image_src(html_content):
    """Trích xuất src của hình ảnh từ HTML"""
    soup = BeautifulSoup(html_content, "html.parser")
    container = soup.find("div", class_="product-view-image-product fhs_img_frame_container")
    if container:
        img_tag = container.find("img")
        if img_tag:
            return img_tag.get("data-src") or img_tag.get("src")

def extract_page_content(html_content):
    """Trích xuất nội dung từ HTML"""
    soup = BeautifulSoup(html_content, "html.parser")
    containers = soup.find_all("div", class_="product images-container")
    links = [a["href"] for container in containers for a in container.find_all("a", href=True)]
    return links
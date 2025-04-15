# AOI OCR Hotkey Tool

Một công cụ hỗ trợ OCR (Optical Character Recognition) cho hệ thống AOI, cho phép người dùng chọn vùng ảnh bằng phím nóng (hotkey) và thực hiện nhận dạng ký tự bằng Tesseract OCR.

## 🛠 Tính năng

- Dùng phím nóng để chụp vùng màn hình.
- Nhận diện văn bản trong ảnh sử dụng Tesseract OCR.
- Hỗ trợ nhiều ngôn ngữ OCR (tùy chọn).
- Dễ sử dụng, gọn nhẹ, không cần GUI phức tạp.

## 🖥 Yêu cầu hệ thống

- Python >= 3.8
- Hệ điều hành: Windows
- Đã cài đặt Tesseract OCR

## 📦 Cài đặt
Tải file exe Tesseract v5.5.0
https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe/download
1. Clone repo:

```bash
git clone https://github.com/kidovnoz/aoi-ocr-hotkey.git
cd aoi-ocr-hotkey


python ocr_hotkey.py

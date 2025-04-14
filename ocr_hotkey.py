import keyboard
import pyautogui
from PIL import ImageGrab, ImageDraw
import time
from datetime import datetime
import threading
import json
import os
import easyocr
import numpy as np
import csv
import cv2
# Khởi tạo EasyOCR reader
reader = easyocr.Reader(['en'], gpu=False, verbose=False, download_enabled=False)

REGIONS_FILE = "ocr_regions.json"
regions = []

if os.path.exists(REGIONS_FILE):
    with open(REGIONS_FILE, 'r') as f:
        regions = json.load(f)

showing_coords = False
click_stage = 0
point1 = None
def run_ocr_all():
    if not regions:
        print("⚠️ Chưa có vùng nào để OCR!")
        return []

    full_screenshot = ImageGrab.grab()
    # full_screenshot = full_screenshot.resize((640, 480))
    img_np = np.array(full_screenshot)
    ocr_results = []

    for i, region in enumerate(regions, start=1):
        x1, y1, x2, y2 = region
        if x2 <= x1 or y2 <= y1:
            print(f"⚠️ Bỏ qua vùng lỗi (tọa độ sai): {region}")
            continue
        print(f"🕒 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖼️ Vùng {i} [{x1}, {y1}, {x2}, {y2}]:")
        cropped_img = img_np[y1:y2, x1:x2]
        results = reader.readtext(cropped_img)

        if not results:
            print("📭 Không nhận diện được văn bản.")
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for (_, text, conf) in results:
                print(f"🔤 {text} (⏱ {conf:.2f})")
                if conf > 0.5:
                    log_to_csv(timestamp, i, region, text, conf)
                    ocr_results.append((i, region, text, timestamp))

        print("-" * 60)
    return ocr_results

def show_mouse_position():
    global showing_coords
    showing_coords = True
    print("\n📍 Đang hiển thị tọa độ chuột. Nhấn F3 lần nữa để dừng.\n")
    last_pos = (-1, -1)
    while showing_coords:
        x, y = pyautogui.position()
        if (x, y) != last_pos:
            print(f"Tọa độ hiện tại: ({x}, {y})", end="\r")
            last_pos = (x, y)
        time.sleep(0.3)
    print("\n🛑 Đã dừng hiển thị tọa độ.")

def toggle_show_coords():
    global showing_coords
    if not showing_coords:
        threading.Thread(target=show_mouse_position, daemon=True).start()
    else:
        showing_coords = False

def mark_region():
    global click_stage, point1
    if click_stage == 0:
        point1 = pyautogui.position()
        print(f"📌 Điểm bắt đầu: {point1}")
        click_stage = 1
    else:
        point2 = pyautogui.position()
        print(f"📌 Điểm kết thúc: {point2}")
        x1, y1 = point1
        x2, y2 = point2
        region = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        regions.append(region)
        with open(REGIONS_FILE, 'w') as f:
            json.dump(regions, f)
        print(f"✅ Đã thêm vùng OCR: {region}")
        click_stage = 0

def show_all_regions():
    if not regions:
        print("⚠️ Chưa có vùng nào để hiển thị!")
        return

    screenshot = ImageGrab.grab()
    draw = ImageDraw.Draw(screenshot)
    for i, (x1, y1, x2, y2) in enumerate(regions, start=1):
        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1 + 5, y1 + 5), f"V{i}", fill="yellow")
    screenshot.save("temp_regions.png")
    os.startfile("temp_regions.png")

def clear_all_regions():
    global regions
    confirm = input("⚠️ Bạn có chắc muốn xoá toàn bộ vùng OCR? (y/n): ").lower()
    if confirm == 'y':
        regions = []
        if os.path.exists(REGIONS_FILE):
            os.remove(REGIONS_FILE)
        print("🧹 Đã xoá toàn bộ vùng OCR!")
    else:
        print("❎ Đã huỷ thao tác.")
def log_to_csv(timestamp, region_id, coords, text, conf):
    file_exists = os.path.isfile("ocr_log.csv")
    with open("ocr_log.csv", mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Thời gian", "Vùng", "Tọa độ", "Văn bản", "Độ tin cậy"])
        writer.writerow([timestamp, f"Vùng {region_id}", coords, text, f"{conf:.2f}"])

def save_regions_as_images(ocr_results):
    if not ocr_results:
        print("⚠️ Không có kết quả OCR để lưu ảnh!")
        return

    folder = "captured_images"
    os.makedirs(folder, exist_ok=True)
    full_screenshot = ImageGrab.grab()

    for region_id, region, text_ocr, timestamp in ocr_results:
        x1, y1, x2, y2 = region
        if x2 <= x1 or y2 <= y1:
            print(f"⚠️ Bỏ qua vùng lỗi: {region}")
            continue
        cropped_img = full_screenshot.crop((x1, y1, x2, y2))
        safe_text = ''.join(c for c in text_ocr.strip().replace(" ", "_") if c.isalnum() or c in ('_', '-'))
        filename = f"{folder}/region_{region_id}_{safe_text}_{timestamp.replace(':', '-')}.png"
        cropped_img.save(filename, optimize=True, quality=85)
        print(f"💾 Đã lưu ảnh vùng {region_id} tại: {filename}")

print("\n======================= OCR TOOL =======================")
print("🟢 F2: Quét toàn bộ vùng OCR")
print("🔵 F3: Xem tọa độ chuột")
print("🟡 F4: Đánh dấu 2 điểm tạo vùng OCR")
print("🟣 F5: Hiển thị các vùng OCR")
print("🟠 F6: Xoá toàn bộ vùng OCR")
print("🔴 ESC: Thoát chương trình")
print("========================================================")

while True:
    if keyboard.is_pressed('f2'):
        ocr_results = run_ocr_all()
        if ocr_results:
            print("🖼️ Đã quét xong các vùng OCR.")
            save_regions_as_images(ocr_results)
        else:
            print("⚠️ Không có văn bản nào được nhận diện.")
        time.sleep(0.5)

    elif keyboard.is_pressed('f3'):
        toggle_show_coords()
        time.sleep(0.5)
    elif keyboard.is_pressed('f4'):
        mark_region()
        time.sleep(0.5)
    elif keyboard.is_pressed('f5'):
        show_all_regions()
        time.sleep(0.5)
    elif keyboard.is_pressed('f6'):
        clear_all_regions()
        time.sleep(0.5)
    elif keyboard.is_pressed('esc'):
        print("\n👋 Đã thoát chương trình.")
        break
    time.sleep(0.1)
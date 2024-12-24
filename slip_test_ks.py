import re
import pytesseract
import cv2
from pyzbar.pyzbar import decode

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_date(text):
    match = re.search(r'\d{1,2}\s[ก-๙]\.[ก-๙]\.\s\d{2}', text)
    return match.group() if match else "ไม่พบวันที่"

def extract_time(text):
    match = re.search(r'\d{2}:\d{2}', text)
    return match.group() if match else "ไม่พบเวลา"

def extract_names(text):
    matches =  re.findall(r'\s*[ก-๙]+\s*[ก-๙]+', text)
    if matches and len(matches) >= 2:
        return {"ผู้โอน": matches[1], "ธนาคารผู้โอน": matches[3], "ผู้รับโอน": matches[4] + ' ' + matches[5].strip()[:-1], "ธนาคารผู้รับโอน": matches[6]}
        
    return {"ผู้โอน": "ไม่พบชื่อ", "ผู้รับโอน": "ไม่พบชื่อ"}

def extract_transaction_details(image_path):
    raw_text = pytesseract.image_to_string(image_path, lang='tha+eng')

    details = {
        "วันที่": extract_date(raw_text),
        "เวลา": extract_time(raw_text),
    }

    names = extract_names(raw_text)
    details.update(names)

    transaction_id_match = re.search(r'เลขที่รายการ:\s*([\dA-Za-z]+)', raw_text)
    details['เลขที่รายการ'] = transaction_id_match.group(1) if transaction_id_match else "ไม่พบเลขที่รายการ"

    amount_match = re.search(r'\d+\.\d{2} บาท', raw_text)
    details['จำนวนเงิน'] = re.sub(r' บาท', '', amount_match.group()) if amount_match else "ไม่พบจำนวนเงิน"

    qr_codes = decode(cv2.imread(image_path))
    details['qrcode'] = qr_codes[0].data.decode('utf-8') if qr_codes else "ไม่พบ QR code"

    return details

image_path = "S__14139405.jpg"
transaction_details = extract_transaction_details(image_path)

for key, value in transaction_details.items():
    print(f"{key}: {value}")

import cv2
import pytesseract

from PIL import Image
import os
import re

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def normalize_token(token: str) -> str:
    # 通常 hh:mm:ss
    m = re.fullmatch(r'(\d{1,2}):(\d{2}):(\d{2})', token)
    if m:
        h, m_, s = m.groups()
        return f"{int(h):02d}:{int(m_):02d}:{int(s):02d}"

    # 3桁 + :mm:ss → 日 + 時 (例: 114:32:52 → 1d 14:32:52, 218:05:12 → 2d 18:05:12)
    m = re.fullmatch(r'(\d{3}):(\d{2}):(\d{2})', token)
    if m:
        h3, m_, s = m.groups()
        d = int(h3[0])
        h = int(h3[1:])
        return f"{d}d {h:02d}:{int(m_):02d}:{int(s):02d}"

    # 4桁 + :mm:ss → 日 + 時 (例: 1015:35:04 → 1d 15:35:04, 1422:17:23 → 1d 22:17:23 とみなす)
    m = re.fullmatch(r'(\d{4}):(\d{2}):(\d{2})', token)
    if m:
        h4, m_, s = m.groups()
        # 先頭1桁を日、残り3桁のうち下2桁を時とみなす
        d = int(h4[0])          # 1
        h = int(h4[-2:])        # 15, 22 など
        return f"{d}d {h:02d}:{int(m_):02d}:{int(s):02d}"

    return ""

def extract_times_from_image(image_name: str):
    image_path = os.path.join(SCRIPT_DIR, image_name)
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError("画像が読み込めていません。")

    img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    _, th = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789:'
    text = pytesseract.image_to_string(th, config=config)
    print("RAW TEXT:")
    print(text)

    raw_tokens = re.findall(r'\d+:\d{2}:\d{2}', text)

    times = []
    for token in raw_tokens:
        norm = normalize_token(token)
        if norm:
            times.append(norm)

    times = list(dict.fromkeys(times))
    return times

if __name__ == "__main__":
    image_file = "wos.png"

    times = extract_times_from_image(image_file)

    out_path = os.path.join(SCRIPT_DIR, "times.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for t in times:
            f.write(t + "\n")

    print("抽出した時間:")
    for t in times:
        print(t)

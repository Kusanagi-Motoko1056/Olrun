import os
import time
import requests
import sys
import tkinter as tk  # 用於讀取剪貼簿 (For clipboard)
from bs4 import BeautifulSoup
from google import genai

# ==========================================
# 設定區 (Configuration)
# ==========================================

# ⚠️⚠️⚠️ 請在此填入您新申請的 API Key ⚠️⚠️⚠️
# 申請網址: https://aistudio.google.com/app/apikey
API_KEY = 'AIzaSyCB4LbyBCy1SZ-WN6nYkiaqgFk6T3rL0u8' 

# 強制設定標準輸出編碼為 utf-8 (Force UTF-8 encoding)
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 核心功能：初始化 Client 與設定模型
# ==========================================
def setup_gemini_client():
    """初始化 Client 並自動尋找最佳模型 ID"""
    print("[系統 System] 正在連接 Google AI 初始化 Client... (Connecting to Google AI...)")
    
    try:
        # 簡單檢查 Key 是否還是預設文字
        if '請在此' in API_KEY or len(API_KEY) < 10:
            print("\n" + "!"*50)
            print("[嚴重錯誤 Critical Error]")
            print("您尚未填入有效的 API Key！(You have not entered a valid API Key!)")
            print("請打開程式碼，修改 'API_KEY' 欄位。")
            print("Please open the code and update the 'API_KEY' variable.")
            print("!"*50 + "\n")
            return None, None

        client = genai.Client(api_key=API_KEY)
        
        # 嘗試列出模型來測試連線 (Test connection)
        try:
            all_models = list(client.models.list())
        except Exception as e:
            if "API key expired" in str(e) or "400" in str(e):
                print(f"[錯誤 Error] API Key 已過期或無效 (Key Expired): {e}")
                print("請去 https://aistudio.google.com/app/apikey 申請新的 Key。")
                return None, None
            raise e

        available_models = [m.name for m in all_models]
        
        if not available_models:
            print("[錯誤 Error] 找不到任何可用的模型 (No available models found).")
            return None, None

        selected_model_id = None
        preferences = ["gemini-2.0-flash", "gemini-1.5-flash", "flash", "pro"]
        
        for pref in preferences:
            for m_name in available_models:
                if pref in m_name.lower() and "vision" not in m_name.lower(): 
                    selected_model_id = m_name
                    break
            if selected_model_id:
                break
        
        if not selected_model_id:
            selected_model_id = available_models[0]

        if selected_model_id.startswith("models/"):
            selected_model_id = selected_model_id.replace("models/", "")

        print(f"[成功 Success] 初始化完成 (Initialized), Model ID: {selected_model_id}")
        return client, selected_model_id

    except Exception as e:
        print(f"[錯誤 Error] API 連線設定失敗 (Connection Failed): {e}")
        return None, None

# 初始化 (Global)
client, MODEL_ID = setup_gemini_client()

# 定義支援的語言映射
SUPPORTED_LANGUAGES = {
    "1": ("現代中文 (Modern Chinese)", "Traditional Chinese (Modern)"),
    "2": ("文言文 (Classical Chinese)", "Classical Chinese (Literary Chinese)"),
    "3": ("現代英文 (Modern English)", "Modern English"),
    "4": ("中古英文 (Middle English)", "Middle English (e.g., Chaucer style)"),
    "5": ("古英文 (Old English)", "Old English (Anglo-Saxon, e.g., Beowulf style)"),
    "6": ("拉丁文 (Latin)", "Latin"),
    "7": ("古希臘文 (Ancient Greek)", "Ancient Greek"),
    "8": ("現代希臘文 (Modern Greek)", "Modern Greek"),
    "9": ("古希伯來文 (Biblical Hebrew)", "Biblical Hebrew"),
    "10": ("現代希伯來文 (Modern Hebrew)", "Modern Hebrew"),
    "11": ("古法文 (Old French)", "Old French"),
    "12": ("現代法文 (Modern French)", "Modern French"),
    "13": ("古德文 (Old German)", "Old High German"),
    "14": ("現代德文 (Modern German)", "Modern German"),
    "15": ("古西班牙文 (Old Spanish)", "Old Spanish"),
    "16": ("現代西班牙文 (Modern Spanish)", "Modern Spanish"),
    "17": ("古日文 (Classical Japanese)", "Classical Japanese (Kobun)"),
    "18": ("現代日文 (Modern Japanese)", "Modern Japanese"),
    "19": ("古韓文 (Old Korean)", "Middle Korean"),
    "20": ("現代韓文 (Modern Korean)", "Modern Korean"),
    "21": ("現代俄文 (Modern Russian)", "Modern Russian"),
    "22": ("古俄文 (Old Russian)", "Old East Slavic / Old Russian (pre-18th century style)"),
    "23": ("中英對照 (Bilingual: CN/EN)", "Traditional Chinese. IMPORTANT: Output in Bilingual Format. For each paragraph, show the Original English Text first, followed immediately by the Chinese Translation.")
}

# ==========================================
# 其他功能函數
# ==========================================

def get_web_content(url):
    print(f"[系統 System] 正在讀取網頁 (Reading URL): {url} ...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            script.extract()
        text = soup.get_text(separator='\n', strip=True)
        return text
    except Exception as e:
        print(f"[錯誤 Error] 網頁讀取失敗 (Failed to read URL): {e}")
        return None

def get_clipboard_text():
    try:
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        print("[系統 System] 已從剪貼簿讀取內容 (Read from clipboard successfully)！")
        return text
    except Exception as e:
        print(f"[錯誤 Error] 無法讀取剪貼簿 (Cannot read clipboard): {e}")
        return ""

def save_to_txt(content, target_lang_name):
    safe_lang_name = target_lang_name.replace("/", "_").replace(" ", "_").replace("(", "").replace(")", "")
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"translation_{safe_lang_name}_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[存檔 Saved] 檔案已儲存為 (File saved as): {filename}")
    except Exception as e:
        print(f"[錯誤 Error] 存檔失敗 (Failed to save file): {e}")

def translate_with_gemini(text, target_lang_prompt):
    if not client or not MODEL_ID:
        return "錯誤 (Error)：Client 未初始化或 Key 無效 (Client not initialized or Invalid Key)."

    print("\n[系統 System] Gemini 正在翻譯中 (Gemini is translating)...")
    
    prompt_text = (
        f"Please translate the following text into {target_lang_prompt}. "
        f"Maintain the original tone and style appropriately for that time period if it is an ancient language. "
        f"Do not add explanations, just provide the translated text.\n\n"
        f"Original Text:\n{text}"
    )

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "API key expired" in error_msg:
            return "【嚴重錯誤】API Key 已過期 (API Key Expired)。請申請新的 Key。"
        if "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
            return f"API 參數錯誤 (API Error): {error_msg} (請檢查 Key 是否正確)"
        return f"API 呼叫錯誤 (Unknown API Error): {error_msg}"

# ==========================================
# 主程式 (Main Loop)
# ==========================================

def main():
    print("=== 全語言時光翻譯機 (v3.6 Loop & Menu Version) ===")
    
    if not client:
        print("程式無法啟動：請先修復 API Key 問題 (Program Exit: Please fix API Key first).")
        return

    # 進入主選單循環 (Main Loop)
    while True:
        print("\n" + "="*40)
        print("   主選單 (Main Menu)")
        print("="*40)
        
        mode = ""
        while True:
            try:
                print("1: 輸入網址 (Enter URL)")
                print("2: 直接輸入文字 (Enter Text Manually)")
                print("3: 自動讀取剪貼簿 (Read from Clipboard) [推薦!]")
                print("Q: 離開程式 (Quit)")
                
                mode = input("您的選擇 (Your Choice): ").strip().lower()
                
                if mode == 'q':
                    print("再見！(Goodbye!)")
                    return # 結束程式
                if mode in ['1', '2', '3']:
                    break
                print(">> 輸入錯誤，請重新輸入 (Invalid Input) <<\n")
            except UnicodeDecodeError:
                print("編碼錯誤 (Encoding Error).")

        source_text = ""
        
        # 執行選擇的模式
        if mode == '1':
            url = input("請輸入網址 (Enter URL): ").strip()
            source_text = get_web_content(url)
            if not source_text: continue # 失敗則回到主選單
        elif mode == '2':
            print("請輸入文字，結束請按兩次 Enter (Enter text, press Enter twice to finish):")
            lines = []
            while True:
                try:
                    line = input()
                    if line: lines.append(line)
                    else: break
                except UnicodeDecodeError:
                    continue 
            source_text = "\n".join(lines)
        elif mode == '3':
            source_text = get_clipboard_text()
            if not source_text:
                print("剪貼簿是空的 (Clipboard is empty)！")
                continue # 回到主選單

        if not source_text.strip():
            print("沒有內容可以翻譯！")
            continue

        # 顯示預覽
        preview = source_text[:100].replace('\n', ' ')
        print(f"\n--- 原始內容預覽 (Content Preview) ---\n{preview}...\n--------------------------------------")

        # 選擇語言
        print("\n請選擇目標語言代號 (Select Target Language ID):")
        items = list(SUPPORTED_LANGUAGES.items())
        for i in range(0, len(items), 2):
            key1, val1 = items[i]
            str1 = f"{key1.ljust(2)}: {val1[0]}"
            if i + 1 < len(items):
                key2, val2 = items[i+1]
                str2 = f"{key2.ljust(2)}: {val2[0]}"
                print(f"{str1:<45} | {str2}")
            else:
                print(str1)

        lang_choice = input("\n輸入代號 (Enter ID) [e.g., 23]: ").strip()
        
        if lang_choice not in SUPPORTED_LANGUAGES:
            print("無效的語言代號 (Invalid Language ID).")
            continue # 回到主選單

        target_lang_name = SUPPORTED_LANGUAGES[lang_choice][0]
        target_lang_prompt = SUPPORTED_LANGUAGES[lang_choice][1]

        # 執行翻譯
        translated_text = translate_with_gemini(source_text, target_lang_prompt)

        print(f"\n=== 翻譯結果 (Translation Result: {target_lang_name}) ===")
        print(translated_text)
        print("=========================================================")
        
        save_to_txt(translated_text, target_lang_name)
        
        # 循環結束，自動回到最上面的 while True

if __name__ == "__main__":
    main()
import os
import time
import requests
import sys
from bs4 import BeautifulSoup
from google import genai

# ==========================================
# 設定區 (Configuration)
# ==========================================

# ⚠️ 嚴重警告：請去申請一組新的 Key，填入下方引號中。
# 填寫完後，請存檔並在自己電腦執行，不要再將此段代碼貼到網路上。
API_KEY = 'AIzaSyDyMoXu3g6BugUFVbgWrB1_9qd5wzgE-PI' 

# 強制設定標準輸出編碼為 utf-8，解決 Windows console 亂碼問題
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# 核心功能：初始化 Client 與設定模型
# ==========================================
def setup_gemini_client():
    """初始化 Client 並自動尋找最佳模型 ID"""
    print("[系統] 正在連接 Google AI 初始化 Client...")
    
    try:
        # 檢查是否忘記填寫 Key
        if '請在此填入' in API_KEY or len(API_KEY) < 10:
            print("[錯誤] 您尚未填入有效的 API Key，請修改程式碼中的 API_KEY 欄位。")
            return None, None

        # 1. 初始化 Client
        client = genai.Client(api_key=API_KEY)
        
        # 2. 列出並篩選模型
        all_models = list(client.models.list())
        available_models = [m.name for m in all_models]
        
        if not available_models:
            print("[錯誤] 找不到任何可用的模型。請檢查 API Key 權限。")
            return None, None

        # 3. 優先順序策略
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

        print(f"[成功] 初始化完成，選用模型 ID: {selected_model_id}")
        return client, selected_model_id

    except Exception as e:
        print(f"[錯誤] API 連線設定失敗: {e}")
        return None, None

# 初始化 (全域變數)
client, MODEL_ID = setup_gemini_client()

# 定義支援的語言映射 (已加入俄文與古俄文)
SUPPORTED_LANGUAGES = {
    "1": ("現代中文", "Traditional Chinese (Modern)"),
    "2": ("文言文", "Classical Chinese (Literary Chinese)"),
    "3": ("現代英文", "Modern English"),
    "4": ("中古英文", "Middle English (e.g., Chaucer style)"),
    "5": ("古英文", "Old English (Anglo-Saxon, e.g., Beowulf style)"),
    "6": ("拉丁文", "Latin"),
    "7": ("古希臘文", "Ancient Greek"),
    "8": ("現代希臘文", "Modern Greek"),
    "9": ("古希伯來文", "Biblical Hebrew"),
    "10": ("現代希伯來文", "Modern Hebrew"),
    "11": ("古法文", "Old French"),
    "12": ("現代法文", "Modern French"),
    "13": ("古德文", "Old High German"),
    "14": ("現代德文", "Modern German"),
    "15": ("古西班牙文", "Old Spanish"),
    "16": ("現代西班牙文", "Modern Spanish"),
    "17": ("古日文", "Classical Japanese (Kobun)"),
    "18": ("現代日文", "Modern Japanese"),
    "19": ("古韓文", "Middle Korean"),
    "20": ("現代韓文", "Modern Korean"),
    "21": ("現代俄文", "Modern Russian"),
    "22": ("古俄文", "Old East Slavic / Old Russian (pre-18th century style)")
}

# ==========================================
# 其他功能函數
# ==========================================

def get_web_content(url):
    """讀取網頁並回傳純文字"""
    print(f"正在讀取網頁: {url} ...")
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
        print(f"網頁讀取錯誤: {e}")
        return None

def save_to_txt(content, target_lang_name):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"translation_{target_lang_name}_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[存檔] 檔案已成功儲存為: {filename}")
    except Exception as e:
        print(f"[錯誤] 存檔失敗: {e}")

def translate_with_gemini(text, target_lang_prompt):
    """呼叫 Gemini API 進行翻譯"""
    if not client or not MODEL_ID:
        return "錯誤：Client 或模型未正確初始化，無法翻譯。"

    print("\n[系統] Gemini 正在進行翻譯轉換，請稍候...")
    
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
        # 捕捉特定的權限錯誤並給予清楚提示
        if "403" in str(e) or "PERMISSION_DENIED" in str(e):
            return "嚴重錯誤：API Key 無效或已被封鎖。請更換新的 API Key。"
        return f"API 呼叫錯誤: {e}"

# ==========================================
# 主程式 (Main)
# ==========================================

def main():
    print("=== 全語言時光翻譯機 (v3.2 俄文擴充版) ===")
    
    if not client:
        print("無法取得可用 Client，程式即將結束。")
        return

    while True:
        try:
            mode = input("\n請選擇輸入模式 (1: 輸入網址, 2: 直接輸入文字): ").strip()
            if mode in ['1', '2']:
                break
            print("輸入錯誤，請輸入 1 或 2")
        except UnicodeDecodeError:
            print("輸入編碼錯誤，請再試一次。")

    source_text = ""
    
    if mode == '1':
        url = input("請輸入網址 (URL): ").strip()
        source_text = get_web_content(url)
        if not source_text: return
    else:
        print("請輸入要翻譯的文字 (輸入完畢後按 Enter，若有多行可貼上後按兩次 Enter 結束):")
        lines = []
        while True:
            try:
                line = input()
                if line: lines.append(line)
                else: break
            except UnicodeDecodeError:
                continue 
        source_text = "\n".join(lines)

    if not source_text.strip():
        print("沒有內容可以翻譯！")
        return

    preview = source_text[:100].replace('\n', ' ')
    print(f"\n--- 原始內容預覽 ---\n{preview}...\n--------------------")

    print("\n請選擇目標語言代號:")
    items = list(SUPPORTED_LANGUAGES.items())
    for i in range(0, len(items), 2):
        key1, val1 = items[i]
        str1 = f"{key1.ljust(2)}: {val1[0]}"
        if i + 1 < len(items):
            key2, val2 = items[i+1]
            str2 = f"{key2.ljust(2)}: {val2[0]}"
            print(f"{str1:<30} | {str2}")
        else:
            print(str1)

    lang_choice = input("\n輸入代號 (例如 21 代表現代俄文): ").strip()
    
    if lang_choice not in SUPPORTED_LANGUAGES:
        print("無效的語言代號，程式結束。")
        return

    target_lang_name = SUPPORTED_LANGUAGES[lang_choice][0]
    target_lang_prompt = SUPPORTED_LANGUAGES[lang_choice][1]

    translated_text = translate_with_gemini(source_text, target_lang_prompt)

    print(f"\n=== 翻譯結果 ({target_lang_name}) ===")
    print(translated_text)
    print("====================================")
    
    save_to_txt(translated_text, target_lang_name)

if __name__ == "__main__":
    main()
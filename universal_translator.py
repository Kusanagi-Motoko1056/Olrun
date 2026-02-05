import os
import time
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ==========================================
# 設定區 (Configuration)
# ==========================================

# ⚠️ 請將此處替換為你的 Gemini API Key
API_KEY = 'AIzaSyDCnu6ZNFR0TXb-YwdxVNxjbSLSsa5V6sI' 

# ==========================================
# 核心功能：自動偵測並設定模型
# ==========================================
def setup_gemini_model():
    """自動尋找可用的模型，解決 404 錯誤"""
    print("正在連接 Google AI 尋找可用模型...")
    genai.configure(api_key=API_KEY)
    
    try:
        available_models = []
        # 列出所有模型
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if not available_models:
            print("❌ 錯誤：找不到任何可用的文字生成模型。請檢查 API Key 權限。")
            return None

        # 優先順序策略：優先使用 Flash (快) -> Pro (強) -> 其他
        selected_model = None
        for model_name in available_models:
            if "flash" in model_name:
                selected_model = model_name
                break
        
        if not selected_model:
            for model_name in available_models:
                if "pro" in model_name:
                    selected_model = model_name
                    break
        
        # 如果都沒找到，就用列表中的第一個
        if not selected_model:
            selected_model = available_models[0]

        print(f"✅ 成功選用模型: {selected_model}")
        return genai.GenerativeModel(selected_model)

    except Exception as e:
        print(f"❌ API 連線設定失敗: {e}")
        return None

# 初始化模型 (全域變數)
model = setup_gemini_model()

# 定義支援的語言映射
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
    "20": ("現代韓文", "Modern Korean")
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
        for script in soup(["script", "style", "nav", "footer", "header"]):
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
        print(f"✅ 檔案已成功儲存為: {filename}")
    except Exception as e:
        print(f"存檔失敗: {e}")

def translate_with_gemini(text, target_lang_prompt):
    """呼叫 Gemini API 進行翻譯"""
    if not model:
        return "錯誤：模型未正確初始化，無法翻譯。"

    print("\n🚀 Gemini 正在進行翻譯轉換，請稍候...")
    prompt = (
        f"Please translate the following text into {target_lang_prompt}. "
        f"Maintain the original tone and style appropriately for that time period if it is an ancient language. "
        f"Do not add explanations, just provide the translated text.\n\n"
        f"Original Text:\n{text}"
    )

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"API 呼叫錯誤: {e}"

# ==========================================
# 主程式 (Main)
# ==========================================

def main():
    print("=== 全語言時光翻譯機 (v2.0 自動偵測版) ===")
    
    if not model:
        print("無法取得可用模型，程式即將結束。")
        return

    # 1. 選擇輸入來源
    while True:
        mode = input("\n請選擇輸入模式 (1: 輸入網址, 2: 直接輸入文字): ").strip()
        if mode in ['1', '2']:
            break
        print("輸入錯誤，請輸入 1 或 2")

    source_text = ""
    
    if mode == '1':
        url = input("請輸入網址 (URL): ").strip()
        source_text = get_web_content(url)
        if not source_text: return
    else:
        print("請輸入要翻譯的文字 (輸入完畢後按 Enter，若有多行可貼上後按兩次 Enter 結束):")
        lines = []
        while True:
            line = input()
            if line: lines.append(line)
            else: break
        source_text = "\n".join(lines)

    if not source_text.strip():
        print("沒有內容可以翻譯！")
        return

    print(f"\n--- 原始內容預覽 (前100字) ---\n{source_text[:100]}...\n----------------------------")

    # 2. 選擇目標語言
    print("\n請選擇目標語言代號:")
    for key, val in SUPPORTED_LANGUAGES.items():
        print(f"{key.ljust(3)}: {val[0]}")

    lang_choice = input("輸入代號 (例如 4 代表中古英文): ").strip()
    
    if lang_choice not in SUPPORTED_LANGUAGES:
        print("無效的語言代號，程式結束。")
        return

    target_lang_name = SUPPORTED_LANGUAGES[lang_choice][0]
    target_lang_prompt = SUPPORTED_LANGUAGES[lang_choice][1]

    # 3. 執行翻譯
    translated_text = translate_with_gemini(source_text, target_lang_prompt)

    # 4. 顯示與存檔
    print(f"\n=== 翻譯結果 ({target_lang_name}) ===")
    print(translated_text)
    print("====================================")
    
    save_to_txt(translated_text, target_lang_name)

if __name__ == "__main__":
    main()
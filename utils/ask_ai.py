import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 正しいエンドポイントの構成
resource_name = os.getenv('AZURE_OPENAI_RESOURCE_NAME')
deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
api_version = os.getenv('AZURE_OPENAI_API_VERSION')
api_key = os.getenv('AZURE_OPENAI_API_KEY')

endpoint = f"https://{resource_name}.openai.azure.com/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

# ヘッダー（Azure OpenAI は "api-key" を使用）
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

def extract_text_from_file(file_path, mime_type):
    """
    シンプルなテキスト抽出関数
    MIME タイプが "text/..." の場合は内容を読み込み、他は空文字を返す。
    必要に応じて他のファイル形式の処理を追加してください。
    """
    if mime_type.startswith("text/"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    # ここでPDF, DOCX, 画像などに対する処理も追加可能
    return ""

def generate_response(conversation_history, files=None):
    """
    conversation_history: これまでの会話履歴（リスト）
    files: オプション。各ファイルは辞書形式 { "file_path": <パス>, "mime_type": <MIMEタイプ> } とする
    """
    # ファイルが渡されている場合、各ファイルからテキストを抽出し、会話履歴に追加
    if files:
        for file_info in files:
            file_path = file_info.get("file_path")
            mime_type = file_info.get("mime_type", "text/plain")
            filename = os.path.basename(file_path)
            file_text = extract_text_from_file(file_path, mime_type)
            conversation_history.append({
                "role": "user",
                "content": f"File {filename} content:\n{file_text}"
            })

    # システムメッセージを先頭に追加（必要に応じて変更してください）
    system_message = {"role": "system", "content": "##や--など文章と関係ない文字は含めないで。また可読性を上げるために。ごとに改行をして。"}
    messages = [system_message] + conversation_history

    data = {
        "messages": messages,
        "max_tokens": 1000,
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()  # HTTPエラーなら例外発生
        response_data = response.json()
        ai_message = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
        return ai_message
    except requests.exceptions.RequestException as e:
        print(f"❌ APIエラー: {e}")
        return "Error: Failed to contact AI server."

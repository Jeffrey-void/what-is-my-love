import os
import re
import json
from dotenv import load_dotenv
from anthropic import Anthropic
import httpx

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
base_url = os.getenv("ANTHROPIC_BASE_URL")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다")

# 프록시 설정을 무시하고 직접 클라이언트 생성
http_client = httpx.Client(trust_env=False)
client = Anthropic(
    api_key=api_key,
    base_url=base_url,
    http_client=http_client
)


def extract_json(text):
    """텍스트에서 JSON 객체를 추출"""
    text = text.strip()

    # 마크다운 코드블록 제거
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    text = text.strip()

    # 첫 번째 { 찾기
    start = text.find('{')
    if start == -1:
        raise ValueError("JSON 객체를 찾을 수 없습니다")

    # 스택을 이용해 매칭하는 } 찾기
    depth = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i
                break

    if end == -1:
        raise ValueError("JSON 객체가 닫혀있지 않습니다")

    json_str = text[start:end+1].strip()

    # JSON 유효성 검사
    try:
        json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"유효하지 않은 JSON: {str(e)}")

    return json_str


def ask_ai(prompt):
    try:
        res = client.messages.create(
            model="claude-haiku",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = res.content[0].text
        print(f"[DEBUG] API 응답 받음: {len(response_text)}자")
        print(f"[DEBUG] 원본 응답: {response_text[:300]}")

        extracted = extract_json(response_text)
        print(f"[DEBUG] 추출된 JSON: {extracted[:200]}")
        return extracted
    except ValueError as e:
        print(f"[DEBUG] JSON 처리 오류: {str(e)}")
        raise
    except Exception as e:
        print(f"[DEBUG] API 호출 오류: {str(e)}")
        raise

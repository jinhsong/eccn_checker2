import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from eccn_knowledge_base import suggest_eccn, format_response


def test_encryption_question_maps_to_5a002() -> None:
    result = suggest_eccn("AES 256 encryption router")
    assert result[0][0].code == "5A002"


def test_unknown_defaults_to_ear99() -> None:
    result = suggest_eccn("나무 책상 수출 분류")
    assert result[0][0].code == "EAR99"


def test_response_contains_required_sections() -> None:
    response = format_response("고주파 RF 증폭기 ECCN 알려줘")
    assert "추천 ECCN" in response
    assert "통제 사유" in response

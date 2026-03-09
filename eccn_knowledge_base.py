"""로컬 ECCN 지식베이스와 간단한 규칙 기반 매칭 로직."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
import re


@dataclass(frozen=True)
class ECCNEntry:
    code: str
    description: str
    reasons_for_control: tuple[str, ...]
    keywords: tuple[str, ...]
    follow_up_questions: tuple[str, ...]


ECCN_ENTRIES: tuple[ECCNEntry, ...] = (
    ECCNEntry(
        code="5A002",
        description="Information security 장비(암호 기능 포함)로 분류되는 항목입니다.",
        reasons_for_control=("NS", "AT", "EI"),
        keywords=("암호", "encryption", "crypto", "vpn", "aes", "rsa", "네트워크 보안"),
        follow_up_questions=(
            "암호화가 사용자 접근 가능한 기능인가요?",
            "정부 전용/군사용으로 특별 설계되었나요?",
            "오픈소스/대중 배포 예외(ENC)에 해당할 가능성이 있나요?",
        ),
    ),
    ECCNEntry(
        code="3A001",
        description="고성능 전자부품(특정 집적회로/ADC/DAC/증폭기 등) 관련 가능성이 있는 항목입니다.",
        reasons_for_control=("NS", "AT"),
        keywords=("반도체", "ic", "adc", "dac", "rf", "mmic", "고주파", "증폭기"),
        follow_up_questions=(
            "동작 주파수/대역폭/정밀도 사양은 어떻게 되나요?",
            "방사선 내성 또는 우주/군사용 등급인가요?",
            "데이터시트상의 성능 임계값이 3A001 기준을 초과하나요?",
        ),
    ),
    ECCNEntry(
        code="5A991",
        description="대중적 통신장비/전자장비로 분류되는 EAR99 인접 범주의 일반 항목 가능성이 있습니다.",
        reasons_for_control=("AT",),
        keywords=("라우터", "switch", "스위치", "무선", "wifi", "bluetooth", "일반 통신"),
        follow_up_questions=(
            "고급 암호 기능(5A002 수준)이 포함되어 있나요?",
            "군/우주/핵 관련 특별 사양이 있나요?",
            "최종사용자/최종용도가 민수용으로 명확한가요?",
        ),
    ),
    ECCNEntry(
        code="EAR99",
        description="CCL에 명시되지 않은 일반 상용 품목일 가능성이 있습니다.",
        reasons_for_control=("NLR(상황별 확인)",),
        keywords=("일반", "소모품", "부품", "consumer", "상용", "범용"),
        follow_up_questions=(
            "해당 품목이 CCL에 명시된 특정 성능을 만족하나요?",
            "원자력/미사일/군사용 최종용도와 연계되나요?",
            "제재 대상국/거래상대 여부를 스크리닝했나요?",
        ),
    ),
)


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9가-힣]+")


def tokenize(text: str) -> set[str]:
    return {tok.lower() for tok in TOKEN_PATTERN.findall(text)}


def score_entry(tokens: set[str], entry: ECCNEntry) -> int:
    score = 0
    for keyword in entry.keywords:
        key = keyword.lower()
        if " " in key:
            if key in " ".join(tokens):
                score += 2
        elif key in tokens:
            score += 2
        else:
            # 부분 매칭 (예: 암호화 vs 암호)
            if any(key in t or t in key for t in tokens if len(t) >= 2):
                score += 1
    return score


def suggest_eccn(question: str, top_n: int = 1) -> list[tuple[ECCNEntry, int]]:
    tokens = tokenize(question)
    ranked: list[tuple[ECCNEntry, int]] = []
    for entry in ECCN_ENTRIES:
        ranked.append((entry, score_entry(tokens, entry)))

    ranked.sort(key=lambda item: item[1], reverse=True)

    # 점수가 0이면 EAR99를 기본값으로 사용
    if not ranked or ranked[0][1] <= 0:
        fallback = next(e for e in ECCN_ENTRIES if e.code == "EAR99")
        return [(fallback, 0)]

    return ranked[:top_n]


def format_response(question: str) -> str:
    suggestion = suggest_eccn(question, top_n=1)[0]
    entry, score = suggestion

    matched_keywords = []
    tokens = tokenize(question)
    for kw in entry.keywords:
        k = kw.lower()
        if k in tokens or any(k in t or t in k for t in tokens):
            matched_keywords.append(kw)

    keyword_view = ", ".join(dict.fromkeys(matched_keywords[:5])) or "명확한 키워드 매칭 없음"

    lines: list[str] = [
        "[응답]",
        f"- 추천 ECCN: {entry.code}",
        f"- 신뢰도 점수(규칙 기반): {score}",
        f"- 근거 키워드: {keyword_view}",
        f"- 설명: {entry.description}",
        f"- 통제 사유: {', '.join(entry.reasons_for_control)}",
        "- 추가 확인 질문:",
    ]

    for idx, q in enumerate(entry.follow_up_questions, start=1):
        lines.append(f"  {idx}) {q}")

    lines.extend(
        [
            "",
            "※ 본 결과는 참고용 자동 분류 제안입니다. 최종 ECCN 판정은 규정 원문 및 내부 컴플라이언스 절차로 확인하세요.",
        ]
    )

    return "\n".join(lines)


def bulk_answer(questions: Iterable[str]) -> list[str]:
    return [format_response(q) for q in questions]

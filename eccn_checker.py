from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class ECCNEntry:
    eccn: str
    category: str
    description: str
    keywords: tuple[str, ...]
    reasons: tuple[str, ...]


DEFAULT_CATALOG: tuple[ECCNEntry, ...] = (
    ECCNEntry(
        eccn="3A001",
        category="전자장치",
        description="고성능 집적회로, ADC/DAC, 특정 주파수 특성의 반도체",
        keywords=("반도체", "집적회로", "adc", "dac", "고성능", "주파수"),
        reasons=("고성능 전자부품", "민감한 반도체 기술"),
    ),
    ECCNEntry(
        eccn="5A002",
        category="정보보안",
        description="암호 기능을 포함한 통신·보안 장비",
        keywords=("암호", "암호화", "encryption", "vpn", "보안", "통신"),
        reasons=("암호 기능 포함", "정보보안 통제품목 가능성"),
    ),
    ECCNEntry(
        eccn="9A610",
        category="항공우주/방산",
        description="군사용 항공우주 부품, 항공전자 장치",
        keywords=("군용", "방산", "항공전자", "항공우주", "무인기"),
        reasons=("군사 전용 또는 군사 파생 품목", "방산 관련 통제"),
    ),
    ECCNEntry(
        eccn="EAR99",
        category="일반품목",
        description="CCL에 명시되지 않은 일반 상용품",
        keywords=("일반", "상용", "소비자", "비민감"),
        reasons=("명시적 통제근거가 낮음", "추가 검토 필요"),
    ),
)

EMBARGOED_DESTINATIONS = {"북한", "이란", "시리아", "쿠바", "러시아", "belarus"}
MILITARY_END_USE_TERMS = {"군사용", "미사일", "핵", "weapon", "military"}


class ECCNChecker:
    def __init__(self, catalog: Iterable[ECCNEntry] | None = None) -> None:
        self.catalog = tuple(catalog or DEFAULT_CATALOG)

    @staticmethod
    def _normalize_text(*parts: str) -> str:
        return " ".join(parts).strip().lower()

    def _score(self, text: str, entry: ECCNEntry) -> tuple[float, list[str]]:
        hits = [kw for kw in entry.keywords if kw in text]
        score = len(hits) / max(len(entry.keywords), 1)

        reasons = []
        if hits:
            reasons.append(f"키워드 일치: {', '.join(hits)}")
        reasons.extend(entry.reasons)
        return score, reasons

    def classify(
        self,
        item_description: str,
        end_use: str = "",
        destination_country: str = "",
        top_n: int = 3,
    ) -> dict[str, Any]:
        text = self._normalize_text(item_description, end_use)
        destination = destination_country.lower().strip()

        matches: list[dict[str, Any]] = []
        for entry in self.catalog:
            score, reasons = self._score(text, entry)
            matches.append(
                {
                    "eccn": entry.eccn,
                    "category": entry.category,
                    "score": round(score, 3),
                    "reasons": reasons,
                }
            )

        matches.sort(key=lambda m: m["score"], reverse=True)

        flags: list[str] = []
        if destination in EMBARGOED_DESTINATIONS:
            flags.append(f"제재·우려국가 목적지: {destination_country}")
        if any(term in text for term in MILITARY_END_USE_TERMS):
            flags.append("군사/대량살상 관련 End-use 의심")

        recommended = matches[0]
        requires_review = bool(flags) or recommended["eccn"] != "EAR99"

        return {
            "input": {
                "item_description": item_description,
                "end_use": end_use,
                "destination_country": destination_country,
            },
            "recommended_eccn": recommended,
            "alternatives": matches[1:top_n],
            "compliance_flags": flags,
            "requires_human_review": requires_review,
            "disclaimer": "최종 ECCN 판정은 수출통제 전문가/법무 검토가 필요합니다.",
        }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ECCN 추천 및 수출통제 리스크 점검 도구")
    parser.add_argument("description", help="품목 설명")
    parser.add_argument("--end-use", default="", help="최종 사용처 설명")
    parser.add_argument("--destination", default="", help="목적지 국가")
    parser.add_argument("--output", default="", help="결과를 JSON 파일로 저장")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    checker = ECCNChecker()
    result = checker.classify(
        item_description=args.description,
        end_use=args.end_use,
        destination_country=args.destination,
    )

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

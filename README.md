# ECCN Checker

수출통제에서 중요한 ECCN(Export Control Classification Number) 후보를 빠르게 찾고,
목적지/최종용도 기반 리스크 플래그를 함께 점검하는 간단한 Python 시스템입니다.

## 기능
- 품목 설명 + End-use + 목적지 국가 입력
- ECCN 후보 점수화 및 추천(예: `3A001`, `5A002`, `9A610`, `EAR99`)
- 제재/우려국가 및 군사 용도 키워드 플래그
- JSON 결과 출력

## 실행
```bash
python eccn_checker.py "암호화 VPN 통신 장비" --end-use "기업 보안망" --destination "한국"
```

## 테스트
```bash
python -m unittest discover -s tests -v
```

## 주의
본 도구는 1차 스크리닝 자동화 용도이며, 최종 ECCN 판정은 반드시 전문 컴플라이언스/법무 검토가 필요합니다.

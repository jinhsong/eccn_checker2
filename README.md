# ECCN Checker

수출통제에서 중요한 ECCN(Export Control Classification Number) 후보를 빠르게 찾고,
목적지/최종용도 기반 리스크 플래그를 함께 점검하는 Python 시스템입니다.

## 핵심 기능
- **품목 설명, 모델명, 코드명, 부품코드**를 입력받아 ECCN 후보 추천
- 내부 식별자(모델/코드/Part Number)와 **직접 매핑**되는 경우 우선 ECCN 제시
- 제재/우려국가 및 군사 용도 키워드 플래그
- JSON 결과 출력

## 실행 예시
### 1) 품목 설명 기반
```bash
python eccn_checker.py "암호화 VPN 통신 장비" --end-use "기업 보안망" --destination "한국"
```

### 2) 모델명 기반 직접 조회
```bash
python eccn_checker.py --model "VPN-GW-X1" --destination "한국"
```

### 3) 부품코드 기반 직접 조회
```bash
python eccn_checker.py --part "ADC-HS-77" --destination "한국"
```

## 테스트
```bash
python -m unittest discover -s tests -v
```

## 운영 가이드
- `eccn_checker.py`의 `KNOWN_IDENTIFIERS`는 예시 데이터입니다.
- 실제 운영에서는 ERP/PLM/마스터 품목 DB와 연동하여 모델명/코드명/Part Number 기준 ECCN 매핑을 관리하세요.

## 주의
본 도구는 1차 스크리닝 자동화 용도이며, 최종 ECCN 판정은 반드시 전문 컴플라이언스/법무 검토가 필요합니다.

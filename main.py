"""ECCN 문의 응답 CLI 엔트리포인트."""

from eccn_knowledge_base import format_response


def main() -> None:
    print("ECCN 문의 응답 시스템 (오프라인 규칙 기반)")
    print("질문을 입력하세요. 종료하려면 'exit' 또는 'quit' 입력")

    while True:
        question = input("\n질문: ").strip()
        if not question:
            print("질문이 비어 있습니다. 다시 입력해 주세요.")
            continue

        if question.lower() in {"exit", "quit"}:
            print("종료합니다.")
            break

        print()
        print(format_response(question))


if __name__ == "__main__":
    main()

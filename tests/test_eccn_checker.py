import unittest

from eccn_checker import ECCNChecker


class ECCNCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checker = ECCNChecker()

    def test_security_product_maps_to_5a002(self) -> None:
        result = self.checker.classify(
            item_description="암호화 VPN 통신 장비",
            end_use="기업 보안 통신망",
            destination_country="한국",
        )
        self.assertEqual(result["recommended_eccn"]["eccn"], "5A002")
        self.assertTrue(result["requires_human_review"])

    def test_embargo_country_is_flagged(self) -> None:
        result = self.checker.classify(
            item_description="일반 상용 노트북",
            end_use="교육 목적",
            destination_country="이란",
        )
        self.assertTrue(result["compliance_flags"])
        self.assertTrue(result["requires_human_review"])


if __name__ == "__main__":
    unittest.main()

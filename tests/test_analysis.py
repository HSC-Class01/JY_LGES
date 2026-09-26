import unittest

from scripts.analyze import calculate


class RatioTests(unittest.TestCase):
    def test_annual_ratios_use_average_balances(self):
        base = {"report_code": "11011", "report_name": "사업보고서", "period_order": 4, "period_months": 12}
        first = {**base, "year": 2021, "revenue": 100.0, "cost_of_sales": 60.0, "gross_profit": 40.0,
                 "operating_income": 10.0, "net_income": 8.0, "current_assets": 50.0, "current_liabilities": 25.0,
                 "total_assets": 100.0, "total_liabilities": 40.0, "total_equity": 60.0,
                 "cash_and_cash_equivalents": 10.0, "accounts_receivable": 20.0, "inventory": 15.0,
                 "short_term_borrowings": 5.0, "long_term_borrowings": 15.0, "operating_cash_flow": 12.0,
                 "capex_ppe": -4.0, "capex_intangibles": -1.0}
        second = {**first, "year": 2022, "revenue": 120.0, "net_income": 12.0, "total_assets": 140.0,
                  "total_equity": 80.0, "accounts_receivable": 24.0, "inventory": 18.0}
        result = calculate([first, second])[1]
        self.assertAlmostEqual(result["revenue_growth_pct"], 20.0)
        self.assertAlmostEqual(result["roa_pct"], 10.0)
        self.assertAlmostEqual(result["free_cash_flow"], 7.0)


if __name__ == "__main__":
    unittest.main()

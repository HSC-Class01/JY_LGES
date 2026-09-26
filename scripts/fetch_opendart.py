"""LG에너지솔루션의 2021년 이후 OpenDART 정기공시와 재무제표를 수집한다."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import time
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = "https://opendart.fss.or.kr/api"
COMPANY = {"name": "LG에너지솔루션", "corp_code": "01515323", "stock_code": "373220"}
REPORTS = {"11013": ("1분기보고서", 1), "11012": ("반기보고서", 2), "11014": ("3분기보고서", 3), "11011": ("사업보고서", 4)}
REQUIRED = {"revenue", "operating_income", "net_income", "current_assets", "total_assets", "current_liabilities", "total_liabilities", "total_equity", "operating_cash_flow"}


def compact(value: str) -> str:
    return re.sub(r"[\s·ㆍ]", "", value or "").replace("(손실)", "")


def load_local_key() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def request_json(endpoint: str, params: dict[str, str], retries: int = 3) -> dict:
    url = f"{API}/{endpoint}?{urlencode(params)}"
    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": "LGES-DART-Agent/1.0"})
            with urlopen(req, timeout=60) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError) as error:
            if attempt == retries - 1:
                raise RuntimeError(f"OpenDART 요청 실패: {endpoint}: {error}") from error
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def amount(item: dict) -> int | None:
    key = "thstrm_amount" if item.get("sj_div") == "BS" else "thstrm_add_amount"
    raw = item.get(key) or item.get("thstrm_amount")
    if not raw or raw.strip() in {"-", ""}:
        return None
    try:
        return int(raw.replace(",", "").replace(" ", ""))
    except ValueError:
        return None


def score_candidate(item: dict, spec: dict) -> tuple[int, int, int]:
    exact_id = int(item.get("account_id") in spec.get("ids", []))
    exact_name = int(compact(item.get("account_nm", "")) in {compact(x) for x in spec.get("names", [])})
    statement = int(item.get("sj_div") == spec.get("statement"))
    return exact_id, exact_name, statement


def normalise(year: int, report_code: str, items: list[dict], accounts: dict) -> tuple[dict, list[str]]:
    report_name, period_order = REPORTS[report_code]
    row = {
        "year": year,
        "report_code": report_code,
        "report_name": report_name,
        "period_order": period_order,
        "period_months": period_order * 3,
        **{field: None for field in accounts},
    }
    for field, spec in accounts.items():
        candidates = [item for item in items if score_candidate(item, spec)[:2] != (0, 0)]
        candidates.sort(key=lambda item: score_candidate(item, spec), reverse=True)
        if candidates:
            row[field] = amount(candidates[0])
    missing = sorted(field for field in REQUIRED if row[field] is None)
    return row, missing


def list_filings(key: str, start_year: int) -> list[dict]:
    page, results = 1, []
    while True:
        data = request_json("list.json", {
            "crtfc_key": key,
            "corp_code": COMPANY["corp_code"],
            "bgn_de": f"{start_year}0101",
            "end_de": date.today().strftime("%Y%m%d"),
            "pblntf_ty": "A",
            "page_no": str(page),
            "page_count": "100",
        })
        if data.get("status") == "013":
            return results
        if data.get("status") != "000":
            raise RuntimeError(f"공시 목록 오류 {data.get('status')}: {data.get('message')}")
        results.extend(data.get("list", []))
        if page >= int(data.get("total_page", 1)):
            return results
        page += 1


def download_archives(key: str, filings: list[dict]) -> None:
    target = ROOT / "reports" / "source"
    target.mkdir(parents=True, exist_ok=True)
    for filing in filings:
        receipt = filing["rcept_no"]
        archive = target / f"{receipt}.zip"
        if archive.exists():
            continue
        url = f"{API}/document.xml?{urlencode({'crtfc_key': key, 'rcept_no': receipt})}"
        with urlopen(Request(url, headers={"User-Agent": "LGES-DART-Agent/1.0"}), timeout=120) as response:
            payload = response.read()
        if payload[:2] != b"PK":
            raise RuntimeError(f"{receipt}: 사업보고서 원문 ZIP 다운로드 실패")
        archive.write_bytes(payload)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="OpenDART 인증키. 생략하면 DART_API_KEY 환경변수를 사용합니다.")
    parser.add_argument("--start-year", type=int, default=2021)
    parser.add_argument("--skip-report-archives", action="store_true")
    args = parser.parse_args()
    if args.start_year < 2015:
        raise SystemExit("OpenDART 재무 API 제공 범위를 고려해 시작연도는 2015년 이후여야 합니다.")
    load_local_key()
    key = args.api_key or os.environ.get("DART_API_KEY")
    if not key:
        raise SystemExit("DART_API_KEY가 없습니다. API_KEY_SETUP.txt를 참고하세요.")

    accounts = json.loads((ROOT / "config" / "accounts.json").read_text(encoding="utf-8"))
    raw_dir = ROOT / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    rows, warnings = [], []
    for year in range(args.start_year, date.today().year + 1):
        for report_code, (report_name, _) in REPORTS.items():
            response = request_json("fnlttSinglAcntAll.json", {
                "crtfc_key": key,
                "corp_code": COMPANY["corp_code"],
                "bsns_year": str(year),
                "reprt_code": report_code,
                "fs_div": "CFS",
            })
            if response.get("status") == "013":
                continue
            if response.get("status") != "000":
                warnings.append(f"{year} {report_name}: {response.get('status')} {response.get('message')}")
                continue
            (raw_dir / f"lges_{year}_{report_code}.json").write_text(
                json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            row, missing = normalise(year, report_code, response.get("list", []), accounts)
            if missing:
                warnings.append(f"{year} {report_name}: 필수 계정 누락({', '.join(missing)}) — 기간 제외")
                continue
            rows.append(row)

    if not rows:
        raise RuntimeError("수집된 완전한 연결 재무제표가 없습니다.")
    rows.sort(key=lambda row: (row["year"], row["period_order"]))
    fields = ["year", "report_code", "report_name", "period_order", "period_months", *accounts]
    write_csv(ROOT / "data" / "financial_summary.csv", rows, fields)

    filings = list_filings(key, args.start_year)
    annual = [item for item in filings if "사업보고서" in item.get("report_nm", "")]
    annual.sort(key=lambda item: item.get("rcept_dt", ""))
    reports_dir = ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "opendart_disclosures.json").write_text(json.dumps({
        "company": COMPANY,
        "source_rss": "https://dart.fss.or.kr/api/companyRSS.xml?crpCd=01515323",
        "filings": annual,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    if not args.skip_report_archives:
        download_archives(key, annual)
    (ROOT / "data" / "fetch_warnings.json").write_text(
        json.dumps(warnings, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"수집 완료: 재무기간 {len(rows)}개, 사업보고서 {len(annual)}건, 경고 {len(warnings)}건")


if __name__ == "__main__":
    main()

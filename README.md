# LG에너지솔루션 OpenDART 재무 분석 대시보드

[![🔗 GitHub 대시보드 바로가기](https://img.shields.io/badge/%F0%9F%94%97-GitHub%20%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C-a50034?style=for-the-badge&logo=github)](https://hsc-class01.github.io/JY_LGES/)

LG에너지솔루션(종목코드 `373220`, DART 고유번호 `01515323`)의 2021년 이후 연결 재무제표와 사업보고서 원문을 OpenDART에서 수집하고, 핵심 재무비율을 계산해 대시보드로 보여줍니다.

## 제공 기능

- 2021년부터 사업보고서·분기·반기·3분기 연결 재무제표 수집
- 사업보고서 원문 ZIP, API 원문 JSON, 공시 목록을 GitHub에 누적 보관
- 매출 성장률, 매출총이익률, 영업이익률, 순이익률, ROA, ROE, 유동·당좌비율, 부채비율, 자산·재고 회전율, DSO, CFO 전환율, CAPEX, FCF 분석
- 매월 1일 09:00 KST 자동 수집 및 분석 데이터 갱신
- GitHub Pages에서 제공되는 모바일 대응 정적 대시보드

## 5분 설정

1. [OpenDART](https://opendart.fss.or.kr/)에서 API 인증키를 발급받습니다.
2. GitHub Actions 워크플로는 `.github/workflows/update-and-deploy.yml`에 이미 포함되어 있으므로 별도 복사 과정이 필요 없습니다.
3. 현재 저장소는 `HSC-Class01/JY_LGES`입니다. 로컬에서 새 사본을 올리는 경우에도 이 저장소를 원격으로 사용하세요.
4. 저장소 **Settings → Secrets and variables → Actions**에 `DART_API_KEY` 이름으로 인증키를 등록합니다. 자세한 내용은 `API_KEY_SETUP.txt`를 확인하세요.
5. **Settings → Pages → Build and deployment → Source**에서 `GitHub Actions`를 선택합니다.
6. **Actions → Update OpenDART data and deploy dashboard → Run workflow**를 실행합니다.

GitHub CLI에 로그인되어 있다면 `./publish_to_github.ps1`로 로컬 사본을 `HSC-Class01/JY_LGES`에 올릴 수 있습니다. 인증키는 보안을 위해 이 스크립트가 입력받지 않으며 GitHub Secret 화면에서 직접 등록합니다.

## 저장소 About 링크

저장소 우측 **About → ⚙ → Website**에는 아래 GitHub Pages 주소를 입력합니다.

`https://hsc-class01.github.io/JY_LGES/`

대시보드는 GitHub Pages에만 배포됩니다. ChatGPT Sites 또는 별도의 GPT 대시보드는 사용하지 않습니다.

## 로컬 실행

```powershell
Copy-Item env.example.txt .env
# .env에 DART_API_KEY 입력
python scripts/fetch_opendart.py --start-year 2021
python scripts/analyze.py
python -m unittest discover -s tests -v
python -m http.server 8000
```

브라우저에서 `http://localhost:8000`을 엽니다. 계정 항목을 추가하려면 `config/accounts.json`에 한글 계정명과 XBRL ID를 추가하면 됩니다.

## 데이터 구조

- `data/raw/`: OpenDART 전체 재무제표 API 원문
- `data/financial_summary.csv`: 분석용 정규화 재무수치
- `data/ratios.csv`: 계산된 재무비율
- `data/dashboard.json`: GitHub Pages 대시보드용 통합 데이터
- `reports/source/`: 사업보고서 원문 ZIP
- `reports/opendart_disclosures.json`: 사업보고서 공시 목록

## 유의사항

계정과목 표기는 회사의 XBRL 작성 방식에 따라 달라질 수 있습니다. 수집 경고는 `data/fetch_warnings.json`에 남습니다. 분기 수치는 누적일 수 있으며 연간 비교와 섞지 않습니다. 본 프로젝트는 정보 제공용이며 투자 권유가 아닙니다.


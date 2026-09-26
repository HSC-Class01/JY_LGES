# ChatGPT 연결 방법

공식 OpenAI 정책상 새 GPT 생성·공개 가능 여부는 계정과 워크스페이스 권한에 따라 달라집니다. 생성 권한이 있는 Business/Enterprise/Edu 워크스페이스에서는 다음과 같이 설정합니다.

1. ChatGPT의 GPTs 영역에서 새 GPT를 만듭니다.
2. 이름을 `LG에너지솔루션 DART 재무분석`으로 지정합니다.
3. `INSTRUCTIONS.md` 전체를 Instructions에 붙여 넣습니다.
4. GitHub 자동 수집 후 생성된 `data/dashboard.json`, `data/financial_summary.csv`, `data/ratios.csv`를 Knowledge에 올립니다.
5. Code Interpreter & Data Analysis를 활성화하고 Preview에서 테스트합니다.
6. 공유 가능한 링크가 생성되면 `dashboard-config.js`의 `chatgptUrl`과 README의 ChatGPT 링크를 해당 주소로 바꿉니다.

개인 계정에서 새 GPT 생성이 제공되지 않는 경우에는 배포된 웹 대시보드를 사용하고, CSV/JSON을 일반 ChatGPT 대화에 첨부하여 `INSTRUCTIONS.md`의 분석 원칙을 함께 전달하면 됩니다.

"""숨김 파일/폴더를 제외한 업로드용 ZIP을 재현 가능하게 생성한다."""
from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parent / "Dart_LGES_agent.zip"


def hidden(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return any(part.startswith(".") or part == "__pycache__" for part in parts) or path.suffix in {".pyc", ".pyo"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output.resolve()
    files = [p for p in ROOT.rglob("*") if p.is_file() and not hidden(p) and p.resolve() != output]
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in sorted(files):
            relative = Path(ROOT.name) / path.relative_to(ROOT)
            info = ZipInfo(str(relative).replace("\\", "/"), date_time=(2021, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    print(f"ZIP 생성: {output} ({len(files)} files)")


if __name__ == "__main__":
    main()

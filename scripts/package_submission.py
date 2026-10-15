"""Create and verify a source/evidence archive without local databases or credentials."""

import hashlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "artifacts" / "routepulse-wild-bugs.zip"
EXCLUDED = {
    "node_modules",
    ".next",
    "__pycache__",
    ".venv",
    ".git",
    ".codex",
    ".agents",
    "test-results",
    "playwright-report",
}
ROOT_FILES = [
    "README.md",
    "AGENTS.md",
    "docker-compose.yml",
    "pyproject.toml",
    ".env.example",
    ".gitignore",
    ".dockerignore",
]
FOLDERS = [
    "services/api",
    "apps/web",
    "scripts",
    "docs",
    "submission",
    ".github/workflows",
    "data/experiments/20261014T091653Z",
    "data/research",
]


def permitted(path: Path) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and not EXCLUDED.intersection(path.parts)
        and path.name not in {".env", ".DS_Store", "tsconfig.tsbuildinfo"}
        and not path.name.startswith(".env.")
        and path.suffix not in {".db", ".pyc", ".zip"}
    )


def build() -> None:
    required = [
        "submission/demo/routepulse-demo.webm",
        "submission/demo/recording.json",
        "submission/demo/recorded-validation.json",
        "submission/EVENT_REQUIREMENTS.md",
    ]
    for name in required:
        if not (ROOT / name).is_file():
            raise SystemExit(f"Missing submission artifact: {name}")
    files = {ROOT / name for name in ROOT_FILES}
    files.add(ROOT / "data/openapi.json")
    for folder in FOLDERS:
        for directory, directories, names in __import__("os").walk(ROOT / folder):
            directories[:] = [name for name in directories if name not in EXCLUDED]
            files.update(p for name in names if permitted(p := Path(directory) / name))
    files = sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())
    if any(not p.is_file() for p in files):
        raise SystemExit("A required source file is missing")
    manifest = "".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n" for p in files
    )
    DESTINATION.parent.mkdir(exist_ok=True)
    with ZipFile(DESTINATION, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, "RoutePulse/" + path.relative_to(ROOT).as_posix())
        archive.writestr("RoutePulse/MANIFEST.sha256", manifest)
    with ZipFile(DESTINATION) as archive:
        assert archive.testzip() is None, "Archive CRC verification failed"
        for row in manifest.splitlines():
            digest, name = row.split("  ", 1)
            assert hashlib.sha256(archive.read("RoutePulse/" + name)).hexdigest() == digest, name
        assert all(not any(part in EXCLUDED for part in Path(name).parts) for name in archive.namelist())
        assert all(Path(name).name != ".env" and not name.endswith(".db") for name in archive.namelist())
    digest = hashlib.sha256(DESTINATION.read_bytes()).hexdigest()
    DESTINATION.with_suffix(".zip.sha256").write_text(f"{digest}  {DESTINATION.name}\n")
    print(f"Verified {len(files)} source/evidence files and every SHA-256 entry.")
    print(f"Archive: {DESTINATION} ({DESTINATION.stat().st_size:,} bytes)")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    build()

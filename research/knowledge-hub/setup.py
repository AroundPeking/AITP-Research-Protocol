from __future__ import annotations

from pathlib import Path
import runpy
import shutil

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py

ROOT = Path(__file__).parent
VERSION_MODULE = runpy.run_path(str(ROOT / "knowledge_hub" / "_version.py"))
BUNDLE_MODULE = runpy.run_path(str(ROOT / "knowledge_hub" / "bundle_support.py"))
PACKAGE_DISTRIBUTION_NAME = str(BUNDLE_MODULE["PACKAGE_DISTRIBUTION_NAME"])
BUILD_BUNDLE_TREE = BUNDLE_MODULE["build_bundle_tree"]
ITER_BUNDLE_SOURCE_FILES = BUNDLE_MODULE["iter_bundle_source_files"]
PACKAGE_VERSION = str(VERSION_MODULE["__version__"])
BUNDLE_PACKAGE_DATA = [
    str(Path("_bundle") / relative_path).replace("\\", "/")
    for _, relative_path in ITER_BUNDLE_SOURCE_FILES(ROOT)
]
README = (ROOT / "README.md").read_text(encoding="utf-8")
REQUIREMENTS = [
    line.strip()
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
]


class BuildPyWithKernelBundle(build_py):
    def run(self) -> None:
        super().run()
        package_root = Path(self.build_lib) / "knowledge_hub"
        bundle_root = package_root / "_bundle"
        BUILD_BUNDLE_TREE(ROOT, bundle_root)
        stale_root = package_root / "__pycache__"
        if stale_root.exists():
            shutil.rmtree(stale_root)


setup(
    name=PACKAGE_DISTRIBUTION_NAME,
    version=PACKAGE_VERSION,
    author="Bohan Jia",
    description="AITP runtime CLI, MCP server, and agent bootstrap assets",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bhjia-phys/AITP-Research-Protocol",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    python_requires=">=3.10",
    install_requires=REQUIREMENTS,
    extras_require={
        "paperqa": [
            "paper-qa; python_version>='3.11'",
        ],
    },
    cmdclass={"build_py": BuildPyWithKernelBundle},
    entry_points={
        "console_scripts": [
            "aitp=knowledge_hub.aitp_cli:main",
            "aitp-mcp=knowledge_hub.aitp_mcp_server:main",
            "aitp-codex=knowledge_hub.aitp_codex:main",
        ]
    },
    include_package_data=True,
    package_data={"knowledge_hub": BUNDLE_PACKAGE_DATA},
    zip_safe=False,
)

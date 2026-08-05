"""Smoke tests for the packaged theme.

These guard the failure modes that are *silent* — a theme that installs fine,
builds fine, reports success, and quietly renders as stock Zensical.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "stridelabs_docs_theme"


# --------------------------------------------------------------------------
# Packaging
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rel",
    ["__init__.py", "mkdocs_theme.yml", "main.html", "css/stridelabs.css", "partials/logo.html"],
)
def test_asset_present_in_package(rel: str) -> None:
    """Every non-Python asset must ship. A wheel missing these installs and
    builds cleanly while silently falling back to the stock theme."""
    assert (PKG / rel).is_file(), f"missing theme asset: {rel}"


def test_entry_point_declared() -> None:
    """`theme.name = "stridelabs"` resolves through this entry point."""
    pyproject = (PKG.parent / "pyproject.toml").read_text()
    assert '[project.entry-points."mkdocs.themes"]' in pyproject
    assert 'stridelabs = "stridelabs_docs_theme"' in pyproject


# --------------------------------------------------------------------------
# The scheme-name trap
# --------------------------------------------------------------------------


def test_stylesheet_targets_stock_scheme_names() -> None:
    """Zensical defines 14 --md-code-hl-* syntax variables under
    [data-md-color-scheme=slate] and zero under "default". A custom scheme
    name orphans all 14 and dark mode renders light-mode syntax colours on a
    dark ground — illegible code, clean build. Tokens must therefore layer on
    top of the stock names."""
    css = (PKG / "css" / "stridelabs.css").read_text()
    assert '[data-md-color-scheme="slate"]' in css
    assert '[data-md-color-scheme="default"]' in css
    assert "stridelabs-dark" not in css, "custom scheme name would orphan slate's syntax vars"


def test_theme_config_uses_stock_scheme_names() -> None:
    config = (PKG / "mkdocs_theme.yml").read_text()
    assert "scheme: default" in config
    assert "scheme: slate" in config


# --------------------------------------------------------------------------
# The font-loading trap
# --------------------------------------------------------------------------


def test_display_font_is_actually_loaded() -> None:
    """The stylesheet sets headings in Fraunces, but Zensical's font.text /
    font.code settings only fetch two families. Fraunces must be requested
    explicitly or headings silently fall back to Georgia."""
    css = (PKG / "css" / "stridelabs.css").read_text()
    if "Fraunces" not in css:
        pytest.skip("stylesheet no longer uses Fraunces")
    head = (PKG / "main.html").read_text()
    assert "family=Fraunces" in head, "Fraunces used in CSS but never loaded"


# --------------------------------------------------------------------------
# End-to-end build
# --------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("zensical") is None, reason="zensical not on PATH")
def test_builds_and_applies_theme() -> None:
    """Build a throwaway site against the installed theme and assert the
    theme's own markup reached the output."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir()
        (root / "docs" / "index.md").write_text("# Smoke\n\nBody text.\n")
        (root / "zensical.toml").write_text(
            '[project]\nsite_name = "Smoke"\ndocs_dir = "docs"\nsite_dir = "out"\n\n'
            '[project.theme]\nname = "stridelabs"\n\n'
            '[project.theme.icon]\nlogo = "material/console"\n'
        )
        proc = subprocess.run(
            [sys.executable, "-m", "zensical", "build", "--clean", "--strict"],
            cwd=root,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(PKG.parent)},
        )
        assert proc.returncode == 0, proc.stderr or proc.stdout

        html = (root / "out" / "index.html").read_text()
        assert "css/stridelabs.css" in html, "theme stylesheet not linked"
        assert (root / "out" / "css" / "stridelabs.css").is_file(), "stylesheet not copied"
        assert "sl-lockup" in html, "owl lockup partial did not override"
        assert "sl-owl-eye" in html, "owl mark missing"
        assert "sl-proj" in html, "per-project icon slot missing"
        assert "family=Fraunces" in html, "display font not loaded"

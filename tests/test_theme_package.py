"""Smoke tests for the packaged theme.

These guard the failure modes that are *silent* — a theme that installs fine,
builds fine, reports success, and quietly renders as stock Zensical.
"""

from __future__ import annotations

import os
import re
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
    [
        "__init__.py",
        "mkdocs_theme.yml",
        "main.html",
        "css/stridelabs.css",
        "css/fonts.css",
        "partials/logo.html",
        "fonts/OFL.txt",
    ],
)
def test_asset_present_in_package(rel: str) -> None:
    """Every non-Python asset must ship. A wheel missing these installs and
    builds cleanly while silently falling back to the stock theme."""
    assert (PKG / rel).is_file(), f"missing theme asset: {rel}"


def test_font_files_present() -> None:
    """woff2 files are what `@font-face` in fonts.css points at. If the wheel
    drops them the site renders in fallback faces with no error anywhere."""
    woff2 = sorted((PKG / "fonts").glob("*.woff2"))
    assert woff2, "no font files shipped"
    declared = (PKG / "css" / "fonts.css").read_text()
    for f in woff2:
        assert f.name in declared, f"{f.name} shipped but never referenced"
    for name in re.findall(r'url\("\.\./fonts/([^"]+)"\)', declared):
        assert (PKG / "fonts" / name).is_file(), f"fonts.css references missing {name}"


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


def test_display_font_is_actually_declared() -> None:
    """The stylesheet sets headings in Fraunces. Zensical's own font loader
    only ever fetches two families, so a display face must come from the
    theme's own @font-face rules or headings silently fall back to Georgia."""
    css = (PKG / "css" / "stridelabs.css").read_text()
    if "Fraunces" not in css:
        pytest.skip("stylesheet no longer uses Fraunces")
    fonts = (PKG / "css" / "fonts.css").read_text()
    assert 'font-family: "Fraunces"' in fonts, "Fraunces used but never declared"


def _strip_comments(text: str) -> str:
    """Drop CSS and Jinja comments — the files discuss the Google Fonts CDN in
    prose, and a naive substring search would flag their own documentation."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"\{#-?.*?-?#\}", "", text, flags=re.S)


def test_no_third_party_font_requests() -> None:
    """Self-hosting is the point: no font may be fetched from a third party."""
    config = (PKG / "mkdocs_theme.yml").read_text()
    assert re.search(r"^font: false$", config, re.M), (
        "Zensical's built-in Google Fonts <link> must be disabled"
    )
    for rel in ("main.html", "css/fonts.css", "css/stridelabs.css"):
        body = _strip_comments((PKG / rel).read_text())
        for host in ("fonts.googleapis.com", "fonts.gstatic.com"):
            assert host not in body, f"{rel} still fetches from {host}"


def test_all_font_sources_are_relative() -> None:
    """Every @font-face src must point at a bundled file, not a URL."""
    fonts = _strip_comments((PKG / "css" / "fonts.css").read_text())
    srcs = re.findall(r"src:\s*url\(([^)]+)\)", fonts)
    assert srcs, "no @font-face src rules found"
    for s in srcs:
        assert s.strip('"').startswith("../fonts/"), f"non-bundled font source: {s}"


# --------------------------------------------------------------------------
# The mobile-drawer lockup trap
# --------------------------------------------------------------------------


def _rules_for(css: str, needle: str) -> list[str]:
    """Return the selector text of every rule whose selector contains needle."""
    return [
        m.group(1).strip()
        for m in re.finditer(r"([^{}]+)\{[^}]*\}", _strip_comments(css))
        if needle in m.group(1)
    ]


def test_drawer_lockup_overrides_present() -> None:
    """Zensical sizes the drawer's logo slot for a single glyph
    (`.md-nav__title[for=__drawer] .md-logo { width: 1.6rem; height: 1.6rem }`).
    The lockup is roughly 3.8rem wide with `flex: none` parts, so without an
    override it overflows and paints on top of the site title — which renders
    fine at desktop width and only breaks behind the hamburger menu."""
    css = (PKG / "css" / "stridelabs.css").read_text()
    selectors = _rules_for(css, '[for="__drawer"]')
    assert selectors, "no drawer overrides at all — the lockup will overlap the title"

    slot = [s for s in selectors if s.rstrip().endswith(".md-logo")]
    assert slot, "the drawer's .md-logo slot is never resized"


def test_drawer_svg_overrides_outspecify_zensical() -> None:
    """Zensical also ships
    `.md-nav .md-nav__title[for=__drawer] .md-logo svg { height: 100% }`.
    Our svg overrides must be at least as specific or the owl and project icon
    get stretched to the slot height. Both must lead with `.md-nav `, which is
    what supplies the extra class needed to win."""
    css = (PKG / "css" / "stridelabs.css").read_text()
    svg_rules = [
        s
        for s in _rules_for(css, '[for="__drawer"]')
        if "svg" in s and ".md-logo" in s
    ]
    assert svg_rules, "no drawer svg sizing overrides found"
    for sel in svg_rules:
        assert sel.lstrip().startswith(".md-nav "), (
            f"drawer svg override {sel!r} is less specific than Zensical's own "
            "rule and will silently lose"
        )


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

        # fonts: declared, shipped, and served from our own origin
        assert "css/fonts.css" in html, "font stylesheet not linked"
        assert (root / "out" / "css" / "fonts.css").is_file(), "fonts.css not copied"
        shipped = list((root / "out" / "fonts").glob("*.woff2"))
        assert shipped, "no woff2 files copied into the built site"
        for host in ("fonts.googleapis.com", "fonts.gstatic.com"):
            assert host not in html, f"built page still calls out to {host}"

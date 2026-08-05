# Changelog

All notable changes to this project will be documented in this file.

## v0.2.1

### Fixed

- **Narrowed an over-broad privacy claim.** v0.2.0's wording implied a site
  built with this theme makes no third-party requests at all. It removes the
  *font* requests; a site that sets `repo_url` still has Zensical's repo
  integration calling `api.github.com` for star and fork counts. Caught in
  review on charliek/prox#104. Documentation only — no behaviour change.

## v0.2.0

### Changed

- **Fonts are now self-hosted.** `font: false` disables Zensical's built-in
  Google Fonts `<link>` and the package ships Fraunces, Inter and JetBrains
  Mono as woff2. No font requests reach `fonts.googleapis.com` or
  `fonts.gstatic.com`, so the Google Fonts CDN never sees a visitor IP — the
  GDPR concern behind Zensical's own `font: false` option — and pages render
  identically offline and behind a firewall.

  Variable fonts split by `unicode-range`, so a browser fetches only what a
  page uses. Verified on a real page: 18 requests, none to a third-party
  host, 3 woff2 files (latin subsets only; latin-ext and italic are not
  fetched unless those glyphs appear).

  This also removes a redundancy that existed in v0.1.0: Zensical's loader
  fetches exactly two families, so the Fraunces display face required a
  *second* `<link>` to Google on every page. Both are now gone.

  All three families are SIL OFL 1.1; licence texts ship in
  `stridelabs_docs_theme/fonts/OFL.txt`.

### Notes

Two new tests guard this, since a missing font is a silent failure — the page
renders in a fallback face and the build still reports success:
`test_no_third_party_font_requests` and `test_all_font_sources_are_relative`.

## v0.1.0

Initial release. The StrideLabs documentation theme, packaged so it can be
shared across every Zensical docs site without copying CSS between repos.

### Added

- **Packaged Zensical theme** exposed as `theme.name = "stridelabs"` via the
  `mkdocs.themes` entry point. Installs as a plain git dependency — no PyPI,
  no registry, no credentials, so public repos and forks can build docs
  unchanged.
- **Header lockup**: the StrideLabs owl as the family mark, a hairline rule,
  then the consuming project's own icon (`[project.theme.icon] logo`). One
  glance says both "this is StrideLabs" and "this is prox".
- **Light and dark schemes.** stridelabs.ai is light-only; docs readers expect
  a toggle, so the dark half is derived from the brand's deep forest
  (`#161c16` ground) rather than invented.
- **Readability-first light scheme.** The site's parchment (`#f5efdf`) is used
  for code panels and accents, not for body text, which sits on a near-white
  `#fdfcf8` ground. Code blocks read as deliberate panels instead of blending
  into the page.
- Editorial detailing carried over from the site: Fraunces display / Inter
  body / JetBrains Mono code, a heavy rule under `h1` and a hairline under
  `h2`, mono uppercase kickers in the sidebar and table headers, rust links,
  and gold focus rings in both schemes.
- Defaults for the nine feature toggles the fleet had standardised on, so
  consuming repos stop repeating them.

### Notes for anyone extending this

Two failure modes here are silent — they build clean and report success:

- **Scheme names.** Zensical defines 14 `--md-code-hl-*` syntax-highlight
  variables under `[data-md-color-scheme=slate]` and none under `default`.
  Naming a custom scheme orphans all 14, and dark mode renders light-mode
  syntax colours on a dark ground. This theme layers its tokens on top of the
  stock `default` / `slate` names instead. Covered by a test.
- **Font loading.** `font.text` / `font.code` fetch exactly two families, so
  the Fraunces display face has to be requested explicitly in `main.html` or
  headings quietly fall back to Georgia. Also covered by a test.

Built against Zensical 0.0.52, which is pre-1.0.

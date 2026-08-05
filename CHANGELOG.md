# Changelog

All notable changes to this project will be documented in this file.

## v0.2.2

### Fixed

- **The header lockup overlapped the site title in the mobile drawer.** Zensical
  sizes the drawer's logo slot for a single glyph
  (`.md-nav__title[for=__drawer] .md-logo { width: 1.6rem; height: 1.6rem }`).
  The lockup is roughly 3.8rem wide and its parts are `flex: none`, so they
  overflowed that box and painted on top of the site name sitting beside it —
  the divider and project icon landed mid-word. The slot now sizes to its
  content.

  This only ever showed **behind the hamburger menu on narrow viewports**. Every
  desktop check passed, which is why it shipped in v0.1.0 and survived four
  repos. Reported from a phone.

  The `svg` overrides carry extra specificity on purpose: Zensical also ships
  `.md-nav .md-nav__title[for=__drawer] .md-logo svg { height: 100% }`, which
  would otherwise stretch both the owl and the project icon to the slot height.

  Verified at 412px and 360px, light and dark, including a site name long
  enough to wrap (`shed-remote-agent`) — it wraps cleanly instead of pushing
  the lockup out of its slot.

- **CI's `consume` job had been failing since v0.2.0.** Its last assertion was
  `grep -q 'family=Fraunces'` — the Google Fonts `<link>` that self-hosting
  removed in v0.2.0. The job was never updated, so it went red on that release
  and stayed red through v0.2.1. It now asserts what self-hosting actually
  means: `css/fonts.css` linked and present, woff2 files copied into the site,
  and **no** request to `fonts.googleapis.com` / `fonts.gstatic.com`. It also
  asserts the drawer overrides survive into the shipped CSS.

### Notes

Two tests guard the drawer fix, both confirmed to fail when the override is
removed. They assert on selector *specificity*, not just presence, because a
correct-looking rule that silently loses the cascade is the same bug wearing a
hat.

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

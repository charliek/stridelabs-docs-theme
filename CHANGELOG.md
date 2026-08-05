# Changelog

All notable changes to this project will be documented in this file.

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

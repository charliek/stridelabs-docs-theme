# stridelabs-docs-theme

The shared [StrideLabs](https://www.stridelabs.ai) documentation theme for
[Zensical](https://zensical.org) sites — one package, so ~24 repos look like
one family without copy-pasting CSS into each of them.

Ported from the stridelabs.ai "Gazette" identity: deep forest green, warm ink,
rust and gold accents, Fraunces / Inter / JetBrains Mono, and the owl as the
family mark.

## Install

No PyPI, no registry auth — it installs straight from this public repo.

```toml
# pyproject.toml
[dependency-groups]
docs = [
    "zensical>=0.0.52",
    "stridelabs-docs-theme",
]

[tool.uv.sources]
stridelabs-docs-theme = { git = "https://github.com/charliek/stridelabs-docs-theme", tag = "v0.2.1" }
```

```toml
# zensical.toml
[project.theme]
name = "stridelabs"

# the icon that says *which* tool this is — shown beside the owl
[project.theme.icon]
logo = "material/console"
```

Then `uv sync --group docs`. That's the whole adoption cost: two config
blocks, no CI changes, no credentials, nothing to install on a dev machine.

`uv.lock` records the resolved commit SHA alongside the tag, so builds are
reproducible and `uv sync --locked` works in CI unchanged.

### Upgrading

Bump the `tag` and re-lock. To move the whole fleet, bump the tag in each
repo — the CSS itself never gets copied anywhere, so there is no drift to
reconcile.

## What the theme provides

Everything below is a **default**. Anything in a consuming repo's
`zensical.toml` wins.

| | |
|---|---|
| **Header** | owl (family mark) + hairline rule + your project icon |
| **Type** | Fraunces display, Inter body, JetBrains Mono code — **self-hosted**, no third-party requests |
| **Light** | near-white `#fdfcf8` reading ground, parchment code panels |
| **Dark** | `#161c16` ground derived from the brand's deep forest |
| **Detailing** | 3px rule under `h1`, hairline under `h2`, mono uppercase kickers in the sidebar and table headers |
| **Accents** | rust links, forest headings, gold focus rings in both schemes |
| **Features** | the nine feature toggles the fleet standardised on |

### Picking your project icon

`[project.theme.icon] logo` accepts any icon from the sets Zensical ships:
`material`, `lucide`, `fontawesome`, `octicons`, `simple`. The owl stays
constant; this icon is what distinguishes one site from the next.

## Fonts

The theme sets `font: false`, which disables Zensical's built-in Google Fonts
`<link>`, and ships the three families itself as woff2. Nothing is fetched
from `fonts.googleapis.com` or `fonts.gstatic.com`.

Why self-host:

- **Privacy.** The Google Fonts CDN sees every visitor's IP. That is the
  GDPR concern behind Zensical's own `font: false` escape hatch, and it is
  worth avoiding by default across two dozen public sites.

  Scope note: this removes the *font* requests. A site that sets `repo_url`
  still has Zensical's repo integration calling `api.github.com` for star and
  fork counts, which is a separate opt-out (drop `repo_url`).
- **Performance.** One origin, so no extra DNS lookup and TLS handshake
  before the first paint.
- **Reliability.** Docs build and render identically offline, behind a
  firewall, and if the CDN is having a bad day.
- **It was always going to need two requests.** Zensical's font loader
  fetches exactly two families, so a display face on top of body + code
  already meant a second `<link>` to Google. Self-hosting removes both.

These are **variable** fonts (one file spans the whole weight range), split
by `unicode-range`, so a browser downloads only what a page uses. Verified on
a real page: 3 files, latin subsets only — the latin-ext and italic variants
are not fetched unless the glyphs appear.

All three families are SIL Open Font License 1.1, which permits
redistribution; the licence texts ship in `stridelabs_docs_theme/fonts/OFL.txt`.

### Changing the fonts

Edit `css/fonts.css` and the `@font-face` blocks together — the stylesheet
sets `--md-text-font` / `--md-code-font` as variables (not `font-family`) so
the theme's system fallbacks still apply. A test asserts that every face the
CSS asks for is actually declared and bundled, because a missing font is a
silent failure: the page renders in a fallback and the build still passes.

## Design notes

**Readability is the constraint.** The site itself uses a parchment ground
(`#f5efdf`); the theme deliberately does not. Parchment is reserved for code
panels and accents so body text sits on the highest-contrast surface — these
are reference docs people keep open for an hour, not a landing page. The
result is that code blocks read as deliberate panels rather than blending in.

**The site has no dark mode; this theme does.** Docs readers expect one. The
dark half is derived from the brand's own deep forest and warm ink rather
than invented from scratch.

### The trap this theme exists to avoid

Zensical defines **14 `--md-code-hl-*`** syntax-highlight variables under
`[data-md-color-scheme=slate]` and **zero** under `default`. Naming a custom
scheme (`stridelabs-dark`, say) silently orphans all 14 — dark mode then
renders *light-mode* syntax colours on a dark ground. Code becomes nearly
illegible, and the build still reports success.

So this theme layers its tokens **on top of** the stock `default` and `slate`
schemes rather than replacing them. If you fork or extend the stylesheet,
keep those selector names.

## Extending it in one repo

Set `custom_dir` and **extend** `main.html` rather than redefining it —
redefining drops the stylesheet link:

```jinja
{% extends "main.html" %}
{% block extrahead %}
  {{ super() }}
  <link rel="stylesheet" href="{{ 'stylesheets/local.css' | url }}">
{% endblock %}
```

To opt a repo out of the new look entirely, `variant = "classic"` restores
the Material for MkDocs appearance.

## Source of truth

The templates and defaults track **[charliek/prox](https://github.com/charliek/prox)**,
the reference implementation (migrated in prox plan 025, PR #103). If prox's
docs setup changes, update this package to match — nothing enforces that
automatically.

Written against **Zensical 0.0.52**, which is pre-1.0 and moves quickly.
Re-verify against the current release before adopting on a new repo.

## Licence

MIT.

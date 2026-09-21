# SkillSetu — Color Theme & Design System

Extracted from the existing SkillSetu landing page prototype (hero + role-selection modal)
so every new screen stays visually consistent with what's already built.

## Color palette

| Token | Hex | Use |
|---|---|---|
| `--ink` | `#16232B` | Primary text, headings |
| `--teal` | `#175E6C` | Primary brand color — buttons, links, active nav, chart lines, icons |
| `--teal-deep` | `#0E4650` | Sidebar/nav background, hover/pressed states |
| `--teal-tint` | `#E4EEEE` | Light backgrounds behind teal icons, progress-track background, "Applied" status chip |
| `--bg` | `#FAF7F2` | Page background (warm off-white, not stark white) |
| `--surface` | `#FFFFFF` | Card / panel background |
| `--border` | `#E8E2D8` | Card borders, dividers (warm light gray-tan, not cool gray) |
| `--clay` | `#E2A46F` | Secondary accent — one deliberate highlight per screen (active-nav dot, one skill bar, "Shortlisted" status, avatar badge). Don't overuse. |
| `--clay-tint` | `#FBEADA` | Background behind clay-accented chips |
| `--sage` | `#4E8C79` | Positive/success states ("Selected" status, trust score) |
| `--sage-tint` | `#E1EFE8` | Background behind sage chips |
| `--danger` | `#B14A38` | Negative states ("Rejected" status) — warm red, not a default alert red, to stay in the brand's warm-cool family |
| `--danger-tint` | `#F7E4E0` | Background behind danger chips |
| `--muted` | `#6B7680` | Secondary/supporting text |

**Rule of thumb:** teal carries the interface (nav, actions, primary data). Clay is the one
accent color and should never compete with teal for attention — use it for exactly one
highlighted thing per screen (an active state, one bar, one badge), the same restraint
already visible in the landing page (teal button, single clay figure in the hero
illustration).

## Typography

**Poppins** — the same geometric sans already used in the landing page headline
("ACADEMIA · INDUSTRY"). Used for everything (headings and body) at different weights,
so no second typeface is needed:

| Weight | Use |
|---|---|
| SemiBold / Bold (600–700) | Page titles, card titles, key numbers (fit %, skill scores) |
| Medium (500) | Nav items, labels, buttons, status chips |
| Regular (400) | Body copy, descriptions |
| Light (300) | Rarely — large decorative numerals only, if ever |

Keep UI text sentence case, not all-caps — the landing page uses caps only for its
top-nav (HOME / FEATURES / ABOUT) and the primary CTA button; don't extend that pattern to
every label or it stops meaning anything.

## Layout principles

- **Sidebar:** fixed, `--teal-deep` background, white/light text, one accent dot (`--clay`)
  marking the active item only.
- **Content area:** `--bg` page background with white `--surface` cards, 16px card radius,
  1px `--border` outline instead of heavy drop shadows — keeps it feeling calm and
  document-like rather than "glossy SaaS."
- **Status chips** (application tracking, trust scores) use tint backgrounds + matching
  text color rather than solid fills — softer, and keeps the palette's warm character even
  in functional UI states.
- **Numbering** (career path rank #1/#2/#3) is used only where content is genuinely ranked —
  don't add numbered badges to unordered lists elsewhere.
- **Charts** (skill growth trend): single teal line, one clay dot marking the current/latest
  point — no gradient fills, no multi-color legends unless the data genuinely has multiple
  independent series.

## Applying this elsewhere

- **Academician / Industry / Institution dashboards:** reuse the same sidebar, card, and
  chip system. Vary only the sidebar nav items and card content — do not introduce new
  accent colors per role; that would break the "one brand" feel across the four dashboards
  the SRS specifies.
- **Curriculum Feedback Loop UI** (the USP): since this is the feature you most want to
  stand out, it's the one place besides the hero where using `--clay` more prominently
  (e.g., a clay-bordered card, like the pitch deck's diagram) is justified — everywhere
  else, keep clay rare.

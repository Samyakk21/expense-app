# STATE.md — Working State

## Active task
Restyle the Expense Splitter web app into a **bold neubrutalist** design.
Started: 2026-11-20
Status: **COMPLETE — committed & pushed** (visual browser check unavailable in this environment)

### Follow-up round (same task, user feedback)
1. Straighten every tilted text box (cards, chips, tabs, stamps, badges, CTA, modal).
2. Fix marquee: seamless continuous loop, larger/taller text, four colored phrases.
3. Fix Add Expense split rows not refreshing when a person is added.
4. Dense seamless marquee (6 repeats × 4 spans per group, 60s loop).
5. Mobile status badge collapsed to a small dot-only sticker.
6. Custom neubrutalist select (chunky arrow block) + keep people constant after
   adding/deleting an expense so multiple expenses can be entered back-to-back.

## Scope / hard constraints
- Keep **all** functionality, data flow, API calls, element IDs, and handlers intact.
- Change **only** markup structure where needed for styling, plus the CSS.
  - Exception (explicitly requested in follow-up): `populateUserSelects()` now calls
    `rebuildSplits()` so Add Expense reflects newly added people. No API/ID/handler changes.
- **No new dependencies.** Plain CSS with custom properties (project does not use Tailwind).
- Do **not** touch business logic (backend `app/*.py`, core splitting/settlement code).
- Fonts loaded from Google Fonts via `<link>` in HTML — no JS dependencies.

## Files owned by this task
| File | Change |
|------|--------|
| `public/style.css` | Full rewrite → neubrutalist design system; follow-up: all text rotations removed, seamless larger marquee with 4 colors |
| `public/index.html` | Font `<link>`s, burst SVG symbol, two-group seamless marquee, stat stickers, `panel-title` tabs, "SETTLE UP" CTA, modal a11y attributes |
| `public/script.js` | Markup edits (avatars, stamps, copy, tints) **plus** the requested `rebuildSplits()` sync fix. No API/ID/handler changes. |
| `STATE.md` | Created + maintained (this file) |

## Files explicitly NOT touched
- `app/` (all Python — backend, core logic, storage layer)
- `requirements.txt`, `vercel.json`, `run.py`, `.python-version`
- `legacy/` (original preserved code)
- `supabase/`
- `README.md`, `.gitignore`

## Invariants preserved (verified ✓)
### Element IDs — all 18 present exactly once in `index.html`
`sync-status`, `toast`, `stat-expenses`, `stat-amount`, `stat-settled`, `stat-pending`,
`users-list`, `expense-payer`, `expense-amount`, `mode-equal`, `mode-exact`,
`splits-container`, `expenses-list`, `balances-output`, `user-modal`, `user-form`,
`modal-user-name`, `modal-user-id`

### Handlers — all present and unchanged
`openUserModal()`, `closeUserModal()`, `handleAddUser(event)`,
`setSplitMode('equal')`, `setSplitMode('exact')`, `addExpense()`, `loadData()`,
`loadBalances()`, `loadSettlements()`, `deleteUser(id)`, `deleteExpense(id)`

### API calls — all unchanged
`GET /users`, `POST /users`, `DELETE /users/{id}`, `GET /expenses`, `POST /expenses`,
`DELETE /expenses/{id}`, `GET /balances`, `GET /settlements`

### JS-dependent class names — retained on rendered elements
`status-badge`, `status-connected`, `status-disconnected`, `toast`, `success`, `error`,
`user-chip`, `chip-remove`, `empty-msg`, `split-row`, `split-user`, `split-amount`,
`remove-split`, `expense-item`, `expense-info`, `expense-payer`, `expense-detail`,
`expense-amount`, `expense-actions`, `btn`, `btn-outline`, `btn-primary`, `btn-full`,
`balance-list`, `balance-item`, `balance-name`, `balance-amount`, `positive`,
`negative`, `zero`, `settlement-list`, `settlement-item`, `settlement-flow`,
`settlement-from`, `settlement-arrow`, `settlement-to`, `settlement-amount`, `hint`,
`toggle-btn`, `active`, `form-row`, `panel`, `panel-header`, `panel-actions`,
`dashboard`, `stat-card`, `stat-total`, `stat-amount`, `stat-settled`, `stat-pending`,
`stat-label`, `stat-value`, `expense-form`, `splits-container`, `split-mode-row`,
`output-area`, `modal`, `modal-backdrop`, `modal-content`, `modal-header`,
`btn-close`, `form-actions`, `app-header`, `header-content`, `brand`, `brand-icon`,
`brand-name`, `header-actions`, `app-container`, `user-list`, `expenses-list`

## What changed visually
- **Palette/type:** cream dotted-paper background, saturated flat fills, 3px ink borders,
  hard zero-blur shadows, Archivo Black + Space Grotesk + Space Mono from Google Fonts.
- **Header:** yellow bar, upright logo, green CONNECTED / pink OFFLINE sticker badge,
  CSS-only black marquee with larger text in blue / orange / green / red phrases that
  loops seamlessly and continuously (two identical groups, `translateX(-50%)`, linear infinite).
- **Stats:** four colored cards, huge numbers, burst stickers, hover lift to larger hard shadow.
- **Sections:** folder-tab titles (colored per section), white bordered cards.
- **Controls:** chunky buttons with press-down active state and striped disabled state;
  uppercase mono labels; custom chevron selects; hidden number spinners; segmented
  Equal/Exact toggle; dashed split container with `:empty` placeholder.
- **People:** upright colored sticker chips with circular initial avatars; dashed empty state.
- **Expenses:** row cards with avatar, bold payer/amount, mono split details, upright
  PENDING stamp, pink delete button; "NO EXPENSES. SUSPICIOUSLY CHEAP." empty state.
- **Balances:** tinted ledger rows, bordered amount boxes, thick arrow with "owes" label,
  oversized yellow SETTLE UP CTA with an upright bounce, green "ALL SQUARE. GO HAVE A SAMOSA 🎉" state.
- **All text boxes are now straight** — only the decorative arrowhead keeps a 45° rotation.
- **Modal/toast:** 4px border modal over flat dark backdrop, colored header band, square ✕;
  bottom-right success/error toasts with stepped slide-in.
- **Motion/a11y:** 80ms linear snaps, 60ms staggered section pop-in, visible focus rings,
  44px tap targets, status conveyed by text + shape, reduced-motion + dark-mode support.
- **Responsive:** 4 → 2 → 1 column stats, stacked forms, reduced borders/shadows at ≤480px.

## Design decisions
- Provided design tokens used verbatim.
- Optional marquee and burst stickers included (pure CSS/inline SVG, no deps).
- Split-area placeholder via CSS `:empty::before` — no JS logic touched.
- Marquee uses two identical `.marquee__group` blocks inside a `width: max-content` flex
  track; `-50%` translation = one group, so the loop has no gap or restart.
- Hover wiggle was replaced with a translate-only bounce so no text is ever tilted.
- `rebuildSplits()` is called from `populateUserSelects()` — the smallest place that
  covers add-person, delete-person, and initial load.
- Status dot drawn with CSS `::before`; JS now sets just "Connected"/"Offline" text.
- "Settle Up" visible label for the existing `loadSettlements()` handler (handler unchanged).
- Dark mode inverts paper/border tokens while keeping saturated accents and black text on them.

## Verification checklist
- [x] All element IDs present exactly once
- [x] All inline handlers present and unchanged
- [x] All API call paths unchanged
- [x] JS syntax check passes (`node --check public/script.js`)
- [x] CSS braces balanced; only remaining `rotate()` is the 45° arrowhead shape
- [x] HTML tag structure balanced (`html.parser` validation)
- [x] Marquee has two identical groups, `linear infinite`, no rotation, larger font/padding
- [x] `populateUserSelects()` calls `rebuildSplits()`; add-person flow re-tested via API
- [x] Only owned files changed (`git status`)
- [x] Demo data round-trip through live FastAPI backend (4 users + 1 expense + settlements)
- [x] Committed and pushed
- [ ] Visual screenshot review — no headless browser connected in this environment

## Progress log
- 2026-11-20 — Inspected all app files + 3 inspiration sites; created STATE.md; clean tree.
- 2026-11-20 — Rewrote `public/style.css` as neubrutalist design system.
- 2026-11-20 — Updated `public/index.html` markup (fonts, marquee, stickers, tab titles, CTA).
- 2026-11-20 — Applied markup-only edits to `public/script.js` (avatars, stamps, copy, tints).
- 2026-11-20 — Verified IDs/handlers/APIs, JS syntax, HTML/CSS structure; seeded demo data
  against live backend successfully. Browser screenshot unavailable (no connected browser).
- 2026-11-20 — Updated STATE.md and committed/pushed (`8efd67d`).
- 2026-11-20 — Follow-up: straightened all tilted text, rebuilt marquee as seamless
  4-color loop with bigger text, fixed Add Expense split rows on person add; verified
  and pushed.
- 2026-11-23 — Dense 6× marquee, mobile dot-only status badge (then shrunk further).
- 2026-11-23 — Replaced native select chrome with `.select-wrap` + solid arrow block
  (payer and split selects); removed redundant `loadUsers()` calls from `addExpense()`
  and `deleteExpense()` so the people list stays constant. Verified with jsdom:
  two consecutive expenses with 3 people, no re-adding.

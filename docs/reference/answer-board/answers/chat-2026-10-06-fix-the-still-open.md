# Instruction in chat · 2026-10-06 · fix what is still open on the London close

The user's words, typed in the build session's chat on 2026-10-06:

> fix the still open

The London gate report (`docs/reports/london-gate-report.md`, "Open, and recorded") listed two
items still open: the flaky city render suite (lessons entry 20) and the delivery section's board
WARN, 210 prose words against its 171-209 band after the London map facade added its caption and
note. This file is the source of board revision 43 on `data/boards/blue-staffy-puppies-london.json`
(`answer board 2026-10-06-chat-fix-the-still-open q01`, the chat-ruling form board revision 34 set).

| Item | What was done |
|---|---|
| Delivery word band | The board gate's prose count (`scripts/pageboard.py` `_SectionProse`) inherits the dup gate's chrome rules and excludes no widget UI text, so no exclusion was invented. The facade's own note was trimmed by the fewest words that keep both disclosures: "Nothing loads from Google until you tap. Showing the map loads Google Maps, which sets cookies." (was "…which sets its own cookies."). Delivery measures 208 prose words; the WARN is gone. `tests/py/test_london_page.py` pins the two disclosures. |
| Flaky city render suite | Fixed in the harness, not the page (lessons entry 20). |

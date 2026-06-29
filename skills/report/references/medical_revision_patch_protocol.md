# Revision Patch Protocol (#390)

**Spec:** `docs/design/2026-06-10-390-diff-patch-revision-mode-spec.md` (mechanism 搂3, coverage claim 搂4, escalation 搂3.6).
**Toolchain:** Slice A (#423) 鈥?`scripts/_block_parser.py`, `scripts/ars_anchorize_draft.py`, `scripts/ars_apply_revision_patch.py`, schemas under `resources/contracts/patch/`.
**Audience:** the pipeline orchestrator (Mode A) and any user running revision rounds phase-by-phase across sessions (Mode B). The commands below are the same in both modes 鈥?Mode A wraps them, Mode B types them.

**What this buys, stated honestly:** under patch apply, a block no operation names cannot be silently distorted, because no generation pass runs over it 鈥?that is a property of the apply script, not of the model. It does NOT make the edits themselves better, and structural rewrites are not patch-protected (they escalate, 搂3.6). Every summary of this feature must survive that sentence.

---

## Artifacts and naming

| Artifact | Produced by | Convention |
|---|---|---|
| Anchored draft | `ars_anchorize_draft.py` (in place) | every block carries `<!--block:BNNNN-->`; IDs never renumbered |
| Block manifest | same run, sidecar | `<draft>.block-manifest.json` 鈥?`base_draft_hash` + `{block_id, old_hash, first_line_excerpt}` per block; the ONLY legitimate hash source for a patch |
| Patch document | `manuscript_drafter` (revision invocation) | `phase6_*/revision_patch_round<N>.json`, schema `resources/contracts/patch/revision_patch.schema.json` |
| Revised draft | `ars_apply_revision_patch.py` | `--output` MUST be a new file (versioned artifact; the base is never modified) |
| Apply report | same run, sidecar | `<output>.apply-report.json` 鈥?ops applied, fresh block IDs, structural flags, `preserved_ratio` |

The apply report shares the revised draft's lifecycle: it is a **required input to re-review and the Stage 4.5 integrity gate** 鈥?re-reviewers read it to see exactly which blocks changed (`ops_applied[]`, `fresh_block_ids`, `pure_move_pairs`) and which are machine-guaranteed untouched.

## Mode B command sequence (one revision round)

```bash
# 1. Anchorize / refresh the manifest (idempotent; safe on legacy drafts).
#    Run at EVERY round entry, and rewrite nothing afterwards until apply 鈥?#    any rewrite (including a finalizer pass) invalidates the manifest.
python scripts/ars_anchorize_draft.py draft.md

# 2. Hand the writer its revision context:
#    draft.md + draft.md.block-manifest.json + the round's Revision Roadmap.
#    The writer emits phase6_*/revision_patch_round1.json (never a full draft).

# 3. Apply 鈥?two-phase fail-closed; output must be a NEW file.
python scripts/ars_apply_revision_patch.py draft.md \
    phase6_revision/revision_patch_round1.json \
    --output draft.rev1.md

# 4. Run your normal post-revision steps (finalizer / citation checks)
#    on draft.rev1.md, then re-review with draft.rev1.md.apply-report.json
#    attached.
```

Exit codes: `0` applied 路 `2` Phase 1 rejection (structured failure report on stdout; base byte-untouched) 路 `3` structural refusal (see escalation) 路 `4` post-write self-check bug.

**On exit 2 (stale hash / unknown target / schema failure):** feed the failure report back to the writer for ONE re-emission of the whole patch against the current manifest. On a second failure, stop and decide: re-anchorize and retry the round, escalate to full re-emission, or abort. Never hand-edit a patch to force it through 鈥?a hash mismatch means the writer was looking at different text than the file holds.

**On exit 3 (structural flags):** the patch touches structure 鈥?heading rewrites/deletes, net section-count change, or `touched_ratio` strictly above **0.6** (the #424 ship decision; `insert_after` merely *anchored* on a heading is exempt 鈥?inserting body text under a section heading is routine, not structural). Read the flags in the refusal output, then either narrow the patch, or 鈥?if the structural change is intended 鈥?re-run with the acknowledgment recorded:

```bash
python scripts/ars_apply_revision_patch.py draft.md patch.json \
    --output draft.rev1.md --acknowledge-structural
```

`--acknowledge-structural` is a deliberate user decision, never a default; the flags stay recorded in the apply report either way. `--touched-ratio-threshold 1.0` disables the ratio trigger (the comparator is strict `>`); overriding 0.6 in pipeline runs requires a recorded user decision.

**Full re-emission (escalated rounds only):** when a round genuinely demands restructuring, the round runs as legacy full re-emission after explicit confirmation 鈥?never as a silent fallback. Afterwards, re-anchorize from scratch (a NEW ID generation; the old manifest and any old patches are dead) and record the round as `mode: full_reemission_escalated`.

## Marker lifecycle (one rule for all marker kinds)

`<!--block:-->` markers live in **working drafts only**, exactly like `<!--ref:-->` / `<!--anchor:-->`. Two authoritative rules govern them 鈥?this doc indexes them rather than re-owning the wording, so the rule cannot drift out of sync with the surfaces the #390 lint guards:

- **Word counts exclude markers** 鈥?strip every `<!--...-->` before `len(body.split())`. Authoritative: `resources/references/word_count_conventions.md` 搂 HTML-comment markers.
- **Phase 7 strips markers from converted final outputs**, after the marker-dependent gates run on the working draft; working drafts and `phase6_*/` artifacts keep theirs (the anchor layer the next round's manifest needs). Authoritative: `output_formatter.md` 搂 MSRA Marker Stripping.

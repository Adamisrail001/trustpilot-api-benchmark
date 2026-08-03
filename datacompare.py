"""
DATACOMPARE - Scraper Data Comparison Engine
============================================
CC: Shehriar Awan

Deterministic scoring engine for the Data pillar, implementing
data-comparison-model.md (Spec v1.2). Used by the /datacompare command.

This script does ONLY the countable arithmetic (fill rate, completeness,
breadth, cardinality, consistency, weighted composite). The judgment calls
(accuracy vs baseline, normalization, freshness, baseline spot-check) and the
written report are done by Claude in the /datacompare command. Keeping the
arithmetic here makes every number reproducible and defensible in an article.

STDLIB ONLY. No pip installs.

TWO PHASES
----------
1) signals   reads the config + raw scraper outputs, computes every
             deterministic signal, writes signals.json. Also emits a
             suggested field map to cut the manual mapping work.

2) rollup    reads signals.json + judgments.json (Claude's value-dimension
             scores + any N/A flags) and computes the weighted composite with
             the model's reweighting rule. Writes datacompare.json (the §13
             machine artifact) and datacompare_scores.md (a plain scores table).

USAGE
-----
  python datacompare.py signals --dir content/<folder>/data
  python datacompare.py rollup  --dir content/<folder>/data

The config lives at <dir>/datacompare.config.json. See
datacompare.config.example.json for the annotated shape.
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from statistics import mean

# ---------------------------------------------------------------------------
# Model constants (data-comparison-model.md §11). LITE is derived from FULL by
# keeping only the four structural dimensions and renormalising, which is
# exactly what the model's Lite-weight table does.
# ---------------------------------------------------------------------------
FULL_WEIGHTS = {
    "accuracy": 0.25,
    "completeness": 0.20,
    "fill_rate": 0.20,
    "breadth_cardinality": 0.15,
    "consistency": 0.10,
    "freshness": 0.05,
    "normalization": 0.05,
}
STRUCTURAL_DIMS = ["fill_rate", "completeness", "breadth_cardinality", "consistency"]
VALUE_DIMS = ["accuracy", "normalization", "freshness"]

EMPTY_STRINGS = {"", "n/a", "na", "null", "none", "-", "--"}

# ---------------------------------------------------------------------------
# Capture-time equivalence (model §3b). Timing skew corrupts only the
# dimensions whose signal is a VALUE or a COUNT, never the structural ones.
# The gap between the earliest and latest capture picks a tier:
#   negligible (<=1h)  -> treat as simultaneous, no adjustment
#   moderate   (<=48h) -> accuracy scoped to stable (non-volatile) fields;
#                         cardinality kept but flagged lower-confidence
#   large      (>48h)  -> as moderate, PLUS completeness, cardinality and
#                         freshness demoted to N/A and reweighted out, since a
#                         later run accrues records/reviews for reasons that
#                         have nothing to do with scraper quality.
# ---------------------------------------------------------------------------
TIMING_NEGLIGIBLE_H = 1
TIMING_MODERATE_H = 48


def _timing(caps, warnings):
    """caps = {scraper_name: captured_at ISO string}. Returns
    (gap_hours, tier, demote_to_na, accuracy_stable_only, drop_cardinality)."""
    if len(caps) < 2:
        if caps:
            warnings.append("captured_at set on <2 scrapers; capture gap unknown, "
                            "treating as simultaneous")
        return None, "unknown", [], False, False
    times = []
    for name, ts in caps.items():
        try:
            times.append(datetime.fromisoformat(str(ts).replace("Z", "+00:00")))
        except ValueError:
            warnings.append(f"{name}: unparseable captured_at '{ts}' "
                            f"(want ISO 8601, e.g. 2026-06-06T14:30:00Z)")
    if len(times) < 2:
        return None, "unknown", [], False, False
    gap_h = (max(times) - min(times)).total_seconds() / 3600.0
    if gap_h <= TIMING_NEGLIGIBLE_H:
        return round(gap_h, 2), "negligible", [], False, False
    if gap_h <= TIMING_MODERATE_H:
        warnings.append(
            f"capture gap {gap_h:.1f}h (MODERATE): accuracy scoped to stable "
            f"fields; cardinality kept but flagged lower-confidence.")
        return round(gap_h, 2), "moderate", [], True, False
    warnings.append(
        f"capture gap {gap_h:.1f}h (LARGE): accuracy scoped to stable fields; "
        f"completeness, cardinality and freshness demoted to N/A and reweighted. "
        f"The later scraper is favored by data accrual -- verify the baseline was "
        f"NOT chosen on record count, and consider reconstructing the overlap set "
        f"on records that existed at the earlier capture (model §3b).")
    return round(gap_h, 2), "large", ["completeness", "freshness"], True, True


# ---------------------------------------------------------------------------
# Small IO helpers
# ---------------------------------------------------------------------------
def die(msg):
    print(f"datacompare: error: {msg}", file=sys.stderr)
    sys.exit(2)


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as fh:
        return json.load(fh)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Record extraction + path walking
# ---------------------------------------------------------------------------
def extract_records(obj, records_path=None):
    """Return the list of record dicts from a loaded scraper output."""
    if records_path:
        cur = obj
        for seg in records_path.split("."):
            if isinstance(cur, dict) and seg in cur:
                cur = cur[seg]
            else:
                return []
        return cur if isinstance(cur, list) else [cur]
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        # common wrappers, first list wins
        for key in ("data", "results", "items", "records", "reviews",
                    "reviewsData", "response", "rows"):
            if isinstance(obj.get(key), list):
                return obj[key]
        # a bare single record
        return [obj]
    return []


def _maybe_json(value):
    """A string value that is itself JSON -> parse it, so the walkers descend
    into the embedded structure instead of counting it as one opaque leaf.
    Covers the model's 'json within the value of a json key as a string' case.
    Non-JSON strings (and everything else) pass through unchanged."""
    if isinstance(value, str):
        s = value.strip()
        if s[:1] in ("{", "["):
            try:
                return json.loads(s)
            except (ValueError, TypeError):
                return value
    return value


def is_populated(v):
    """A value carries data. 'N/A'-style strings are treated as EMPTY here so
    fill rate reflects real data; the normalization dimension flags the fact
    that the scraper used a junk string instead of a proper null."""
    if v is None:
        return False
    if isinstance(v, str):
        return v.strip().lower() not in EMPTY_STRINGS
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return True  # numbers, bools (incl. 0 / False are real values)


def collect_leaf_paths(obj, prefix, out):
    """Distinct key PATHS in dot-notation, array indices collapsed to []."""
    obj = _maybe_json(obj)
    if isinstance(obj, dict):
        if not obj:
            out.add(prefix + "{}" if prefix else "{}")
            return
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            collect_leaf_paths(v, p, out)
    elif isinstance(obj, list):
        if not obj:
            out.add(f"{prefix}[]")
            return
        for item in obj:
            collect_leaf_paths(item, f"{prefix}[]", out)
    else:
        out.add(prefix)


def collect_populated_paths(obj, prefix, out):
    obj = _maybe_json(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            collect_populated_paths(v, p, out)
    elif isinstance(obj, list):
        for item in obj:
            collect_populated_paths(item, f"{prefix}[]", out)
    else:
        if is_populated(obj):
            out.add(prefix)


def collect_cardinalities(obj, prefix, out):
    """For each array path, how many elements it holds (populated + containers)."""
    obj = _maybe_json(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            collect_cardinalities(v, p, out)
    elif isinstance(obj, list):
        path = f"{prefix}[]"
        count = sum(1 for x in obj if isinstance(x, (dict, list)) or is_populated(x))
        out[path] = out.get(path, 0) + count
        for item in obj:
            collect_cardinalities(item, path, out)


def path_segments(path):
    """'a.b[].c' -> ['a', 'b[]', 'c']  (keeps the [] marker on its token)."""
    return path.split(".")


def resolve_values(obj, segments):
    """Yield every concrete value found at a collapsed path (fans out over [])."""
    obj = _maybe_json(obj)
    if not segments:
        yield obj
        return
    seg, rest = segments[0], segments[1:]
    is_arr = seg.endswith("[]")
    key = seg[:-2] if is_arr else seg
    if not isinstance(obj, dict) or key not in obj:
        return
    val = _maybe_json(obj[key])
    if is_arr:
        if isinstance(val, list):
            for item in val:
                yield from resolve_values(item, rest)
    else:
        yield from resolve_values(val, rest)


def path_populated(record, path):
    """Does this record carry data at the given collapsed path?"""
    return any(is_populated(v) for v in resolve_values(record, path_segments(path)))


# ---------------------------------------------------------------------------
# Field-map suggestion (cuts the manual alignment work; also validates a map)
# ---------------------------------------------------------------------------
_TOKEN_SPLIT = re.compile(r"[^a-z0-9]+")


def name_tokens(path):
    leaf = path.split(".")[-1].replace("[]", "")
    # split camelCase then non-alnum
    leaf = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", leaf)
    return set(t for t in _TOKEN_SPLIT.split(leaf.lower()) if t)


def name_similarity(a, b):
    ta, tb = name_tokens(a), name_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def suggest_field_map(scrapers, baseline_name, common_records, exclude):
    """For each baseline leaf path, propose the best-matching path in each other
    scraper by name-token overlap + value agreement on the common record."""
    base_rec = common_records.get(baseline_name)
    if base_rec is None:
        return []
    base_paths = set()
    collect_leaf_paths(base_rec, "", base_paths)
    base_paths = sorted(p for p in base_paths if not _excluded(p, exclude))

    other = {n: r for n, r in common_records.items() if n != baseline_name}
    other_paths = {}
    for n, r in other.items():
        s = set()
        collect_leaf_paths(r, "", s)
        other_paths[n] = sorted(s)

    suggestions = []
    for bp in base_paths:
        base_vals = {str(v).strip().lower()
                     for v in resolve_values(base_rec, path_segments(bp))
                     if is_populated(v)}
        row = {"canonical": bp.split(".")[-1].replace("[]", ""),
               "paths": {baseline_name: bp}}
        for n in other:
            best, best_score = None, 0.0
            for op in other_paths[n]:
                nsim = name_similarity(bp, op)
                vals = {str(v).strip().lower()
                        for v in resolve_values(other[n], path_segments(op))
                        if is_populated(v)}
                vsim = (len(base_vals & vals) / len(base_vals | vals)
                        if (base_vals or vals) else 0.0)
                score = 0.6 * nsim + 0.4 * vsim
                if score > best_score:
                    best, best_score = op, score
            row["paths"][n] = best if best_score >= 0.34 else None
            row.setdefault("confidence", {})[n] = round(best_score, 2)
        suggestions.append(row)
    return suggestions


def _excluded(path, exclude):
    leaf = path.split(".")[-1].replace("[]", "")
    norm = re.sub(r"[^a-z0-9]", "", leaf.lower())
    for ex in exclude:
        if re.sub(r"[^a-z0-9]", "", ex.lower()) == norm:
            return True
    return False


# ---------------------------------------------------------------------------
# Scoring bands / helpers
# ---------------------------------------------------------------------------
def band_score(ratio):
    """ratio (0..1) -> 0..10, one decimal, capped."""
    return round(min(1.0, max(0.0, ratio)) * 10, 1)


# ---------------------------------------------------------------------------
# PHASE 1 - signals
# ---------------------------------------------------------------------------
def cmd_signals(args):
    d = args.dir
    cfg_path = os.path.join(d, "datacompare.config.json")
    if not os.path.exists(cfg_path):
        die(f"config not found: {cfg_path}")
    cfg = load_json(cfg_path)

    mode = cfg.get("mode", "full").lower()
    if mode not in ("full", "lite"):
        die("mode must be 'full' or 'lite'")
    exclude = cfg.get("exclude_paths", [])
    genuine_null = set(cfg.get("genuine_null_fields", []))
    default_id = cfg.get("id_field")
    field_map = cfg.get("fields")  # optional canonical universe with aliases
    accuracy_sample = int(cfg.get("accuracy_sample_size", 40))
    # canonical field names that change over time (helpful votes, aggregate
    # rating, price, availability...). Two sources, unioned: a top-level list
    # and a per-field "volatile": true marker in the field map.
    volatile_fields = set(cfg.get("volatile_fields", []))
    for f in (field_map or []):
        if f.get("volatile"):
            volatile_fields.add(f["canonical"])

    scraper_cfgs = cfg.get("scrapers", [])
    if len(scraper_cfgs) < 2:
        die("need at least 2 scrapers")

    warnings = []
    loaded = {}       # name -> {records, id_field, is_api, csv}
    id_sets = {}
    for sc in scraper_cfgs:
        name = sc["name"]
        path = os.path.join(d, sc["json"])
        if not os.path.exists(path):
            die(f"missing scraper file: {path}")
        recs = extract_records(load_json(path), sc.get("records_path"))
        idf = sc.get("id_field", default_id)
        loaded[name] = {
            "records": recs,
            "id_field": idf,
            "is_api": bool(sc.get("is_api")),
            "csv": sc.get("csv"),
            "reruns": sc.get("reruns", []),
            "cfg": sc,
        }
        if idf:
            ids = set()
            for r in recs:
                if isinstance(r, dict) and idf in r and r[idf] is not None:
                    ids.add(str(r[idf]))
            id_sets[name] = ids
            if not ids:
                warnings.append(f"{name}: no records carry id_field '{idf}'")
        else:
            warnings.append(f"{name}: no id_field configured; cannot align records")

    # --- overlap set (records present in ALL scrapers, aligned on id) ---
    if id_sets and len(id_sets) == len(loaded):
        overlap_ids = set.intersection(*id_sets.values()) if id_sets else set()
    else:
        overlap_ids = set()
    overlap_size = len(overlap_ids)
    if overlap_size == 0:
        warnings.append("EMPTY OVERLAP SET - align on a shared id or drop to "
                        "equivalence level D (describe structures, emit no scores)")

    # index records by id for quick lookup on the overlap set
    indexed = {}
    for name, info in loaded.items():
        idf = info["id_field"]
        idx = {}
        if idf:
            for r in info["records"]:
                if isinstance(r, dict) and r.get(idf) is not None:
                    idx[str(r[idf])] = r
        indexed[name] = idx

    # --- capture-time equivalence (model §3b) ---
    caps = {sc["name"]: sc["captured_at"]
            for sc in scraper_cfgs if sc.get("captured_at")}
    gap_hours, timing_tier, timing_demote, acc_stable_only, drop_cardinality = \
        _timing(caps, warnings)

    # --- baseline selection ---
    baseline = cfg.get("baseline", "auto")
    if baseline == "auto" or baseline not in loaded:
        # most distinct leaf paths on the common record (superset heuristic)
        def path_count(name):
            rec = _pick_common_record(loaded[name]["records"],
                                      loaded[name]["id_field"],
                                      cfg.get("common_record_id"))
            s = set()
            if rec:
                collect_leaf_paths(rec, "", s)
            return len([p for p in s if not _excluded(p, exclude)])
        baseline = max(loaded, key=path_count)
        warnings.append(f"baseline auto-selected: '{baseline}' (most fields). "
                        f"Disclose + spot-check it before publishing.")

    # --- pick the deliberately-chosen common record per scraper ---
    common_id = cfg.get("common_record_id")
    common_records = {}
    for name, info in loaded.items():
        rec = _pick_common_record(info["records"], info["id_field"], common_id)
        common_records[name] = rec
        if rec is None:
            warnings.append(
                f"{name}: common record '{common_id}' NOT FOUND -> excluded from "
                f"breadth/cardinality/normalization/accuracy (no silent fallback "
                f"to a different entity). Pick a common_record_id present in ALL "
                f"scrapers, or accept this scraper scores N/A on depth dimensions.")

    base_common = common_records.get(baseline)
    base_leaf = set()
    if base_common:
        collect_leaf_paths(base_common, "", base_leaf)
    base_leaf = set(p for p in base_leaf if not _excluded(p, exclude))

    # baseline cardinalities on the common record
    base_card = {}
    if base_common:
        collect_cardinalities(base_common, "", base_card)

    # --- per-scraper dimension signals ---
    results = {}
    baseline_count = len(loaded[baseline]["records"])
    records_expected = cfg.get("records_expected") or baseline_count

    for name, info in loaded.items():
        r = {"name": name, "is_api": info["is_api"], "is_baseline": name == baseline}

        # (2) completeness ---------------------------------------------------
        returned = len(info["records"])
        r["completeness"] = {
            "records_returned": returned,
            "records_expected": records_expected,
            "ratio": round(returned / records_expected, 4) if records_expected else None,
            "score": band_score(returned / records_expected) if records_expected else None,
        }

        # (6) breadth + cardinality (common record) --------------------------
        # Under a large capture gap, cardinality is dropped (records/reviews
        # accrue over time) but BREADTH is kept -- the field set is a schema
        # property that a time gap can't change. Combined then = breadth only.
        r["breadth_cardinality"] = _breadth_cardinality(
            name, baseline, common_records, base_leaf, base_card,
            field_map, exclude, drop_cardinality=drop_cardinality)

        # (1) fill rate (overlap set) ----------------------------------------
        r["fill_rate"] = _fill_rate(
            name, baseline, overlap_ids, indexed, field_map, base_leaf,
            exclude, genuine_null)

        # (3) consistency (reruns) -------------------------------------------
        r["consistency"] = _consistency(d, info, mode)

        # normalization mechanical pre-checks (common record, full only) -----
        if mode == "full":
            r["normalization_prechecks"] = _normalization_prechecks(
                common_records.get(name), exclude)

        # accuracy field diffs vs baseline (SAMPLE of overlap records, not one
        # record; full + map). Under a capture gap, volatile fields are skipped.
        if mode == "full" and field_map and name != baseline:
            r["accuracy_diffs"] = _accuracy_diffs(
                name, baseline, overlap_ids, indexed, field_map, exclude,
                sample_size=accuracy_sample, stable_only=acc_stable_only,
                volatile_fields=volatile_fields)

        # CSV export round-trip ----------------------------------------------
        if info["csv"]:
            r["csv_check"] = _csv_roundtrip(d, info["csv"], common_records.get(name))

        results[name] = r

    signals = {
        "mode": mode,
        "skip_dimensions": cfg.get("skip_dimensions", []),
        "equivalence_level": cfg.get("equivalence_level"),
        "target": cfg.get("target"),
        "baseline_scraper": baseline,
        "baseline_auto_selected": cfg.get("baseline", "auto") == "auto",
        "datasets": {
            "overlap_set_size": overlap_size,
            "common_record_id": common_id,
        },
        "records_expected": records_expected,
        "timing": {
            "gap_hours": gap_hours,
            "tier": timing_tier,
            "accuracy_stable_only": acc_stable_only,
            "cardinality_dropped": drop_cardinality,
            "demote_to_na": timing_demote,
            "volatile_fields": sorted(volatile_fields),
        },
        "field_map_provided": bool(field_map),
        "scrapers": [results[n] for n in loaded],
        "suggested_field_map": suggest_field_map(
            loaded, baseline, common_records, exclude) if not field_map else None,
        "warnings": warnings,
    }
    out = os.path.join(d, "signals.json")
    write_json(out, signals)
    print(f"wrote {out}")
    print(f"  mode={mode}  baseline={baseline}  overlap={overlap_size}  "
          f"scrapers={len(loaded)}")
    if timing_tier not in (None, "unknown", "negligible"):
        print(f"  timing: gap={gap_hours}h tier={timing_tier} "
              f"demote={timing_demote or '-'}")
    if warnings:
        print("  warnings:")
        for w in warnings:
            print(f"    - {w}")
    if not field_map:
        print("  no field map in config -> see 'suggested_field_map' in "
              "signals.json, review it, and paste a 'fields' block into the config.")


def _pick_common_record(records, id_field, common_id):
    if not records:
        return None
    if common_id and id_field:
        for r in records:
            if isinstance(r, dict) and str(r.get(id_field)) == str(common_id):
                return r
        # The common record was explicitly chosen. If this scraper doesn't have
        # it, DO NOT substitute records[0] -- that is a different real-world
        # entity, and silently comparing depth/accuracy across mismatched
        # entities is the exact failure this guard exists to prevent. Return
        # None so the caller warns and excludes this scraper from depth metrics.
        return None
    # No common_id specified at all -> first record is an acceptable default.
    return records[0] if isinstance(records[0], dict) else None


def _breadth_cardinality(name, baseline, common_records, base_leaf, base_card,
                         field_map, exclude, drop_cardinality=False):
    rec = common_records.get(name)
    if rec is None or not base_leaf:
        return {"breadth_ratio": None, "cardinality_ratio": None,
                "breadth_score": None, "cardinality_score": None,
                "combined": None, "note": "common record missing"}

    # breadth = schema/field-TYPE coverage (does the field exist), NOT whether
    # this record populated it. A field present-but-empty still counts for
    # breadth and gets dinged on fill rate instead (the two are orthogonal).
    if field_map:
        base_fields = [f for f in field_map
                       if f["paths"].get(baseline) and
                       not _excluded(f["paths"][baseline], exclude)]
        present = sum(1 for f in base_fields if f["paths"].get(name))
        denom = len(base_fields)
    else:
        leaf = set()
        collect_leaf_paths(rec, "", leaf)
        leaf = set(p for p in leaf if not _excluded(p, exclude))
        present = len(leaf & base_leaf)
        denom = len(base_leaf)
    breadth_ratio = present / denom if denom else None

    # cardinality
    card = {}
    collect_cardinalities(rec, "", card)
    collection_map = field_map and [f for f in (field_map or []) if f.get("collection")]
    ratios = []
    detail = {}
    card_note = None
    if drop_cardinality:
        # Large capture gap: element counts differ because reviews/records
        # accrue over time, not because of scraper quality. Keep breadth only.
        card_note = ("cardinality dropped: large capture gap makes element "
                     "counts incomparable (accrual over time)")
    elif field_map and collection_map:
        for f in collection_map:
            bpath = f["paths"].get(baseline)
            spath = f["paths"].get(name)
            bn = base_card.get(bpath, 0) if bpath else 0
            sn = card.get(spath, 0) if spath else 0
            if bn:
                ratios.append(min(1.0, sn / bn))
                detail[f["canonical"]] = {"baseline": bn, name: sn}
    else:
        # no explicit collection mapping: compare same-named array paths
        for bpath, bn in base_card.items():
            if bn and not _excluded(bpath, exclude):
                sn = card.get(bpath, 0)
                ratios.append(min(1.0, sn / bn))
                detail[bpath] = {"baseline": bn, name: sn}
    cardinality_ratio = mean(ratios) if ratios else None

    breadth_score = band_score(breadth_ratio) if breadth_ratio is not None else None
    cardinality_score = (band_score(cardinality_ratio)
                         if cardinality_ratio is not None else None)
    if breadth_score is not None and cardinality_score is not None:
        combined = round(0.5 * breadth_score + 0.5 * cardinality_score, 1)
    else:
        combined = breadth_score if cardinality_score is None else cardinality_score
    return {
        "breadth_ratio": round(breadth_ratio, 4) if breadth_ratio is not None else None,
        "cardinality_ratio": round(cardinality_ratio, 4) if cardinality_ratio is not None else None,
        "breadth_score": breadth_score,
        "cardinality_score": cardinality_score,
        "combined": combined,
        "cardinality_detail": detail,
        "cardinality_note": card_note,
    }


def _fill_rate(name, baseline, overlap_ids, indexed, field_map, base_leaf,
               exclude, genuine_null):
    if not overlap_ids:
        return {"score": None, "mean_fill": None,
                "note": "no overlap set; fill rate not computable"}
    if not field_map and name != baseline:
        return {"score": None, "mean_fill": None,
                "note": "no field map; cross-scraper fill rate needs a "
                        "'fields' map (names differ across scrapers)"}

    base_idx = indexed[baseline]
    this_idx = indexed[name]

    # universe of fields the baseline actually delivers on the overlap set
    if field_map:
        universe = []
        for f in field_map:
            bpath = f["paths"].get(baseline)
            if not bpath or _excluded(bpath, exclude):
                continue
            if f["canonical"] in genuine_null:
                continue
            # baseline delivers it in >=1 overlap record?
            if any(path_populated(base_idx[i], bpath)
                   for i in overlap_ids if i in base_idx):
                universe.append(f)
        per_field = {}
        for f in universe:
            spath = f["paths"].get(name)
            if not spath:
                per_field[f["canonical"]] = 0.0
                continue
            pops = sum(1 for i in overlap_ids
                       if i in this_idx and path_populated(this_idx[i], spath))
            per_field[f["canonical"]] = round(pops / len(overlap_ids), 4)
    else:
        # baseline vs itself: ~1.0 by definition
        universe = sorted(base_leaf)
        per_field = {}
        for p in universe:
            if p.split(".")[-1] in genuine_null:
                continue
            pops = sum(1 for i in overlap_ids
                       if i in base_idx and path_populated(base_idx[i], p))
            per_field[p] = round(pops / len(overlap_ids), 4)

    mean_fill = mean(per_field.values()) if per_field else None
    return {
        "mean_fill": round(mean_fill, 4) if mean_fill is not None else None,
        "score": band_score(mean_fill) if mean_fill is not None else None,
        "fields_measured": len(per_field),
        "per_field": per_field,
    }


def _consistency(d, info, mode):
    reruns = info.get("reruns", [])
    if len(reruns) < 2:
        return {"score": None, "note": "N/A - need >=2 rerun files", "available": False}
    idf = info["id_field"]
    run_paths, schemas, run_indexes = [], [], []
    for rp in reruns:
        full = os.path.join(d, rp)
        if not os.path.exists(full):
            return {"score": None, "note": f"rerun file missing: {rp}",
                    "available": False}
        recs = extract_records(load_json(full))
        s = set()
        for r in recs:
            collect_leaf_paths(r, "", s)
        schemas.append(s)
        idx = {}
        if idf:
            for r in recs:
                if isinstance(r, dict) and r.get(idf) is not None:
                    idx[str(r[idf])] = r
        run_indexes.append(idx)

    schema_identical = all(s == schemas[0] for s in schemas)

    # value drift across the aligned records shared by all runs
    shared = set.intersection(*[set(ix.keys()) for ix in run_indexes]) \
        if all(run_indexes) else set()
    drift_fields, compared = set(), 0
    for rid in shared:
        recs = [ix[rid] for ix in run_indexes]
        paths = set()
        collect_leaf_paths(recs[0], "", paths)
        for p in paths:
            vals = [tuple(sorted(str(v) for v in resolve_values(rc, path_segments(p))))
                    for rc in recs]
            compared += 1
            if any(v != vals[0] for v in vals):
                drift_fields.add(p)
    value_drift_pct = round(100 * len(drift_fields) / compared, 2) if compared else 0.0

    # suggested band (Claude confirms; "volatile fields only" -> 7-9)
    if not schema_identical:
        suggested = 2.0
    elif value_drift_pct == 0 or mode == "lite":
        suggested = 10.0
    elif value_drift_pct <= 10:
        suggested = 8.0
    else:
        suggested = 5.0
    return {
        "available": True,
        "runs": len(reruns),
        "schema_identical": schema_identical,
        "value_drift_pct": value_drift_pct,
        "drifting_fields": sorted(drift_fields)[:30],
        "suggested_score": suggested,
        "note": "schema-only in lite mode; Claude confirms the band in full mode",
    }


def _normalization_prechecks(rec, exclude):
    """Mechanical pre-checks for the 8-criterion normalization checklist.
    Claude finalises criteria_met/8 using these + the fuzzy criteria."""
    if rec is None:
        return {"note": "common record missing"}
    findings = {c: [] for c in
                ["numeric_as_string", "non_iso_dates", "currency_glued",
                 "html_in_text", "whitespace_junk", "na_strings"]}
    iso = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2})?")
    numlike = re.compile(r"^-?\d[\d,]*\.?\d*$")
    datelike = re.compile(r"\d{1,4}[/\-.]\d{1,2}[/\-.]\d{1,4}|\b\d{4}\b")
    currency = re.compile(r"[$€£¥]\s?\d|\d\s?(usd|eur|gbp)\b", re.I)
    html = re.compile(r"<[^>]+>|&[a-z]+;", re.I)

    def walk(o, prefix=""):
        o = _maybe_json(o)
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{prefix}.{k}" if prefix else str(k))
        elif isinstance(o, list):
            for it in o:
                walk(it, f"{prefix}[]")
        elif isinstance(o, str):
            leaf = prefix.split(".")[-1]
            if _excluded(prefix, exclude):
                return
            if numlike.match(o.strip()) and o.strip() not in ("", "-"):
                findings["numeric_as_string"].append(f"{prefix}={o[:30]}")
            if o.strip().lower() in ("n/a", "na", "null", "none"):
                findings["na_strings"].append(prefix)
            if o != o.strip() or "  " in o:
                findings["whitespace_junk"].append(prefix)
            if html.search(o):
                findings["html_in_text"].append(prefix)
            if currency.search(o):
                findings["currency_glued"].append(f"{prefix}={o[:20]}")
            if ("date" in leaf.lower() or "time" in leaf.lower()) \
                    and datelike.search(o) and not iso.match(o.strip()):
                findings["non_iso_dates"].append(f"{prefix}={o[:30]}")

    walk(rec)
    # trim + de-dup
    for k in findings:
        findings[k] = sorted(set(findings[k]))[:15]
    return findings


def _accuracy_diffs(name, baseline, overlap_ids, indexed, field_map, exclude,
                    sample_size=40, stable_only=False, volatile_fields=None):
    """Value comparison vs baseline over a SAMPLE of matched overlap records --
    not one record -- so a single odd record can't define the accuracy score.
    Aggregates raw string mismatches per field across the sample; Claude then
    judges which mismatches are true ERRORS vs legitimate differences.

    Under a capture-time gap (stable_only=True), volatile fields (helpful votes,
    aggregate rating, price...) are excluded, because a disagreement there could
    just be the value moving between captures, not a scraper error."""
    volatile_fields = set(volatile_fields or [])
    base_idx, this_idx = indexed.get(baseline, {}), indexed.get(name, {})
    ids = sorted(i for i in overlap_ids if i in base_idx and i in this_idx)
    if not ids:
        return {"note": "no matched overlap records", "diffs": [], "sampled": 0}
    # deterministic, reproducible sample: first N of the sorted overlap ids
    sample = ids[:sample_size]

    skipped_volatile = []
    comparable = []
    for f in field_map:
        bpath, spath = f["paths"].get(baseline), f["paths"].get(name)
        if not bpath or not spath or f.get("collection") or _excluded(bpath, exclude):
            continue
        if stable_only and (f.get("volatile") or f["canonical"] in volatile_fields):
            skipped_volatile.append(f["canonical"])
            continue
        comparable.append(f)

    fields_compared = 0
    mismatch = {}
    examples = []
    for rid in sample:
        brec, srec = base_idx[rid], this_idx[rid]
        for f in comparable:
            bvals = list(resolve_values(brec, path_segments(f["paths"][baseline])))
            svals = list(resolve_values(srec, path_segments(f["paths"][name])))
            if not bvals or not svals:
                continue
            fields_compared += 1
            if str(bvals[0]).strip() != str(svals[0]).strip():
                mismatch[f["canonical"]] = mismatch.get(f["canonical"], 0) + 1
                if len(examples) < 15:
                    examples.append({"id": rid, "field": f["canonical"],
                                     "baseline": str(bvals[0])[:80],
                                     name: str(svals[0])[:80]})
    total_mismatch = sum(mismatch.values())
    return {
        "sampled_records": len(sample),
        "overlap_available": len(ids),
        "fields_compared": fields_compared,
        "mismatches": total_mismatch,
        "raw_match_ratio": (round(1 - total_mismatch / fields_compared, 4)
                            if fields_compared else None),
        "mismatch_by_field": dict(sorted(mismatch.items(), key=lambda kv: -kv[1])),
        "stable_only": stable_only,
        "skipped_volatile_fields": sorted(set(skipped_volatile)),
        "diffs": examples,
        "note": "Claude judges which diffs are true errors vs legitimate; "
                "raw_match_ratio is plain string inequality across the sample, "
                "NOT the final accuracy score.",
    }


def _csv_roundtrip(d, csv_name, json_rec):
    path = os.path.join(d, csv_name)
    if not os.path.exists(path):
        return {"note": f"csv missing: {csv_name}"}
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
    except Exception as e:
        return {"note": f"csv unreadable: {e}"}
    json_paths = set()
    if json_rec:
        collect_leaf_paths(json_rec, "", json_paths)
    nested = sorted(p for p in json_paths if "[]" in p and p.count("[]") >= 1)
    # CSV can't hold repeated collections; flag any nested array leaf
    lost = [p for p in nested if not any(p.split(".")[-1].replace("[]", "")
                                         in h for h in header)]
    return {
        "csv_columns": len(header),
        "json_leaf_paths": len(json_paths),
        "nested_paths_at_risk": nested[:20],
        "likely_lost_in_csv": lost[:20],
        "nested_data_lost": bool(lost),
        "note": "CSV is an export round-trip check only (model §10); "
                "dropped nested data = usability ding, not a schema score",
    }


# ---------------------------------------------------------------------------
# PHASE 2 - rollup
# ---------------------------------------------------------------------------
def cmd_rollup(args):
    d = args.dir
    sig = load_json(os.path.join(d, "signals.json"))
    jpath = os.path.join(d, "judgments.json")
    judgments = load_json(jpath) if os.path.exists(jpath) else {"scrapers": {}}
    jmap = {s["name"]: s for s in judgments.get("scrapers", [])} \
        if isinstance(judgments.get("scrapers"), list) else judgments.get("scrapers", {})

    mode = sig["mode"]
    skip = sig.get("skip_dimensions", [])
    timing = sig.get("timing") or {}
    timing_demote = set(timing.get("demote_to_na", []))

    # Level-D floor (model §3 / non-negotiable §14.1): no overlap set can be
    # established -> not a valid comparison. Describe structures, emit NO scores.
    overlap = (sig.get("datasets") or {}).get("overlap_set_size", 0)
    floor = overlap == 0 or (sig.get("equivalence_level") or "").upper() == "D"

    out_scrapers = []
    for s in sig["scrapers"]:
        name = s["name"]
        j = jmap.get(name, {})
        dims = {}

        dims["fill_rate"] = _num(s.get("fill_rate", {}).get("score"))
        dims["completeness"] = _num(s.get("completeness", {}).get("score"))
        dims["breadth_cardinality"] = _num(s.get("breadth_cardinality", {}).get("combined"))
        # consistency: Claude's final band wins, else the suggested band, else N/A
        cons = s.get("consistency", {})
        dims["consistency"] = _num(j.get("consistency",
                                          cons.get("suggested_score") if cons.get("available") else None))

        if mode == "full":
            dims["accuracy"] = _num(j.get("accuracy"))
            dims["normalization"] = _num(j.get("normalization"))
            dims["freshness"] = _num(j.get("freshness"))

        # baseline is the reference: fill + breadth ~10 by definition
        if s.get("is_baseline"):
            if dims.get("fill_rate") is None:
                dims["fill_rate"] = 10.0
            if dims.get("breadth_cardinality") is None:
                dims["breadth_cardinality"] = 10.0

        # capture-time gap: demote timing-sensitive dims to N/A so the model's
        # reweighting rule redistributes their weight (model §3b). Structural
        # dims are untouched -- a time gap can't change a schema.
        for dm in timing_demote:
            dims[dm] = None

        composite, weights_used, na = _composite(dims, mode, skip=skip)
        entry = {
            "name": name,
            "is_baseline": s.get("is_baseline", False),
            "is_api": s.get("is_api", False),
            "dimensions": {k: v for k, v in dims.items()
                           if v is not None and k not in skip},
            "na_dimensions": na,
            "weights_used": {} if floor else weights_used,
            "composite": None if floor else composite,
            "flags": j.get("flags", []),
        }
        out_scrapers.append(entry)

    artifact = {
        "mode": mode,
        "skipped_dimensions": skip,
        "equivalence_level": sig.get("equivalence_level"),
        "target": sig.get("target"),
        "valid_comparison": not floor,
        "baseline_scraper": sig.get("baseline_scraper"),
        "baseline_disclosed": judgments.get("baseline_disclosed", True),
        "baseline_spotcheck_passed": judgments.get("baseline_spotcheck_passed"),
        "datasets": sig.get("datasets"),
        "timing": timing,
        "scrapers": out_scrapers,
    }
    if floor:
        artifact["floor_reason"] = (
            "Level-D floor: no overlap set could be established (records do not "
            "align on a shared id). Not a valid comparison - describe each "
            "scraper's structure, emit no scores (model §3, §14.1).")
    write_json(os.path.join(d, "datacompare.json"), artifact)
    _write_scores_md(d, artifact)
    print(f"wrote {os.path.join(d, 'datacompare.json')}")
    print(f"wrote {os.path.join(d, 'datacompare_scores.md')}")
    if floor:
        print("  LEVEL-D FLOOR: no valid overlap set -> no scores emitted. "
              "Describe each scraper's structure instead.")
        return
    for sc in out_scrapers:
        print(f"  {sc['name']:<16} composite={sc['composite']}  "
              f"NA={sc['na_dimensions']}")


def _num(v):
    try:
        return round(float(v), 1) if v is not None else None
    except (TypeError, ValueError):
        return None


def _composite(dims, mode, skip=None):
    """Weighted composite with the model's reweighting rule: keep FULL weights,
    restrict to the dims in scope (lite drops value dims), drop any N/A dim OR
    any dimension the config deliberately skips, renormalise over survivors so
    weights total 1.00."""
    skip = set(skip or [])
    in_scope = STRUCTURAL_DIMS[:] if mode == "lite" else list(FULL_WEIGHTS.keys())
    in_scope = [k for k in in_scope if k not in skip]
    available = [k for k in in_scope if dims.get(k) is not None]
    na = [k for k in in_scope if dims.get(k) is None]
    total_w = sum(FULL_WEIGHTS[k] for k in available)
    if not available or total_w == 0:
        return None, {}, na
    weights_used = {k: round(FULL_WEIGHTS[k] / total_w, 4) for k in available}
    composite = sum(dims[k] * weights_used[k] for k in available)
    return round(composite, 2), weights_used, na


def _write_scores_md(d, art):
    dims_order = ["fill_rate", "completeness", "breadth_cardinality",
                  "consistency", "accuracy", "normalization", "freshness"]
    labels = {"fill_rate": "Fill rate", "completeness": "Completeness",
              "breadth_cardinality": "Breadth+Card", "consistency": "Consistency",
              "accuracy": "Accuracy", "normalization": "Normalization",
              "freshness": "Freshness"}
    names = [s["name"] for s in art["scrapers"]]
    lines = [f"# Data comparison scores - {art.get('target', '')}", "",
             f"- Mode: **{art['mode']}**  |  Equivalence level: "
             f"**{art.get('equivalence_level')}**",
             f"- Baseline (de facto oracle): **{art['baseline_scraper']}** "
             f"(disclosed={art.get('baseline_disclosed')}, "
             f"spot-check={art.get('baseline_spotcheck_passed')})",
             f"- Overlap set: **{art['datasets'].get('overlap_set_size')}** records"
             f"  |  Common record: `{art['datasets'].get('common_record_id')}`", ""]
    _t = art.get("timing") or {}
    if _t.get("tier") not in (None, "unknown", "negligible"):
        _dem = ", ".join(_t.get("demote_to_na") or []) or "none"
        lines += [f"- **Capture-time gap: {_t.get('gap_hours')}h "
                  f"({_t.get('tier')}).** Accuracy scoped to stable fields; "
                  f"demoted to N/A (reweighted): {_dem}. Value/count dimensions "
                  f"are timing-limited -- structural dimensions are not.", ""]
    lines += ["| Dimension | " + " | ".join(names) + " |",
             "|---|" + "|".join(["---"] * len(names)) + "|"]
    used = [dm for dm in dims_order
            if any(dm in s["dimensions"] or dm in s["na_dimensions"]
                   for s in art["scrapers"])]
    for dm in used:
        row = [labels[dm]]
        for s in art["scrapers"]:
            if dm in s["dimensions"]:
                row.append(str(s["dimensions"][dm]))
            elif dm in s["na_dimensions"]:
                row.append("N/A")
            else:
                row.append("-")
        lines.append("| " + " | ".join(row) + " |")
    comp = ["**Composite /10**"] + [
        ("**invalid**" if s["composite"] is None else f"**{s['composite']}**")
        for s in art["scrapers"]]
    lines.append("| " + " | ".join(comp) + " |")
    if not art.get("valid_comparison", True):
        lines.insert(1, f"\n> **No scores emitted.** {art.get('floor_reason', '')}\n")
    lines.append("")
    for s in art["scrapers"]:
        if s.get("flags"):
            lines.append(f"- **{s['name']} flags:** " + "; ".join(s["flags"]))
    with open(os.path.join(d, "datacompare_scores.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# DOCS - the human/vault-facing text files (mechanical layer)
# ---------------------------------------------------------------------------
GEN_MARKER = "generated by datacompare.py"


def _safe_write(path, content, force):
    """Write, but never clobber a hand-edited file. A file we generated carries
    GEN_MARKER; if a file exists WITHOUT it and --force wasn't passed, skip so a
    hand-written analysis (e.g. an editorial gaps.txt) is protected."""
    if os.path.exists(path) and not force:
        try:
            with open(path, "r", encoding="utf-8-sig") as fh:
                existing = fh.read()
        except Exception:
            existing = ""
        if GEN_MARKER not in existing:
            print(f"  SKIP (hand-written, no marker): {os.path.basename(path)} "
                  f"-- pass --force to overwrite")
            return False
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  wrote {os.path.basename(path)}")
    return True


def _inventory(d, cfg):
    """name -> sorted union of raw leaf paths across all of a scraper's records."""
    inv = {}
    for sc in cfg["scrapers"]:
        recs = extract_records(load_json(os.path.join(d, sc["json"])),
                               sc.get("records_path"))
        paths = set()
        for r in recs:
            collect_leaf_paths(r, "", paths)
        inv[sc["name"]] = sorted(paths)
    return inv


def _canon_key_maps(cfg, inv):
    """For each scraper, map raw leaf path -> comparison key. A mapped field uses
    its canonical name (so renamed-but-equivalent fields collapse and don't show
    as false uniques); an unmapped field keeps its raw path. Returns (keyset,
    pathkey) where keyset[name] is the set of keys and pathkey[name][raw]=key."""
    field_map = cfg.get("fields") or []
    raw2canon = {sc["name"]: {} for sc in cfg["scrapers"]}
    for f in field_map:
        for name, p in (f.get("paths") or {}).items():
            if p:
                raw2canon.setdefault(name, {})[p] = f["canonical"]
    keyset, pathkey = {}, {}
    for name, paths in inv.items():
        pk = {p: raw2canon.get(name, {}).get(p, p) for p in paths}
        pathkey[name] = pk
        keyset[name] = set(pk.values())
    return keyset, pathkey


def cmd_docs(args):
    d = args.dir
    cfg_path = os.path.join(d, "datacompare.config.json")
    if not os.path.exists(cfg_path):
        die(f"config not found: {cfg_path}")
    cfg = load_json(cfg_path)
    exclude = cfg.get("exclude_paths", [])
    platform = cfg.get("platform") or cfg.get("target") or ""
    names = [sc["name"] for sc in cfg["scrapers"]]

    inv = _inventory(d, cfg)
    keyset, pathkey = _canon_key_maps(cfg, inv)
    canon_aware = bool(cfg.get("fields"))

    # baseline for the "missing" orientation
    baseline = cfg.get("baseline", "auto")
    if baseline == "auto" or baseline not in inv:
        baseline = max(inv, key=lambda n: len(inv[n]))

    def others_keys(name):
        u = set()
        for n in names:
            if n != name:
                u |= keyset[n]
        return u

    # a raw path is unique if its comparison key appears in no other scraper.
    # Plumbing (exclude_paths) is stripped: the gap analysis is about real data
    # points, not business-listing metadata / internal IDs repeated on every row.
    uniques = {}
    for n in names:
        ok = others_keys(n)
        uniques[n] = sorted(p for p in inv[n]
                            if pathkey[n][p] not in ok and not _excluded(p, exclude))

    print(f"docs: platform='{platform}'  baseline='{baseline}'  "
          f"canonical-aware={canon_aware}")

    # --- per-scraper: {name}-data.txt and {name}-meaningful-data.txt ---
    for n in names:
        disp = n.upper()
        ok = others_keys(n)
        not_returned = sorted(k for k in ok
                              if k not in keyset[n] and not _excluded(k, exclude))
        body = [f"{disp}", f"Total fields: {len(inv[n])}",
                f"({GEN_MARKER}; regenerate with /datacompare)", ""]
        body += inv[n]
        body += ["", f"UNIQUE IN {disp}"] + (uniques[n] or ["(none)"])
        body += ["", f"NOT RETURNED BY {disp}"] + (not_returned or ["(none)"])
        _safe_write(os.path.join(d, f"{n}-data.txt"), "\n".join(body) + "\n", args.force)

        meaningful = [p for p in inv[n] if not _excluded(p, exclude)]
        stripped = sorted({ex for ex in exclude
                           if any(_excluded(p, [ex]) for p in inv[n])})
        mbody = [f"MEANINGFUL DATA POINTS - {disp}" + (f" ({platform})" if platform else ""),
                 f"({GEN_MARKER}; plumbing in exclude_paths stripped; "
                 f"nested fields use dot notation, [] marks an array)",
                 f"{len(meaningful)} meaningful data points",
                 f"(stripped: {', '.join(stripped) if stripped else 'none'})",
                 "-" * 60] + meaningful
        _safe_write(os.path.join(d, f"{n}-meaningful-data.txt"),
                    "\n".join(mbody) + "\n", args.force)

    # --- gaps.txt (FACTUAL skeleton only; the roadmap layer is hand-written) ---
    gaps = [f"DATA GAP ANALYSIS - FACTUAL SKELETON" + (f" - {platform}" if platform else ""),
            f"({GEN_MARKER}; unique + missing data points across scrapers.)",
            "This is the FACTUAL layer only. Priority, why-it-matters, feasibility",
            "and the roadmap framing are added by hand on top of these facts.",
            f"Comparison basis: {'canonical field map' if canon_aware else 'raw field names (no map - renamed fields may show as false uniques)'}.",
            "=" * 68, "",
            "FIELDS UNIQUE TO EACH SCRAPER (present here, absent everywhere else)"]
    for n in names:
        gaps += ["", f"UNIQUE IN {n.upper()}"] + (uniques[n] or ["(none)"])
    base_missing = sorted(k for k in others_keys(baseline)
                          if k not in keyset[baseline] and not _excluded(k, exclude))
    gaps += ["", "=" * 68, "",
             f"MISSING FROM {baseline.upper()} "
             f"(a competitor captures it, {baseline} has no equivalent)"]
    for k in base_missing:
        havers = [n for n in names if n != baseline and k in keyset[n]]
        gaps.append(f"{k}  <- {', '.join(havers)}")
    if not base_missing:
        gaps.append("(none)")
    _safe_write(os.path.join(d, "gaps.txt"), "\n".join(gaps) + "\n", args.force)

    # --- comparison.md (engine-fuelled detailed comparison, for knowledge.md) ---
    _write_comparison_md(d, cfg, inv, keyset, uniques, baseline, exclude,
                         platform, canon_aware, args.force)


def _write_comparison_md(d, cfg, inv, keyset, uniques, baseline, exclude,
                         platform, canon_aware, force):
    art = None
    ap = os.path.join(d, "datacompare.json")
    if os.path.exists(ap):
        art = load_json(ap)
    names = [sc["name"] for sc in cfg["scrapers"]]
    api_names = {sc["name"] for sc in cfg["scrapers"] if sc.get("is_api")}
    L = [f"# Data comparison - {platform}",
         "",
         f"<!-- {GEN_MARKER}; reference this from knowledge.md. "
         f"Regenerate with /datacompare. -->",
         ""]
    if api_names:
        L += [f"> Scraper-vs-API run. Official API: **{', '.join(sorted(api_names))}**.", ""]
    if art:
        L += [f"- Mode: **{art['mode']}**  |  Equivalence level: "
              f"**{art.get('equivalence_level')}**  |  Valid: "
              f"**{art.get('valid_comparison', True)}**",
              f"- Baseline (de facto oracle): **{art.get('baseline_scraper')}** "
              f"(disclosed={art.get('baseline_disclosed')}, "
              f"spot-check={art.get('baseline_spotcheck_passed')})",
              f"- Overlap set: **{(art.get('datasets') or {}).get('overlap_set_size')}** "
              f"records  |  Common record: "
              f"`{(art.get('datasets') or {}).get('common_record_id')}`", ""]

    # human verdict (editorial one-liner; survives regeneration via the config)
    verdict = cfg.get("verdict")
    if verdict:
        L += [f"> **Verdict.** {verdict}", ""]

    # field inventory summary
    L += ["## Field inventory", "",
          "| Scraper | Total fields | Meaningful | Unique |",
          "|---|---|---|---|"]
    for n in names:
        meaningful = sum(1 for p in inv[n] if not _excluded(p, exclude))
        tags = []
        if n == baseline:
            tags.append("baseline")
        if n in api_names:
            tags.append("official API")
        star = f" ({', '.join(tags)})" if tags else ""
        L.append(f"| {n}{star} | {len(inv[n])} | {meaningful} | {len(uniques[n])} |")
    L.append("")

    # scores (if rollup ran)
    if art and art.get("valid_comparison", True):
        L += ["## Data-quality scores", "",
              "Weights + reweighting per data-comparison-model.md. Breadth and "
              "cardinality are reported as two numbers.", ""]
        if art.get("skipped_dimensions"):
            L += [f"_Dimensions excluded by choice (weights renormalized over the "
                  f"rest): {', '.join(art['skipped_dimensions'])}._", ""]
        dims_order = ["fill_rate", "completeness", "breadth_cardinality",
                      "consistency", "accuracy", "normalization", "freshness"]
        labels = {"fill_rate": "Fill rate", "completeness": "Completeness",
                  "breadth_cardinality": "Breadth+Card", "consistency": "Consistency",
                  "accuracy": "Accuracy", "normalization": "Normalization",
                  "freshness": "Freshness"}
        L.append("| Dimension | " + " | ".join(names) + " |")
        L.append("|---|" + "|".join(["---"] * len(names)) + "|")
        amap = {s["name"]: s for s in art["scrapers"]}
        used = [dm for dm in dims_order
                if any(dm in amap[n]["dimensions"] or dm in amap[n]["na_dimensions"]
                       for n in names if n in amap)]
        for dm in used:
            row = [labels[dm]]
            for n in names:
                s = amap.get(n, {"dimensions": {}, "na_dimensions": []})
                if dm in s["dimensions"]:
                    row.append(str(s["dimensions"][dm]))
                elif dm in s["na_dimensions"]:
                    row.append("N/A")
                else:
                    row.append("-")
            L.append("| " + " | ".join(row) + " |")
        comp = ["**Composite /10**"]
        for n in names:
            c = amap.get(n, {}).get("composite")
            comp.append(f"**{c}**" if c is not None else "-")
        L.append("| " + " | ".join(comp) + " |")
        L.append("")
        for n in names:
            fl = amap.get(n, {}).get("flags")
            if fl:
                L.append(f"- **{n} flags:** " + "; ".join(fl))
        L.append("")
    elif not art:
        L += ["## Data-quality scores", "",
              "_Not computed yet. Run `python datacompare.py rollup --dir <dir>` "
              "(after judgments.json) to add scores here._", ""]

    # uniques cross-tab
    L += ["## Fields unique to each scraper", ""]
    for n in names:
        L.append(f"**{n}**: " + (", ".join(f"`{u}`" for u in uniques[n])
                                 if uniques[n] else "_none_"))
    L.append("")

    # baseline misses
    base_missing = sorted(k for k in
                          set().union(*[keyset[n] for n in names if n != baseline])
                          if k not in keyset[baseline] and not _excluded(k, exclude)) \
        if len(names) > 1 else []
    L += [f"## Missing from {baseline} (competitor has it, {baseline} doesn't)", ""]
    if base_missing:
        for k in base_missing:
            havers = [n for n in names if n != baseline and k in keyset[n]]
            L.append(f"- `{k}` -- {', '.join(havers)}")
    else:
        L.append("_none_")
    L.append("")
    _safe_write(os.path.join(d, "comparison.md"), "\n".join(L) + "\n", force)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Scraper data comparison engine "
                                             "(data-comparison-model.md v1.2)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("signals", "rollup", "docs"):
        p = sub.add_parser(c)
        p.add_argument("--dir", required=True,
                       help="data directory holding datacompare.config.json + outputs")
        if c == "docs":
            p.add_argument("--force", action="store_true",
                           help="overwrite files even without the generated marker")
    args = ap.parse_args()
    {"signals": cmd_signals, "rollup": cmd_rollup, "docs": cmd_docs}[args.cmd](args)


if __name__ == "__main__":
    main()
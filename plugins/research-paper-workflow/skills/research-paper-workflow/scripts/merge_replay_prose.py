"""Consolidate repeated verified replay counts in their own results section."""
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
import re

SECTION = re.compile(r"(?m)^\\(?:sub)*section\*?\{")
INTEGER = r"\d+(?:(?:\{,\}|,)\d{3})*"
REPLAY_COUNT = re.compile(
    r"(?P<start>\b(?:"
    r"(?:Our|The) independent replay documented in the (?:archived |accompanying )?[^\n.\\]{1,110} found"
    r"|The complete records in the trial archive show"
    r"))\s+"
    rf"(?P<count>{INTEGER})\s+of\s+(?P<total>{INTEGER})\s+"
    r"(?P<event>[^\n]*?)\.(?=\s|$)", re.I,
)
POPULATION_VIOLATION = re.compile(r"\bpopulation\b[^;]{0,100}\b(?:above|exceed(?:ed|s|ing)?)\b", re.I)
FREQUENCY = re.compile(
    r"(?:This is|The joint violation frequency is) "
    r"(?P<rate>\d+(?:\.\d+)?) *(?:percent|\\%)"
    r"(?: with a Monte Carlo standard error of (?P<words>\d+(?:\.\d+)?) percentage points"
    r"| \(Monte Carlo standard error (?P<parentheses>\d+(?:\.\d+)?) percentage points\))"
)
EDITORIAL_BOUNDARY = re.compile(r"\\(?:begin|end|include|input|caption|label|section)\b|(?<!\\)%")
AUXILIARY = re.compile(r"\b(?:MCSE|standard error|confidence interval|medians?|means?|half-width|versus|never|did not)\b", re.I)
MULTI_CELL = re.compile(
    rf"\bAmong (?P<total>{INTEGER}) repetitions per (?:cell|setting|configuration), "
    r"(?P<event>[^;\n]{1,170}?) in (?P<results>[^\n]*?)\.(?=\s|$)", re.I,
)
CELL_RESULT = re.compile(
    rf"(?P<count>{INTEGER})(?: repetitions)? at (?P<setting>\$[A-Za-z] ?= ?(?P<value>\d+(?:\.\d+)?)\$) "
    r"\(\$(?P<rate>\d+(?:\.\d+)?)\\%\$, with Monte Carlo standard error "
    r"\$(?P<mcse>\d+(?:\.\d+)?)\$ percentage points\)"
)


def serial_integer(text):
    return int(re.sub(r"\D", "", text))


def shared_fields(groups):
    return {key: value for key, value in groups[0]["cell"].items()
            if all(group["cell"][key] == value for group in groups)}


def describe_design(spec, cell):
    return ", ".join(spec.get("levels", {}).get(key, {}).get(value)
                     or f"{spec.get('labels', {}).get(key, key)} {value}"
                     for key, value in cell.items())


def rate_matches(rate, count, total):
    value = Decimal(rate)
    expected = (Decimal(count) / Decimal(total) * 100).quantize(
        Decimal(1).scaleb(value.as_tuple().exponent), rounding=ROUND_HALF_UP)
    return expected == value


def verified_rows(rows, profile):
    files = {spec["file"]: spec for spec in profile["experiments"]
             if spec["basis"] == "replay"}
    if len(files) != 1:
        return {}
    spec, = files.values()
    available = [row for row in rows if row.get("source") == spec["file"]]
    if not available:
        return {}
    common = shared_fields(available)
    totals = Counter((row["count"], row["denominator"]) for row in available)
    return {(row["count"], row["denominator"]): (
                row, describe_design(spec, {key: value for key, value in row["cell"].items() if key not in common}))
            for row in available
            if row["count"] > 0 and totals[row["count"], row["denominator"]] == 1}


def consolidate(source, anchor, location, rows, profile):
    """Remove only recognized exact count restatements; keep other evidence."""
    cells = verified_rows(rows, profile)
    if not cells or location.get("position", "before") != "before":
        return source, []
    ending = source.index(anchor)
    sections = list(SECTION.finditer(source, 0, ending))
    if not sections:
        return source, []
    beginning = sections[-1].start()
    region = source[beginning:ending]
    if not re.search(r"independent(?:ly)?\W+(?:replay|replayed|reproducibility check)", region, re.I):
        return source, []

    edits = []
    removed = []
    matches = list(REPLAY_COUNT.finditer(region))
    for i, found in enumerate(matches):
        count = serial_integer(found["count"])
        total = serial_integer(found["total"])
        pair = cells.get((count, total))
        line_prefix = region[region.rfind("\n", 0, found.start()) + 1:found.start()]
        if not pair or EDITORIAL_BOUNDARY.search(found[0]) or r"\caption{" in line_prefix:
            continue
        event = found["event"]
        if AUXILIARY.search(event):
            continue
        row, design = pair
        flagged = POPULATION_VIOLATION.search(event) and "population" in row["measurement"].lower()
        is_declared_unsafe_selection = (
            event.strip().lower() == "runs with unsafe selection"
            and "population risk" in row["measurement"].lower()
            and re.search(r"call a selection unsafe\b", region[:found.start()], re.I)
        )
        if not (flagged or is_declared_unsafe_selection):
            continue

        # Keep commands, paragraph breaks, and all supporting statistics. If
        # a following duplicate percentage contains an MCSE, keep the MCSE
        # with an explicit design label.
        limit = matches[i + 1].start() if i + 1 < len(matches) else len(region)
        rest = region[found.end():min(limit, found.end() + 1000)]
        follow = FREQUENCY.search(rest)
        if follow:
            if rate_matches(follow["rate"], count, total):
                mcse = follow["words"] or follow["parentheses"]
                label = f" for {design}" if design else ""
                phrase = (f"The Monte Carlo standard error of the replay violation frequency{label} "
                          f"was {mcse} percentage points")
                edits.append((found.end() + follow.start(), found.end() + follow.end(), phrase))

        # When the next sentence points back to the removed statement,
        # keep its estimate and make the design explicit.
        referent = re.match(r"\s*The exact unconditional risk for (?P<reference>this configuration)\b", rest)
        if referent and design:
            a, b = referent.span("reference")
            edits.append((found.end() + a, found.end() + b, f"the configuration with {design}"))

        start, end = found.span()
        if region[end:end + 1] == " ":
            end += 1
        edits.append((start, end, ""))
        removed.append({"count": count, "denominator": total, "cell": row["cell"]})

    # Some manuscripts present both cells in one sentence with a shared
    # denominator. Match all counts, cell identifiers and rates before
    # retaining just the sentence's distinct uncertainty information.
    related = [row for row, _ in cells.values()]
    common = shared_fields(related)
    varying = set(related[0]["cell"]) - set(common)
    if len(varying) == 1:
        key, = varying
        for found in MULTI_CELL.finditer(region):
            if not (re.search(r"\b(?:violated|exceeded)\b", found["event"], re.I)
                    and "population" in found["event"].lower()
                    and not EDITORIAL_BOUNDARY.search(found[0])):
                continue
            parts = found["results"].split(" and ")
            matches = [CELL_RESULT.fullmatch(p) for p in parts]
            if len(matches) < 2 or None in matches:
                continue
            total = serial_integer(found["total"])
            replacement = []
            claims = []
            for match in matches:
                count = serial_integer(match["count"])
                pair = cells.get((count, total))
                if not pair or not rate_matches(match["rate"], count, total):
                    break
                row, _ = pair
                value = row["cell"][key]
                if not re.fullmatch(r"\d+(?:\.\d+)?", value) or Decimal(value) != Decimal(match["value"]):
                    break
                replacement.append(
                    f"at {match['setting']}, ${match['mcse']}$ percentage points")
                claims.append({"count": count, "denominator": total, "cell": row["cell"]})
            else:
                if len({item["count"] for item in claims}) == len(claims):
                    sentence = "The Monte Carlo standard errors for the replay violation frequency are "
                    edits.append((*found.span(), sentence + " and ".join(replacement) + "."))
                    removed.extend(claims)

    for start, end, replacement in sorted(edits, reverse=True):
        region = region[:start] + replacement + region[end:]
    return source[:beginning] + region + source[ending:], removed

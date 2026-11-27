"""Recount the author's trajectory classifications and visible crossings in the PDF."""
from decimal import Decimal
import re
import zlib


RGB = {
    (Decimal(1), Decimal(0), Decimal(0)): "red",
    (Decimal(0), Decimal("0.5019607843"), Decimal(0)): "green",
    (Decimal(0), Decimal(0), Decimal(1)): "blue",
}
POINT = re.compile(rb"([-0-9.]+)\s+([-0-9.]+)\s+[ml](?:\s|$)")
STROKE = re.compile(rb"(?P<rgb>[-0-9.]+\s+[-0-9.]+\s+[-0-9.]+)\s+RG\s+/DeviceRGB cs\s+(?P<path>[-0-9.\sml]+)\s+S(?:\s|$)")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def object_tail(pdf, number):
    pattern = rb"(?:^|\n)" + number + rb" 0 obj\s*"
    match = re.search(pattern, pdf)
    require(match is not None, f"Missing PDF object {number!r}")
    return pdf[match.end():]


def figure_stream(pdf):
    content_refs = re.findall(rb"/Type /Page(?=\s)[^>]*?/Contents\s+(\d+)\s+0\s+R", pdf)
    require(len(content_refs) == 1, "Expected the single page's direct content stream")
    payload = object_tail(pdf, content_refs[0])
    header, data = re.split(rb"\bstream\r?\n", payload, maxsplit=1)
    require(b"/Filter /FlateDecode" in header, "Expected Matplotlib's Flate stream")
    length_ref = re.search(rb"/Length\s+(\d+)\s+0\s+R", header)
    require(length_ref is not None, "Expected a length object")
    length_header = object_tail(pdf, length_ref[1])
    length = int(length_header.split(maxsplit=1)[0])
    return zlib.decompress(data[:length])


def number(raw):
    return Decimal(raw.decode("ascii"))


def count_plot(path, target, minimum_vertices=2):
    stream = figure_stream(path.read_bytes())
    colored_paths = {c: [] for c in RGB.values()}
    for match in STROKE.finditer(stream):
        rgb = tuple(number(x) for x in match["rgb"].split())
        color = RGB.get(rgb)
        if color is None:
            continue
        points = [(number(x), number(y)) for x, y in POINT.findall(match["path"])]
        colored_paths[color].append(points)

    ref, = colored_paths["blue"]
    require(len(ref) == 2 and ref[0][1] == ref[1][1], "Expected one horizontal risk limit")
    target_y = ref[0][1]
    require(all(len(path) >= minimum_vertices for color in ("red", "green") for path in colored_paths[color]),
            "Found an unrecognized colored stroke")
    result = {"file": path.name, "population_risk_target": target,
              "horizontal_reference_y_pdf_points": str(target_y)}
    for color in ("red", "green"):
        paths = colored_paths[color]
        result[color + "_paths"] = len(paths)
        result[color + "_with_visible_strict_crossing"] = sum(
            max(y for _, y in path) > target_y for path in paths
        )
    result["plotted_calibration_runs"] = result["red_paths"] + result["green_paths"]
    result["visible_strict_crossing_lower_bound"] = (
        result["red_with_visible_strict_crossing"] + result["green_with_visible_strict_crossing"]
    )
    return result

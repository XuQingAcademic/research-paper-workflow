#!/usr/bin/env python3
"""Draft a source-qualified result from a verified count and applicability statement."""

import argparse


WORDING = {
    "en": {
        "author-labels": "Using the authors' labels in {source}, {count} of {total} {unit} met the event criterion ({event}).",
        "full-records": "A recount of the decision records in {source} found {count} of {total} {unit} meeting the event criterion ({event}).",
        "visible-lower-bound": "The visible portion of {source} confirms at least {count} of {total} {unit} meeting the event criterion ({event}).",
        "replay": "In our replay of the design using {source}, {count} of {total} {unit} met the event criterion ({event}).",
    },
    "zh": {
        "author-labels": "按{source}中的作者标记，{total}个{unit}中有{count}个满足事件定义（{event}）。",
        "full-records": "从{source}的逐次决策重算，{total}个{unit}中有{count}个满足事件定义（{event}）。",
        "visible-lower-bound": "从{source}的可见部分可确认，{total}个{unit}中至少有{count}个满足事件定义（{event}）。",
        "replay": "按{source}重跑该设计时，{total}个{unit}中有{count}个满足事件定义（{event}）。",
    },
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--basis", required=True, choices=WORDING["en"])
    parser.add_argument("--language", choices=WORDING, default="en")
    parser.add_argument("--count", type=int, required=True)
    parser.add_argument("--total", type=int, required=True)
    parser.add_argument("--source", required=True, help="Reader-facing figure, data, or replay locator")
    parser.add_argument("--unit", required=True, help="Unit of the denominator")
    parser.add_argument("--event", required=True, help="Decision event at the specified limit")
    parser.add_argument("--scope", required=True, help="Verified full sentence on applicability")
    args = parser.parse_args()
    if not 0 <= args.count <= args.total or args.total == 0:
        parser.error("require 0 <= count <= total and total > 0")
    if not all(s.strip() for s in (args.source, args.unit, args.event, args.scope)):
        parser.error("source, unit, event, and scope must be nonempty")
    print(WORDING[args.language][args.basis].format(**vars(args)), args.scope.strip())


if __name__ == "__main__":
    main()

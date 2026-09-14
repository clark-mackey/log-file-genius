"""Canonical STATE handoff field names; the contract writers and readers share.

STATE's Current Context records the handoff as line-anchored bold fields whose
labels `freshness.assess` matches literally. The label is therefore load-bearing:
relabel one and the reader stops finding it, so recorded evidence reads exactly
like evidence that was never recorded. Stating the labels once here, and finding
near-miss relabelings, lets a rename fail loudly at both ends instead of becoming
absent evidence. A variant is never read as the field it shadows - accepting the
rename would hide it, which is the outcome this guards against.
"""
import re

CANONICAL_FIELDS = ('Baseline branch', 'Baseline commit', 'Next action', 'Tests', 'Blockers')

_LABEL = re.compile(r'^\*\*([^*:]+):\*\*', re.M)


def read_field(text, label):
    """The value recorded under exactly `label`, or None when absent, empty or repeated.

    The value is whatever follows the label on that same line: `.` excludes the
    newline and only spaces/tabs may separate label from value, so a label left
    bare reads as unrecorded instead of absorbing the next line as its value.
    Every occurrence of the label counts toward uniqueness, valued or bare, so a
    repeated label stays ambiguous rather than resolving to the one that has a
    value.
    """
    values = re.findall(r'^\*\*' + re.escape(label) + r':\*\*[ \t]*(.*)$', text, re.M)
    if len(values) != 1:
        return None
    return values[0].strip() or None


def _words(label):
    return [word for word in re.split(r'[^0-9a-z]+', label.lower()) if word]


def _shadows(candidate, canonical):
    """True when `candidate` reads as a relabeled `canonical`.

    Every canonical word survives, in order, with extra or differently cased
    words around it: `Baseline code commit`, `Baseline Commit`, `Last baseline
    commit`. The canonical label itself never shadows; a repeated canonical
    field keeps its own missing/ambiguous verdict rather than being called a
    rename of itself.
    """
    if candidate == canonical:
        return False
    wanted, written = _words(canonical), _words(candidate)
    remaining = list(wanted)
    for word in written:
        if remaining and word == remaining[0]:
            remaining.pop(0)
    return not remaining


def find_renamed_fields(text, labels=CANONICAL_FIELDS):
    """Canonical label -> the non-canonical labels standing in for it, in file order.

    Only labels that are not themselves recorded exactly once are reported, so a
    supplementary field beside a present canonical one stays ordinary content.
    A canonical label that is absent, bare or repeated is not recorded, so a
    variant standing beside it is still reported: an ambiguous canonical field
    plus a near-miss label is exactly the case worth naming.
    """
    recorded = {label for label in labels if read_field(text, label) is not None}
    renamed = {}
    for candidate in dict.fromkeys(match.group(1).strip() for match in _LABEL.finditer(text)):
        for label in labels:
            if label not in recorded and _shadows(candidate, label):
                renamed.setdefault(label, []).append(candidate)
    return renamed

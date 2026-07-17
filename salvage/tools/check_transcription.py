#!/usr/bin/env python3
"""Verify docs/original/users-guide.md against mbmgemp/MBMGEMP.DOC.

The transcription promises to change formatting only. This check
reduces both files to a bare word stream — the DOC stripped of page
breaks and layout whitespace, the markdown stripped of its editorial
preamble (everything up to the first ---), heading markers and code
fences — and diffs the two streams word by word. Any wording change,
dropped line or "fixed" typo shows up as a diff.
"""
import difflib
import re
import sys

DOC = "/Users/jim/develop/ge/mbmgemp/MBMGEMP.DOC"
MD = "/Users/jim/develop/ge/docs/original/users-guide.md"


def words(text):
    return re.sub(r"[ \t\n]+", " ", text).strip().split(" ")


doc = open(DOC, encoding="latin-1").read()
doc = re.sub(r"[^\x20-\x7e\t\n]", "", doc)          # form feeds, stray bytes
doc_words = words(doc)

md = open(MD).read().split("\n---\n", 1)[1]
md = re.sub(r"^```.*$", "", md, flags=re.M)          # code fences
md = re.sub(r"^#+ ", "", md, flags=re.M)             # heading markers
md_words = words(md)

diff = list(difflib.unified_diff(doc_words, md_words, "MBMGEMP.DOC",
                                 "users-guide.md", lineterm="", n=3))
if diff:
    print("\n".join(diff[:80]))
    print(f"TRANSCRIPTION DRIFT: {sum(1 for d in diff if d[:1] in '+-') - 2} "
          "word-level differences")
    sys.exit(1)
print(f"ok: {len(md_words)} words match {DOC}")

# SPDX-License-Identifier: Apache-2.0
"""Tests for bibliography-driven curation.

The idea: a source paper's own (web-verified) reference list is a far better
matching pool than open web search. The honesty guards under test:

- the parser extracts ids (arXiv/DOI) only when literally present;
- matching is deterministic lexical ranking against the pool;
- a registrar record may only stand in for a bib entry when the TITLES agree
  (normalized token overlap) — a mismatched registrar hit is a miscitation
  signal and must be rejected, never silently attached.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from biblio_curate import (  # noqa: E402
    match_bib, parse_bibliography, titles_agree,
)

BIB = """\
## References

- Andriushchenko, M., Souly, A., et al. (2024). AgentHarm: A Benchmark for \
Measuring Harmfulness of LLM Agents. *ICLR 2025*. arXiv:2410.09024.

- Howard, S. R., Ramdas, A., McAuliffe, J., & Sekhon, J. (2021). Time-uniform, \
nonparametric, nonasymptotic confidence sequences. *Annals of Statistics*. \
doi:10.1214/20-AOS1991.

- Bjøru, A. R. (2026). Causal Post-hoc Explainable AI (PhD thesis). Norwegian \
University of Science and Technology (NTNU). ISBN 978-82-353-0022-5.

- Geifman, Y. & El-Yaniv, R. (2017). Selective classification for deep neural \
networks. *NeurIPS 2017*. arXiv:1705.08500.
"""


def test_parser_extracts_entries_with_ids_only_when_present():
    entries = parse_bibliography(BIB)
    assert len(entries) == 4
    agent = entries[0]
    assert agent["first_author"] == "Andriushchenko"
    assert agent["year"] == 2024
    assert agent["title"].startswith("AgentHarm")
    assert agent["arxiv_id"] == "2410.09024"
    howard = entries[1]
    assert howard["doi"] == "10.1214/20-aos1991"
    assert howard["arxiv_id"] is None
    thesis = entries[2]
    assert thesis["arxiv_id"] is None and thesis["doi"] is None  # never invented


def test_match_ranks_pool_deterministically():
    entries = parse_bibliography(BIB)
    claim = {"id": "C-4", "statement":
             "selective prediction achieves 88.0% accuracy at 23.2% coverage "
             "on a held-out split with locked decision threshold"}
    ranked = match_bib(claim, entries)
    assert ranked[0][0]["title"].startswith("Selective classification")
    assert ranked == match_bib(claim, entries)      # deterministic


def test_titles_agree_guards_against_miscitation():
    assert titles_agree(
        "Time-uniform, nonparametric, nonasymptotic confidence sequences",
        "Time-uniform nonparametric nonasymptotic confidence sequences")
    # the Wave-1 class of bug: registrar returns a DIFFERENT paper
    assert not titles_agree(
        "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents",
        "A Survey of Watering Schedules for Houseplants")
    # regression (caught live): short-title overlap must not pass — Guo 2017
    # vs an unrelated 1989 sensor-calibration paper shared 3 of 4 tokens
    assert not titles_agree(
        "On calibration of modern neural networks",
        "Sensor calibration using artificial neural networks")

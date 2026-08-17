from __future__ import annotations

import pyarrow as pa
import pytest

from scripts.create_msmarco_subset import process_language_records


def _create_mock_table() -> pa.Table:
    """Creates a mock PyArrow table simulating the MSMARCO-XI Parquet structure."""
    data = {
        "query_id": [101, 102, 103, 104, 101],  # 101 is duplicate, 103 has no relevant, 104 has empty query
        "query": [
            "प्रकाश संश्लेषण क्या है?",
            "मंगल ग्रह लाल क्यों है?",
            "अमान्य प्रश्न",
            "",
            "डुप्लिकेट प्रश्न",
        ],
        "Eng_Query": [
            "What is photosynthesis?",
            "Why is Mars red?",
            "Invalid query",
            "",
            "Duplicate query",
        ],
        "source_lang": ["eng_Latn"] * 5,
        "target_lang": ["hin_Deva"] * 5,
        "passages": [
            {
                "English_passages": ["Photosynthesis creates sugar.", "Plants need light."],
                "Translated_passages": ["प्रकाश संश्लेषण शर्करा बनाता है।", "पौधों को प्रकाश चाहिए।"],
                "is_selected": [1, 0],
            },
            {
                "English_passages": ["Mars has iron oxide in soil."],
                "Translated_passages": ["मंगल की मिट्टी में आयरन ऑक्साइड है।"],
                "is_selected": [1],
            },
            {
                "English_passages": ["No passage selected."],
                "Translated_passages": ["कोई अंश चयनित नहीं।"],
                "is_selected": [0],
            },
            {
                "English_passages": ["Empty query passage."],
                "Translated_passages": ["खाली प्रश्न अंश।"],
                "is_selected": [1],
            },
            {
                "English_passages": ["Duplicate query passage."],
                "Translated_passages": ["डुप्लिकेट प्रश्न अंश।"],
                "is_selected": [1],
            },
        ],
    }
    return pa.Table.from_pydict(data)


def test_process_language_records_filters_and_formats_correctly() -> None:
    table = _create_mock_table()
    indices = list(range(len(table)))
    corpus: list[dict] = []
    cases: list[dict] = []

    selected, rejected = process_language_records(
        table=table,
        indices=indices,
        target_count=10,
        language="hi",
        translated=True,
        corpus_records=corpus,
        eval_cases=cases,
    )

    # Valid: 101, 102. Rejected: 103 (no selected=1), 104 (empty query), 101 dup (seen query_id)
    assert selected == 2
    assert rejected == 3

    assert len(cases) == 2
    assert cases[0]["query_id"] == "msmarco-xi:hi:101"
    assert cases[0]["language"] == "hi"
    assert cases[0]["query"] == "प्रकाश संश्लेषण क्या है?"
    assert cases[0]["relevant_document_ids"] == ["msmarco-xi:hi:101:0"]

    assert cases[1]["query_id"] == "msmarco-xi:hi:102"
    assert cases[1]["relevant_document_ids"] == ["msmarco-xi:hi:102:0"]

    # Check corpus integrity
    assert len(corpus) == 3  # 2 passages from 101, 1 passage from 102
    doc_ids = {c["document_id"] for c in corpus}
    for case in cases:
        for rel_id in case["relevant_document_ids"]:
            assert rel_id in doc_ids


def test_process_language_records_english_fields() -> None:
    table = _create_mock_table()
    indices = list(range(len(table)))
    corpus: list[dict] = []
    cases: list[dict] = []

    selected, rejected = process_language_records(
        table=table,
        indices=indices,
        target_count=1,
        language="en",
        translated=False,
        corpus_records=corpus,
        eval_cases=cases,
    )

    assert selected == 1
    assert cases[0]["query_id"] == "msmarco-xi:en:101"
    assert cases[0]["language"] == "en"
    assert cases[0]["query"] == "What is photosynthesis?"
    assert cases[0]["relevant_document_ids"] == ["msmarco-xi:en:101:0"]

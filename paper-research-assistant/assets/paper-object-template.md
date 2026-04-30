# Paper Object

```json
{
  "title": null,
  "authors": [],
  "year": null,
  "venue_or_source": null,
  "doi": null,
  "arxiv_id": null,
  "urls": {
    "abstract": null,
    "pdf": null,
    "publisher": null,
    "source": null
  },
  "input_type": "arxiv_url | doi | doi_url | pdf_url | local_pdf | title | pasted_text | unknown",
  "evidence_coverage": "full_text_pdf | full_text_html | abstract_only | metadata_only | partial_text | unknown",
  "resolution_confidence": "high | medium | low",
  "source_input": null,
  "ambiguities": [],
  "notes": []
}
```

Use `null`, `[]`, or `unknown` instead of inventing missing metadata. For multi-paper work, create one object per paper before synthesis.

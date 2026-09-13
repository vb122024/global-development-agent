# Reviewed World Bank report corpus

The initial narrative corpus is deliberately small: two official World Bank
overview booklets. [The catalog](catalog.json) records each source URL, title,
year, citation, and document-level license. The PDFs themselves are downloaded
into the ignored, project-local `data/source_documents/` directory.

1. `backend/.venv/bin/python scripts/ingest_reports.py prepare` downloads and
   validates the two PDFs. The script accepts only the reviewed World Bank
   hosts in the catalog, HTTPS, PDFs under 15 MiB, and no redirects to other
   hosts.
2. `backend/.venv/bin/python scripts/ingest_reports.py upload` puts the PDFs
   in OpenAI **Storage → Files** using the official Python SDK. Stable
   content-hash filenames and remote lookup prevent duplicate uploads.
3. `backend/.venv/bin/python scripts/ingest_reports.py create-store` creates
   or reuses the `global-development-world-bank-reports` vector store. It is
   initially **empty**.
4. `backend/.venv/bin/python scripts/ingest_reports.py status` checks remote
   file visibility and the count of files attached to the store.

OpenAI's portal is scoped to the organization and project associated with the
configured API key. Select that same project if these objects do not appear in
the portal. The ignored `data/runtime/openai_corpus_state.json` records only
file/store IDs, checksums, and public source metadata; it contains no key.

Attaching files to a vector store starts indexing and embedding, which may
incur charges. This is intentionally a separate command:

`backend/.venv/bin/python scripts/ingest_reports.py index --allow-model-indexing`

Do not run that command until the project owner decides to enable model use.
Until then, the OpenAI Files page should show two PDFs, while the vector store
exists with zero attached files and cannot answer report-search questions.

Both overview booklets state CC BY 3.0 IGO terms. Retain the catalog's
attribution when citing either report. Third-party figures or images inside a
report may have separate rights. The PDFs are source evidence, not a substitute
for current World Development Indicators API data; analytical claims need a
report date and should not be presented as causal findings.

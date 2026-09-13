# Agent instructions

Each role has a short, reviewable prompt in its own text file:

- `orchestrator.txt` routes the request and controls scope.
- `research.txt` gathers source-backed evidence.
- `structured_retrieval.txt` and `document_retrieval.txt` define the two
  narrow retrieval specialists.
- `synthesis.txt` produces the final comparison with limitations.
- `evaluation.txt` judges groundedness and citation quality.

Keeping prompts outside Python makes them easier to audit and revise. Treat
changes to these files like code changes and rerun the evaluations afterward.

# Publish AITP To PyPI

Use this runbook when you want to ship a new public `aitp` release.

## Preconditions

- working tree is clean
- `research/knowledge-hub/knowledge_hub/_version.py` has the intended semver
- the packaging contract and install docs for that version are already merged

## 1. Build prerequisites

```bash
python -m pip install --upgrade build twine
```

## 2. Run packaging verification

```bash
python research/knowledge-hub/runtime/scripts/run_dependency_contract_acceptance.py --json
```

This should produce a successful wheel and sdist validation for `aitp`.

## 3. Build distributions

```bash
python -m build research/knowledge-hub
```

Expected artifacts:

- `research/knowledge-hub/dist/aitp-<version>-py3-none-any.whl`
- `research/knowledge-hub/dist/aitp-<version>.tar.gz`

## 4. Check distribution metadata

```bash
python -m twine check research/knowledge-hub/dist/*
```

## 5. Upload

TestPyPI first when you want a dry run:

```bash
python -m twine upload --repository testpypi research/knowledge-hub/dist/*
```

Production PyPI:

```bash
python -m twine upload research/knowledge-hub/dist/*
```

## 6. Post-publish smoke check

In a clean Python 3.10+ environment:

```bash
python -m pip install aitp
aitp --version
aitp doctor
```

If the release is meant to unlock a runtime adapter path, also verify the
relevant adapter doc once against the published package.

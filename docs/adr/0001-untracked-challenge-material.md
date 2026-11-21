# ADR 0001: Keep private challenge material out of Git

Status: Accepted

## Context

The challenge repository contains public instructions. Private scoring material and downloaded candidate datasets do not belong in that history.

## Decision

Ignore `_internal/` and `datasets/` in Git. Candidates obtain the datasets from the source named in each challenge rather than committing local downloads.

## Consequences

The public repository does not accidentally distribute private scoring files or duplicate large datasets. A submission must still be committed under `submissions/`; the current ignore rule conflicts with that published workflow and is tracked separately.

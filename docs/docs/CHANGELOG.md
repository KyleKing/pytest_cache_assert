## Unreleased

## 1.2.1 (2022-02-27)

### Fix

- support Paths

## 1.2.0 (2022-02-27)

### Fix

- implement serializer before diffing
- failing tests and run doit

### Feat

- WIP serializer to support functions
- copier update. Add Github Actions

### Refactor

- use next generation attrs syntax

## 1.1.1 (2022-02-18)

### Fix

- show the changelog on PyPi

### Refactor

- drop 2021 prefix on tags

## 1.1.0 (2022-02-18)

### Refactor

- use beartype's typing imports

### Feat

- new assert_against_dict for in-memory comparison
- add support for comparing date-times

### Fix

- argument order issues in main
- datetime comparison logic

## 1.0.0 (2021-11-02)

### Fix

- correctly implement an optional fixture
- make config fixture optional

### Feat

- improve serialization

## 1.0.0rc0 (2021-11-02)

### Refactor

- code cleanup & documentation updates
- simplify merge_metadata logic
- serialize the func_args metadata recursively
- improve code quality of _raw_diff

### Feat

- support comparison of lists
- always write metadata as a list
- customizable cache directory
- support lists of dictionaries
- replace asterisk string with Wildcard enum
- support UUID in check_type

### Fix

- support dictionary keys with dots
- add CNAME for custom subdomain
- add missing check_imports file

## 0.1.0 (2021-10-31)

### Fix

- add tests and verify correctness of KeyRule
- use full name instead of custom indexing for cache
- use 2-spaces on JSON for pre-commit
- reduce stored metadata and check args
- re-run "poetry install" after entrypoint changes

### Feat

- implement key rules
- implement dictdiffer wrapper
- initialize decoupled differ and error message (WIP)
- use dictdiffer for quick fix for assertion messages
- resolve cache file name based on pytest metadata
- initial attempt at pytest plugin
- initialize package code and tests
- start with Readme (RDD)
- initialized project with copier

### Refactor

- rename checks to main
- rename check_assert to assert_against_cache & update README
- drop transformer and match_precision
- update notes and implementation plans

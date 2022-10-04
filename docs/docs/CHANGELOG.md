## Unreleased

### Fix

- move generic memory serializer after type lookup
- support in-memory assertion checking
- handle serializing MagicMock

### Refactor

- type ignore comment removal
- switch to BaseModel and Protocol

## 3.0.0 (2022-09-25)

### Feat

- add missing Wild.recur
- initiaiize Wild class and rename KeyRule to AssertRule
- add serializer to store only relative paths
- begin supporting string-based KeyRules!
- even better error messages
- start switch from dictdiffer to deepdiff
- start migration of attrs to pydantic
- migrate from pendulum to arrow

### Fix

- replace punq with dictionary config for failing tests
- remove casts because they break the tests
- cast to Interface and not Protocol
- resolve list regex matching rules
- determine how to match regex for nested paths
- continue to update tests for change in pattern syntax
- start removing the Wildcards and legacy KeyRules

### Refactor

- considered ssort, but blocked by https://github.com/bwhmather/ssort/issues/70
- last fix to restore mypy passing
- correct type ignore comments
- additional changes to pass type checks
- better support mypy
- add pydantic validators to custom types
- by default nest the caches by test file
- use suppress and remove loguru from pkg

## 2.0.0 (2022-05-01)

### Feat

- make numpy, pandas, and pydantic optionally serialize
- replace preconvert with custom registration logic
- **#3**: implement always_write
- initialize configurable list of converters
- implement DictDifferValidator
- implement LocalJSONCacheStore
- initialize new customization features

### Fix

- on first write use test_data for comparison
- order of flow for parsing diff result
- handling s3 serialization and remove returns
- s3 serialization needs to catch all objects
- try to fix s3 serialization
- remove type checking entirely for str
- str can't be type-checked
- resolve local test failures after initial refactor
- commitizen changed Cerberus dependency version

### Refactor

- always override the converter
- support an optional Path
- replace TEST_DATA_TYPE with Any
- switch to preconvert internally
- encapsulate JSON logic
- combine into single CacheStore representation
- separate functional logic from state for DictDiff
- remove optional validator argument
- decouple AssertConfig from plugin

## 1.3.5 (2022-03-03)

### Fix

- another attempt at fixing edge case for unknown class

## 1.3.4 (2022-03-03)

### Fix

- class is only in the type string

## 1.3.3 (2022-03-03)

### Fix

- handle edge cases with serializing classes

## 1.3.2 (2022-03-01)

### Fix

- debug recursive serialization for diffing
- handle one-level of recursion in lists

## 1.3.1 (2022-02-27)

### Fix

- correct type validation of AssertConfig ser_rules

## 1.3.0 (2022-02-27)

### Feat

- improve configurability with AssertConfig
- introduce internally configurable punq

## 1.2.1 (2022-02-27)

### Fix

- support Paths

## 1.2.0 (2022-02-27)

### Feat

- WIP serializer to support functions
- copier update. Add Github Actions

### Fix

- implement serializer before diffing
- failing tests and run doit

### Refactor

- use next generation attrs syntax

## 1.1.1 (2022-02-18)

### Fix

- show the changelog on PyPi

### Refactor

- drop 2021 prefix on tags

## 1.1.0 (2022-02-18)

### Feat

- new assert_against_dict for in-memory comparison
- add support for comparing date-times

### Fix

- argument order issues in main
- datetime comparison logic

### Refactor

- use beartype's typing imports

## 1.0.0 (2021-11-02)

### Feat

- improve serialization

### Fix

- correctly implement an optional fixture
- make config fixture optional

## 1.0.0rc0 (2021-11-02)

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

### Refactor

- code cleanup & documentation updates
- simplify merge_metadata logic
- serialize the func_args metadata recursively
- improve code quality of _raw_diff

## 0.1.0 (2021-10-31)

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

### Fix

- add tests and verify correctness of KeyRule
- use full name instead of custom indexing for cache
- use 2-spaces on JSON for pre-commit
- reduce stored metadata and check args
- re-run "poetry install" after entrypoint changes

### Refactor

- rename checks to main
- rename check_assert to assert_against_cache & update README
- drop transformer and match_precision
- update notes and implementation plans

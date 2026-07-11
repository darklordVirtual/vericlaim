# RFC 4180 CSV parse + write

*Subject area: Data / Serialization. Language: python. Vendorable bundle `82348dc9d933`.*

CSV looks trivial until a field contains a comma, a newline, or a quote -- then you need RFC 4180's quoting rules (wrap the field in double quotes and double any embedded quote), and a hand-rolled str.split(',') silently corrupts the data. This module implements a proper state-machine parser and a quoting writer with zero dependencies; the claim proves the parser agrees with Python's csv module and the writer round-trips, so you inherit a checked codec rather than a split-on-comma bug waiting to happen.

## Claim

<!-- claim:CLAIM-LIB-CSV-RFC4180-001 checks_matched -->
The vendored RFC 4180 CSV codec -- which parses and writes CSV DIRECTLY and never imports the csv module -- passes all 17 checks with 0 mismatches: parse(text) equals list(csv.reader(text)) on 12 inputs (quoted fields, embedded delimiters, embedded newlines, doubled quotes, empty fields, CRLF and LF records, and a trailing delimiter), and parse(format_rows(rows)) round-trips 5 record sets (including fields that require quoting). Verified value: <!-- v:CLAIM-LIB-CSV-RFC4180-001.checks_matched -->**17**
(`checks_matched`), backed by [`modules/csv_rfc4180/artifacts/csv_rfc4180.json`](../modules/csv_rfc4180/artifacts/csv_rfc4180.json).

## Vendor it

Ships `csv_rfc4180.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/82348dc9d93301c6f40b818703010d409a30be7704eeaaadb4ed298de0bb09cb --target .
```

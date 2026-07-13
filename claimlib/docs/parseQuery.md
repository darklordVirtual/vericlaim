# Query-string parse + stringify

*Subject area: TypeScript / URL & Web. Language: typescript. Vendorable bundle `ffe3a5ace645`.*

A URL query string is a '&'-separated list of 'key=value' pairs where keys can repeat and both sides are percent-encoded (with '+' historically meaning space in form submissions). parseQuery decodes each pair and collapses repeated keys into ordered arrays so 'a=1&a=3' becomes {a:["1","3"]}, while stringifyQuery reverses that with a deterministic sorted key order for stable, diffable output. Vendor it to read and build query strings consistently with zero dependencies; the claim proves the parse/serialize behaviour matches hand-written expectations and agrees with URLSearchParams, so you inherit a checked helper rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-PARSEQUERY-001 correct -->
The vendored TypeScript parseQuery / stringifyQuery pair produces the expected result on every one of a fixed 32-case reference battery whose expected values are written independently of the module (correct = 32, errors = 0): hand-written parse/stringify expectations (repeated keys -> ordered arrays such as parseQuery("?a=1&b=2&a=3") -> {a:["1","3"], b:"2"}, leading "?" handling, URI-decoding, empty-pair skipping, extra-"=" handling), stringify's stable sorted key order and form-style encoding, round-trip stability, and a per-key cross-check of decoding against the built-in URLSearchParams.getAll (an independent reference). Verified value: <!-- v:CLAIM-LIB-PARSEQUERY-001.correct -->**32**
(`correct`), backed by [`ts/parseQuery/artifacts/parseQuery.json`](../ts/parseQuery/artifacts/parseQuery.json).

## Vendor it

Ships `parseQuery.ts` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/ffe3a5ace645243959095f07ddb3e14a220a55eb58f6dc5221ce2c43ca193c03 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **WHATWG URL Living Standard (last updated 6 July 2026)** — URL Standard. [https://url.spec.whatwg.org/](https://url.spec.whatwg.org/)

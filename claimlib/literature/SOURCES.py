# SPDX-License-Identifier: Apache-2.0
"""Curated literature for claimlib -- the standards & papers the modules implement.

Each entry is a bibliographic record whose ``summary`` is hash-locked (see
claimlib/build_literature.py, which writes literature/<id>.json with a
summary_sha256, and claimlib/tests/test_literature.py, which re-verifies it).
Modules cite these ids in their MODULES.py ``references`` field; the build refuses
a reference that does not resolve here. This is Claim-Oriented Programming applied
to citations: the literature is committed, integrity-checked, and bound to code.
"""
from __future__ import annotations

SOURCES = [
    {
        "id": "fips-180-4",
        "title": "Secure Hash Standard (SHS)",
        "authors": ["NIST"],
        "publisher": "NIST",
        "year": 2015,
        "kind": "standard",
        "identifier": "FIPS PUB 180-4",
        "url": "https://csrc.nist.gov/publications/detail/fips/180/4/final",
        "summary": "The Secure Hash Standard specifies the SHA-1 and SHA-2 family "
                   "(SHA-224/256/384/512) of cryptographic hash functions, defining "
                   "the message padding, block processing, and round compression that "
                   "map an arbitrary message to a fixed-length digest.",
    },
    {
        "id": "rfc-2104",
        "title": "HMAC: Keyed-Hashing for Message Authentication",
        "authors": ["H. Krawczyk", "M. Bellare", "R. Canetti"],
        "publisher": "IETF",
        "year": 1997,
        "kind": "rfc",
        "identifier": "RFC 2104",
        "url": "https://www.rfc-editor.org/rfc/rfc2104",
        "summary": "Defines HMAC, a mechanism for message authentication using a "
                   "cryptographic hash together with a secret key, via the nested "
                   "inner/outer construction with the ipad and opad padding constants.",
    },
    {
        "id": "rfc-4231",
        "title": "Identifiers and Test Vectors for HMAC-SHA-224/256/384/512",
        "authors": ["M. Nystrom"],
        "publisher": "IETF",
        "year": 2005,
        "kind": "rfc",
        "identifier": "RFC 4231",
        "url": "https://www.rfc-editor.org/rfc/rfc4231",
        "summary": "Provides object identifiers and a set of official test vectors for "
                   "HMAC built on the SHA-2 hash functions, used to validate "
                   "interoperable implementations.",
    },
    {
        "id": "rfc-4226",
        "title": "HOTP: An HMAC-Based One-Time Password Algorithm",
        "authors": ["D. M'Raihi", "M. Bellare", "F. Hoornaert", "D. Naccache", "O. Ranen"],
        "publisher": "IETF",
        "year": 2005,
        "kind": "rfc",
        "identifier": "RFC 4226",
        "url": "https://www.rfc-editor.org/rfc/rfc4226",
        "summary": "Specifies HOTP, an event-based one-time-password algorithm that "
                   "HMACs a moving counter with a shared secret and applies dynamic "
                   "truncation to produce a short numeric code, with reference vectors.",
    },
    {
        "id": "rfc-6238",
        "title": "TOTP: Time-Based One-Time Password Algorithm",
        "authors": ["D. M'Raihi", "S. Machani", "M. Pei", "J. Rydell"],
        "publisher": "IETF",
        "year": 2011,
        "kind": "rfc",
        "identifier": "RFC 6238",
        "url": "https://www.rfc-editor.org/rfc/rfc6238",
        "summary": "Extends HOTP to a time-based variant by replacing the counter with "
                   "the number of fixed time steps since an epoch, yielding codes that "
                   "rotate automatically; includes SHA-1/256/512 test vectors.",
    },
    {
        "id": "rfc-8018",
        "title": "PKCS #5: Password-Based Cryptography Specification Version 2.1",
        "authors": ["K. Moriarty", "B. Kaliski", "A. Rusch"],
        "publisher": "IETF",
        "year": 2017,
        "kind": "rfc",
        "identifier": "RFC 8018",
        "url": "https://www.rfc-editor.org/rfc/rfc8018",
        "summary": "Defines PBKDF2, a password-based key derivation function that "
                   "iterates a pseudorandom function (typically HMAC) over a password "
                   "and salt to stretch a low-entropy password into a cryptographic key.",
    },
    {
        "id": "rfc-6070",
        "title": "PKCS #5 PBKDF2 Test Vectors",
        "authors": ["S. Josefsson"],
        "publisher": "IETF",
        "year": 2011,
        "kind": "rfc",
        "identifier": "RFC 6070",
        "url": "https://www.rfc-editor.org/rfc/rfc6070",
        "summary": "Provides official PBKDF2-HMAC-SHA1 test vectors for a range of "
                   "iteration counts and output lengths, used to validate "
                   "implementations of the RFC 8018 key derivation function.",
    },
    {
        "id": "rfc-5869",
        "title": "HMAC-based Extract-and-Expand Key Derivation Function (HKDF)",
        "authors": ["H. Krawczyk", "P. Eronen"],
        "publisher": "IETF",
        "year": 2010,
        "kind": "rfc",
        "identifier": "RFC 5869",
        "url": "https://www.rfc-editor.org/rfc/rfc5869",
        "summary": "Specifies HKDF, a two-step extract-then-expand key derivation "
                   "function built on HMAC: extract concentrates input entropy into a "
                   "pseudorandom key, and expand stretches it into output keying "
                   "material with domain-separating context.",
    },
    {
        "id": "rfc-7468",
        "title": "Textual Encodings of PKIX, PKCS, and CMS Structures",
        "authors": ["S. Josefsson", "S. Leonard"],
        "publisher": "IETF",
        "year": 2015,
        "kind": "rfc",
        "identifier": "RFC 7468",
        "url": "https://www.rfc-editor.org/rfc/rfc7468",
        "summary": "Standardizes the PEM textual encoding used to wrap DER-encoded "
                   "certificates, keys, and CMS structures: base64 of the binary "
                   "content between BEGIN/END lines with a labeled encapsulation "
                   "boundary.",
    },
    {
        "id": "rfc-7469",
        "title": "Public Key Pinning Extension for HTTP (HPKP)",
        "authors": ["C. Evans", "C. Palmer", "R. Sleevi"],
        "publisher": "IETF",
        "year": 2015,
        "kind": "rfc",
        "identifier": "RFC 7469",
        "url": "https://www.rfc-editor.org/rfc/rfc7469",
        "summary": "Defines public key pinning, where a client remembers the SHA-256 "
                   "hash of a server's Subject Public Key Info (base64-encoded) and "
                   "rejects future connections whose certificate chain does not present "
                   "a matching pinned key.",
    },
    {
        "id": "rfc-5280",
        "title": "Internet X.509 Public Key Infrastructure Certificate and CRL Profile",
        "authors": ["D. Cooper", "S. Santesson", "S. Farrell", "et al."],
        "publisher": "IETF",
        "year": 2008,
        "kind": "rfc",
        "identifier": "RFC 5280",
        "url": "https://www.rfc-editor.org/rfc/rfc5280",
        "summary": "Profiles the X.509 v3 certificate and CRL formats and the "
                   "certification-path validation algorithm (validity windows, name "
                   "chaining, basic constraints, key usage) that underpins TLS and "
                   "mutual-TLS authentication.",
    },
    {
        "id": "rfc-8446",
        "title": "The Transport Layer Security (TLS) Protocol Version 1.3",
        "authors": ["E. Rescorla"],
        "publisher": "IETF",
        "year": 2018,
        "kind": "rfc",
        "identifier": "RFC 8446",
        "url": "https://www.rfc-editor.org/rfc/rfc8446",
        "summary": "Specifies TLS 1.3, including the handshake, the HKDF-based key "
                   "schedule, and optional client authentication via certificates "
                   "(mutual TLS), where each peer proves possession of the private key "
                   "for a presented certificate.",
    },
    {
        "id": "lamport-1979",
        "title": "Constructing Digital Signatures from a One-Way Function",
        "authors": ["Leslie Lamport"],
        "publisher": "SRI International (Technical Report CSL-98)",
        "year": 1979,
        "kind": "paper",
        "identifier": "SRI CSL-98",
        "url": "https://www.microsoft.com/en-us/research/publication/constructing-digital-signatures-one-way-function/",
        "summary": "Introduces the Lamport one-time signature, which builds a digital "
                   "signature scheme from nothing but a one-way (hash) function by "
                   "revealing pre-images of committed hash values; its security rests "
                   "only on hash preimage resistance, making it quantum-resistant.",
    },
    {
        "id": "rfc-8391",
        "title": "XMSS: eXtended Merkle Signature Scheme",
        "authors": ["A. Huelsing", "D. Butin", "S. Gazdag", "J. Rijneveld", "A. Mohaisen"],
        "publisher": "IETF",
        "year": 2018,
        "kind": "rfc",
        "identifier": "RFC 8391",
        "url": "https://www.rfc-editor.org/rfc/rfc8391",
        "summary": "Specifies XMSS, a stateful hash-based signature scheme that combines "
                   "Winternitz one-time signatures under a Merkle tree to sign many "
                   "messages; being hash-based, it is a post-quantum (quantum-resistant) "
                   "signature standard.",
    },
    {
        "id": "fips-203",
        "title": "Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM)",
        "authors": ["NIST"],
        "publisher": "NIST",
        "year": 2024,
        "kind": "standard",
        "identifier": "FIPS 203",
        "url": "https://csrc.nist.gov/pubs/fips/203/final",
        "summary": "The NIST post-quantum standard for key encapsulation (ML-KEM, based "
                   "on CRYSTALS-Kyber), whose security relies on the hardness of "
                   "module-lattice problems believed to resist attack by quantum "
                   "computers; used to establish shared secrets.",
    },
    {
        "id": "fips-204",
        "title": "Module-Lattice-Based Digital Signature Standard (ML-DSA)",
        "authors": ["NIST"],
        "publisher": "NIST",
        "year": 2024,
        "kind": "standard",
        "identifier": "FIPS 204",
        "url": "https://csrc.nist.gov/pubs/fips/204/final",
        "summary": "The NIST post-quantum digital signature standard (ML-DSA, based on "
                   "CRYSTALS-Dilithium), a module-lattice signature scheme intended to "
                   "replace RSA/ECDSA signatures against a quantum adversary.",
    },
    {
        "id": "fips-205",
        "title": "Stateless Hash-Based Digital Signature Standard (SLH-DSA)",
        "authors": ["NIST"],
        "publisher": "NIST",
        "year": 2024,
        "kind": "standard",
        "identifier": "FIPS 205",
        "url": "https://csrc.nist.gov/pubs/fips/205/final",
        "summary": "The NIST post-quantum standard for stateless hash-based signatures "
                   "(SLH-DSA, based on SPHINCS+), whose security depends only on the "
                   "properties of its underlying hash function, generalizing the "
                   "Lamport/Merkle idea to a practical many-time signature.",
    },
    {
        "id": "nist-csf-2.0",
        "title": "The NIST Cybersecurity Framework (CSF) 2.0",
        "authors": ["NIST"],
        "publisher": "NIST",
        "year": 2024,
        "kind": "framework",
        "identifier": "NIST CSWP 29",
        "url": "https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final",
        "summary": "Version 2.0 of the NIST Cybersecurity Framework organizes cyber "
                   "risk management into six Functions -- Govern, Identify, Protect, "
                   "Detect, Respond, and Recover -- each decomposed into Categories and "
                   "Subcategories used to assess and communicate security posture.",
    },
    {
        "id": "nis2-directive",
        "title": "Directive (EU) 2022/2555 (NIS2) on measures for a high common level of cybersecurity",
        "authors": ["European Parliament and Council"],
        "publisher": "Official Journal of the European Union",
        "year": 2022,
        "kind": "regulation",
        "identifier": "Directive (EU) 2022/2555",
        "url": "https://eur-lex.europa.eu/eli/dir/2022/2555/oj",
        "summary": "The EU NIS2 Directive raises the baseline of cybersecurity across "
                   "essential and important entities; its Article 21 enumerates minimum "
                   "risk-management measures (risk analysis, incident handling, business "
                   "continuity, supply chain security, cryptography, MFA, and more).",
    },
    {
        "id": "aicpa-tsc-2017",
        "title": "Trust Services Criteria for Security, Availability, Processing Integrity, "
                 "Confidentiality, and Privacy",
        "authors": ["AICPA Assurance Services Executive Committee"],
        "publisher": "AICPA",
        "year": 2017,
        "kind": "framework",
        "identifier": "AICPA TSP Section 100 (2017, rev. 2022)",
        "url": "https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022",
        "summary": "The AICPA Trust Services Criteria are the control criteria used in SOC 2 "
                   "examinations, organized into five categories -- Security, Availability, "
                   "Processing Integrity, Confidentiality, and Privacy -- where Security is "
                   "expressed as the nine Common Criteria series (CC1 through CC9).",
    },
    {
        "id": "iso-27001-2022",
        "title": "Information security, cybersecurity and privacy protection -- "
                 "Information security management systems -- Requirements",
        "authors": ["ISO/IEC JTC 1/SC 27"],
        "publisher": "ISO/IEC",
        "year": 2022,
        "kind": "standard",
        "identifier": "ISO/IEC 27001:2022",
        "url": "https://www.iso.org/standard/27001",
        "summary": "The international standard for information security management systems "
                   "(ISMS); its 2022 revision restructured Annex A into 93 controls across "
                   "four themes -- Organizational (37), People (8), Physical (14), and "
                   "Technological (34).",
    },
    {
        "id": "pci-dss-4.0",
        "title": "Payment Card Industry Data Security Standard, Version 4.0",
        "authors": ["PCI Security Standards Council"],
        "publisher": "PCI SSC",
        "year": 2022,
        "kind": "standard",
        "identifier": "PCI DSS v4.0",
        "url": "https://www.pcisecuritystandards.org/document_library/",
        "summary": "The security standard for organizations that store, process, or transmit "
                   "payment card data; version 4.0 defines twelve requirements grouped under "
                   "six goals, from building a secure network to maintaining an information "
                   "security policy.",
    },
    {
        "id": "benford-1938",
        "title": "The Law of Anomalous Numbers",
        "authors": ["Frank Benford"],
        "publisher": "Proceedings of the American Philosophical Society, 78(4)",
        "year": 1938,
        "kind": "paper",
        "identifier": "Proc. Am. Philos. Soc. 78(4):551-572",
        "url": "https://www.jstor.org/stable/984802",
        "summary": "Benford's empirical observation that in many natural datasets the leading "
                   "digit d occurs with frequency log10(1 + 1/d); the distribution is now a "
                   "standard forensic-accounting screen for detecting fabricated or "
                   "manipulated numeric data.",
    },
    {
        "id": "aicpa-audit-sampling",
        "title": "Audit Sampling (AICPA Audit Guide)",
        "authors": ["AICPA"],
        "publisher": "AICPA",
        "year": 2019,
        "kind": "framework",
        "identifier": "AICPA Audit Guide: Audit Sampling",
        "url": "https://www.aicpa-cima.com/cpe-learning/publication/audit-sampling-audit-guide",
        "summary": "The AICPA guide to statistical and non-statistical audit sampling; its "
                   "Poisson reliability factors let an auditor size an attribute sample so "
                   "that, at a chosen confidence, the sample bounds the true deviation rate "
                   "below the tolerable rate.",
    },
    {
        "id": "cvss-v3.1",
        "title": "Common Vulnerability Scoring System version 3.1: Specification Document",
        "authors": ["FIRST.Org, Inc."],
        "publisher": "FIRST",
        "year": 2019,
        "kind": "specification",
        "identifier": "CVSS v3.1 Specification Document (Revision 1, June 2019)",
        "url": "https://www.first.org/cvss/v3.1/specification-document",
        "summary": "Defines the CVSS v3.1 open framework for scoring the severity of software "
                   "vulnerabilities via Base, Temporal, and Environmental metric groups. "
                   "Specifies the exact base-score equations, including the Impact and "
                   "Exploitability sub-scores, the changed/unchanged Scope (S) handling that "
                   "alters coefficients and score combination, and the Roundup function "
                   "introduced to eliminate floating-point scoring inconsistencies seen in v3.0. "
                   "Base scores computed per this document are the reference values published by "
                   "FIRST and used by NVD.",
    },
    {
        "id": "haber-1991",
        "title": "How to Time-Stamp a Digital Document",
        "authors": ["Stuart Haber", "W. Scott Stornetta"],
        "publisher": "Springer (Journal of Cryptology)",
        "year": 1991,
        "kind": "paper",
        "identifier": "Journal of Cryptology, vol. 3, no. 2, pp. 99-111; doi:10.1007/BF00196791",
        "url": "https://doi.org/10.1007/BF00196791",
        "summary": "Introduces linked time-stamping: each new record incorporates a cryptographic "
                   "hash of the previous record, forming a chain in which back-dating, "
                   "forward-dating, or altering any entry invalidates every subsequent hash. This "
                   "is the canonical construction for tamper-evident append-only hash-chained "
                   "logs and a direct ancestor of blockchain data structures.",
    },
    {
        "id": "merkle-1988",
        "title": "A Digital Signature Based on a Conventional Encryption Function",
        "authors": ["Ralph C. Merkle"],
        "publisher": "Springer",
        "year": 1988,
        "kind": "paper",
        "identifier": "Advances in Cryptology — CRYPTO '87, LNCS 293, pp. 369-378; doi:10.1007/3-540-48184-2_32",
        "url": "https://doi.org/10.1007/3-540-48184-2_32",
        "summary": "Introduces tree authentication, now known as the Merkle tree: a binary tree "
                   "of hash values whose root commits to a set of leaf values, so that any single "
                   "leaf can be authenticated against the root using only a logarithmic-length "
                   "path of sibling hashes. This is the foundational construction for inclusion "
                   "proofs verified against a committed root.",
    },
    {
        "id": "rfc-6962",
        "title": "Certificate Transparency",
        "authors": ["Ben Laurie", "Adam Langley", "Emilia Kasper"],
        "publisher": "IETF",
        "year": 2013,
        "kind": "rfc",
        "identifier": "RFC 6962",
        "url": "https://www.rfc-editor.org/info/rfc6962",
        "summary": "Specifies Certificate Transparency logs, including the precise binary Merkle "
                   "Tree Hash construction over SHA-256 with distinct leaf (0x00) and "
                   "interior-node (0x01) prefixes, and the recursive algorithms for Merkle audit "
                   "paths (inclusion proofs) and consistency proofs against a signed tree head. "
                   "This is the de facto reference definition of SHA-256 Merkle inclusion proofs "
                   "used by deployed CT logs. Experimental status; obsoleted by RFC 9162 (CT "
                   "2.0), which retains the same tree and proof definitions.",
    },
    {
        "id": "incits-359-2012",
        "title": "Information technology — Role Based Access Control",
        "authors": ["INCITS"],
        "publisher": "ANSI/INCITS",
        "year": 2012,
        "kind": "standard",
        "identifier": "INCITS 359-2012 (R2022)",
        "url": "https://webstore.ansi.org/standards/incits/incits3592012r2022",
        "summary": "The American National Standard for Role Based Access Control, revising the "
                   "original INCITS 359-2004 adoption of the NIST RBAC model. Defines the RBAC "
                   "Reference Model — users, roles, permissions, operations, objects, and role "
                   "hierarchies — together with static and dynamic separation-of-duty constraint "
                   "relations (SSD/DSD), and the System and Administrative Functional "
                   "Specification required of conforming RBAC systems. SoD findings in a "
                   "role/permission access matrix are evaluated against these constraint "
                   "relations.",
    },
    {
        "id": "saltzer-1975",
        "title": "The Protection of Information in Computer Systems",
        "authors": ["Jerome H. Saltzer", "Michael D. Schroeder"],
        "publisher": "IEEE",
        "year": 1975,
        "kind": "paper",
        "identifier": "Proceedings of the IEEE, vol. 63, no. 9, pp. 1278-1308; doi:10.1109/PROC.1975.9939",
        "url": "https://doi.org/10.1109/PROC.1975.9939",
        "summary": "Tutorial survey of architectural mechanisms for protecting stored information "
                   "that states the eight classic secure-design principles, including least "
                   "privilege, fail-safe defaults, complete mediation, and separation of "
                   "privilege. The principle of least privilege — every program and user "
                   "operating with the fewest privileges necessary — as applied in access-control "
                   "audits originates in this paper.",
    },
    {
        "id": "rfc-4648",
        "title": "The Base16, Base32, and Base64 Data Encodings",
        "authors": ["S. Josefsson"],
        "publisher": "IETF",
        "year": 2006,
        "kind": "rfc",
        "identifier": "RFC 4648",
        "url": "https://www.rfc-editor.org/rfc/rfc4648",
        "summary": "Specifies the base16, base32, and base64 encodings, including the standard "
                   "base32 alphabet (A-Z, 2-7) in section 6, the '=' padding rules mapping 5-byte "
                   "input groups to 8-symbol output blocks, and handling of non-alphabet "
                   "characters. Section 10 provides the canonical test vectors (e.g. "
                   "BASE32(\"foobar\") = \"MZXW6YTBOI======\") that conforming implementations "
                   "must reproduce. Obsoletes RFC 3548.",
    },
    {
        "id": "rfc-6901",
        "title": "JavaScript Object Notation (JSON) Pointer",
        "authors": ["P. Bryan, Ed.", "K. Zyp", "M. Nottingham, Ed."],
        "publisher": "IETF",
        "year": 2013,
        "kind": "rfc",
        "identifier": "RFC 6901",
        "url": "https://www.rfc-editor.org/rfc/rfc6901",
        "summary": "Defines JSON Pointer, a string syntax of '/'-separated reference tokens for "
                   "identifying a specific value within a JSON document. Specifies the escape "
                   "sequences '~0' for '~' and '~1' for '/', evaluation semantics for object "
                   "member and array index resolution (including the rejection of leading zeros "
                   "in indices), and error conditions for non-existent references. Section 5 "
                   "gives the worked example document and pointer/result pairs used as the "
                   "conformance vectors.",
    },
    {
        "id": "rfc-4180",
        "title": "Common Format and MIME Type for Comma-Separated Values (CSV) Files",
        "authors": ["Y. Shafranovich"],
        "publisher": "IETF",
        "year": 2005,
        "kind": "rfc",
        "identifier": "RFC 4180",
        "url": "https://www.rfc-editor.org/rfc/rfc4180",
        "summary": "Documents the de facto CSV format as an ABNF grammar: CRLF-delimited records "
                   "of comma-separated fields, an optional header line, and double-quote "
                   "enclosure for fields containing commas, quotes, or line breaks, with embedded "
                   "quotes escaped by doubling. Registers the text/csv MIME type. Informational "
                   "status; it is the reference grammar for interoperable CSV parsing and "
                   "writing.",
    },
    {
        "id": "protobuf-encoding",
        "title": "Encoding | Protocol Buffers Documentation",
        "authors": ["Google"],
        "publisher": "Google",
        "year": 2026,
        "kind": "specification",
        "identifier": "protobuf.dev/programming-guides/encoding",
        "url": "https://protobuf.dev/programming-guides/encoding/",
        "summary": "The Protocol Buffers wire-format specification. Defines varints as base-128 "
                   "little-endian encodings of unsigned integers in 7-bit groups with a "
                   "most-significant continuation bit (one to ten bytes for 64-bit values), with "
                   "the worked example 150 -> 0x96 0x01. Also defines ZigZag encoding for signed "
                   "sint32/sint64 fields, mapping a positive integer p to 2*p and a negative "
                   "integer n to 2*|n| - 1 so small magnitudes stay small on the wire.",
    },
    {
        "id": "dwarf-5",
        "title": "DWARF Debugging Information Format Version 5",
        "authors": ["DWARF Debugging Information Format Committee"],
        "publisher": "DWARF Debugging Information Format Committee",
        "year": 2017,
        "kind": "standard",
        "identifier": "DWARF Version 5",
        "url": "https://dwarfstd.org/dwarf5std.html",
        "summary": "The DWARF 5 debugging information format standard, published February 2017. "
                   "Section 7.6 defines LEB128 (Little-Endian Base 128) variable-length integer "
                   "encoding in both unsigned (ULEB128) and signed (SLEB128) forms, including the "
                   "encode/decode algorithms and tables of reference encodings that LEB128 "
                   "implementations reproduce. LEB128 is the pseudo-standard cited by varint "
                   "implementations beyond DWARF itself.",
    },
    {
        "id": "ieee-802-3",
        "title": "IEEE Standard for Ethernet",
        "authors": ["IEEE"],
        "publisher": "IEEE",
        "year": 2022,
        "kind": "standard",
        "identifier": "IEEE 802.3-2022",
        "url": "https://standards.ieee.org/ieee/802.3/10422/",
        "summary": "The Ethernet standard covering MAC and physical-layer operation from 1 Mb/s "
                   "to 400 Gb/s. Clause 3.2.9 defines the 32-bit Frame Check Sequence and its "
                   "degree-32 generator polynomial (x^32 + x^26 + x^23 + x^22 + x^16 + x^12 + "
                   "x^11 + x^10 + x^8 + x^7 + x^5 + x^4 + x^2 + x + 1, i.e. 0x04C11DB7), computed "
                   "with all-ones preset and complemented result. The bit-reflected form of this "
                   "polynomial, 0xEDB88320, is the constant used by LSB-first CRC-32 "
                   "implementations.",
    },
    {
        "id": "rfc-1952",
        "title": "GZIP file format specification version 4.3",
        "authors": ["P. Deutsch"],
        "publisher": "IETF",
        "year": 1996,
        "kind": "rfc",
        "identifier": "RFC 1952",
        "url": "https://www.rfc-editor.org/rfc/rfc1952",
        "summary": "Specifies the gzip file format, whose integrity check is the CRC-32 of ISO "
                   "3309 / ITU-T V.42. Section 8 gives reference sample code for the "
                   "table-driven, reflected CRC-32 algorithm: 256-entry table built from "
                   "polynomial 0xEDB88320, initial value 0xFFFFFFFF, and final XOR with "
                   "0xFFFFFFFF. This is the concrete algorithmic reference for the ubiquitous "
                   "zip/gzip/PNG/Ethernet CRC-32.",
    },
    {
        "id": "luhn-1960",
        "title": "Computer for Verifying Numbers",
        "authors": ["Hans P. Luhn"],
        "publisher": "United States Patent Office",
        "year": 1960,
        "kind": "paper",
        "identifier": "U.S. Patent 2,950,048",
        "url": "https://patents.google.com/patent/US2950048A/en",
        "summary": "Luhn's patent (filed 1954, granted 23 August 1960) describes a hand-operated "
                   "device for computing and verifying a mod-10 check digit: every second digit "
                   "from the right is doubled, digits above 9 are reduced by 9, and the total "
                   "must be divisible by 10. This 'double-add-double' formula is the origin of "
                   "the Luhn algorithm used for payment card numbers, IMEIs, and many national "
                   "identifiers. It detects all single-digit errors and most adjacent "
                   "transpositions but provides no cryptographic integrity.",
    },
    {
        "id": "iso-7812-1",
        "title": "Identification cards — Identification of issuers — Part 1: Numbering system",
        "authors": ["ISO"],
        "publisher": "ISO",
        "year": 2017,
        "kind": "standard",
        "identifier": "ISO/IEC 7812-1:2017",
        "url": "https://www.iso.org/standard/70484.html",
        "summary": "Specifies the numbering system for identification card issuers: the issuer "
                   "identification number (IIN) and the structure of the primary account number "
                   "(PAN), whose final digit is a check digit. Normative Annex B specifies the "
                   "Luhn formula for computing modulus-10 double-add-double check digits, making "
                   "this standard the formal specification of the Luhn check for card numbers.",
    },
    {
        "id": "iso-13616-2020",
        "title": "Financial services — International bank account number (IBAN) — Part 1: "
                 "Structure of the IBAN",
        "authors": ["ISO"],
        "publisher": "ISO",
        "year": 2020,
        "kind": "standard",
        "identifier": "ISO 13616-1:2020",
        "url": "https://www.iso.org/standard/81090.html",
        "summary": "Defines the structure of the International Bank Account Number: a two-letter "
                   "ISO 3166-1 country code, two check digits, and a country-specific BBAN of up "
                   "to 30 alphanumeric characters. Specifies the electronic format (no "
                   "separators, upper case) and requires the check digits to be computed and "
                   "validated with the MOD 97-10 scheme of ISO/IEC 7064.",
    },
    {
        "id": "iso-7064",
        "title": "Information technology — Security techniques — Check character systems",
        "authors": ["ISO"],
        "publisher": "ISO",
        "year": 2003,
        "kind": "standard",
        "identifier": "ISO/IEC 7064:2003",
        "url": "https://www.iso.org/standard/31531.html",
        "summary": "Specifies a family of pure and hybrid check character systems that protect "
                   "strings against human copying and keying errors, including MOD 97-10 for "
                   "numeric strings. Under MOD 97-10, letters are mapped to two-digit values "
                   "(A=10 .. Z=35), the string is read as a base-10 integer, and a valid string "
                   "satisfies integer mod 97 == 1; this is the check computation behind IBAN "
                   "check digits.",
    },
    {
        "id": "ieee-754-2019",
        "title": "IEEE Standard for Floating-Point Arithmetic",
        "authors": ["IEEE"],
        "publisher": "IEEE",
        "year": 2019,
        "kind": "standard",
        "identifier": "IEEE Std 754-2019",
        "url": "https://ieeexplore.ieee.org/document/8766229",
        "summary": "Specifies interchange and arithmetic formats and rounding for binary and "
                   "decimal floating-point arithmetic. Defines the rounding-direction attribute "
                   "roundTiesToEven — round to the nearest representable value, with ties going "
                   "to the value with an even least-significant digit — as the default; this is "
                   "the 'banker's rounding' (ROUND_HALF_EVEN) rule, which avoids the systematic "
                   "upward bias of round-half-up when summing rounded amounts.",
    },
    {
        "id": "balinski-2001",
        "title": "Fair Representation: Meeting the Ideal of One Man, One Vote",
        "authors": ["Michel L. Balinski", "H. Peyton Young"],
        "publisher": "Brookings Institution Press",
        "year": 2001,
        "kind": "book",
        "identifier": "ISBN 978-0-8157-0111-8 (2nd ed.; 1st ed. Yale University Press, 1982)",
        "url": "https://www.brookings.edu/books/fair-representation/",
        "summary": "The standard mathematical treatment of apportionment: dividing a fixed "
                   "integer total into parts proportional to weights. Defines and analyzes "
                   "Hamilton's largest-remainder method — give each part the floor of its exact "
                   "proportional share, then distribute the leftover units to the parts with the "
                   "largest fractional remainders — which by construction always sums exactly to "
                   "the total. Also establishes the method's properties and paradoxes relative to "
                   "divisor methods.",
    },
    {
        "id": "brreg-orgnr",
        "title": "Om organisasjonsnummeret",
        "authors": ["Brønnøysundregistrene"],
        "publisher": "Brønnøysundregistrene",
        "year": 2023,
        "kind": "specification",
        "identifier": "Brønnøysundregistrene: Om organisasjonsnummeret (rev. 13 Dec 2023)",
        "url": "https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsnummeret/",
        "summary": "The Norwegian registry authority's specification of the nine-digit "
                   "organisasjonsnummer and its weighted modulus-11 check digit. The first eight "
                   "digits are multiplied by the weights 3, 2, 7, 6, 5, 4, 3, 2 (from the first "
                   "digit), the products are summed, and the ninth digit is 11 minus the sum's "
                   "remainder modulo 11; a remainder of 0 gives check digit 0, and a remainder of "
                   "1 (which would require check digit 10) means no valid organisation number "
                   "exists for that payload.",
    },
    {
        "id": "pacioli-1494",
        "title": "Summa de arithmetica, geometria, proportioni et proportionalita",
        "authors": ["Luca Pacioli"],
        "publisher": "Paganino de Paganini (Venice)",
        "year": 1494,
        "kind": "book",
        "identifier": "Venice: Paganino de Paganini, 10–20 November 1494 (LCCN 49036374)",
        "url": "https://www.loc.gov/item/49036374/",
        "summary": "Pacioli's mathematical compendium whose treatise 'Particularis de computis et "
                   "scripturis' is the first printed exposition of double-entry (Venetian) "
                   "bookkeeping. It codifies the system in which every transaction is recorded as "
                   "equal debits and credits across journal and ledger, so that total debits "
                   "equal total credits and the ledger can be proved by a trial balance. These "
                   "balance invariants are exactly what a double-entry integrity check enforces.",
    },
    {
        "id": "semver-2.0.0",
        "title": "Semantic Versioning 2.0.0",
        "authors": ["Tom Preston-Werner"],
        "publisher": "semver.org",
        "year": 2013,
        "kind": "specification",
        "identifier": "SemVer 2.0.0",
        "url": "https://semver.org/spec/v2.0.0.html",
        "summary": "Specifies the MAJOR.MINOR.PATCH version format with optional dot-separated "
                   "pre-release identifiers and build metadata. Section 10 requires build "
                   "metadata to be ignored when determining precedence, and section 11 defines "
                   "the precedence algorithm: numeric comparison of the core triple, a "
                   "pre-release version ranking below its associated normal version, and "
                   "left-to-right comparison of pre-release identifiers where numeric identifiers "
                   "compare numerically, alphanumeric identifiers compare in ASCII order, numeric "
                   "ranks below alphanumeric, and a larger identifier set wins when all preceding "
                   "identifiers are equal.",
    },
    {
        "id": "rfc-2697",
        "title": "A Single Rate Three Color Marker",
        "authors": ["Juha Heinanen", "Roch Guerin"],
        "publisher": "IETF",
        "year": 1999,
        "kind": "rfc",
        "identifier": "RFC 2697",
        "url": "https://www.rfc-editor.org/info/rfc2697",
        "summary": "Defines the single rate Three Color Marker (srTCM), which meters an IP packet "
                   "stream using two token buckets C and E that share the common rate CIR and "
                   "have capacities CBS and EBS. The token counts Tc and Te start full and are "
                   "updated CIR times per second under a strict priority rule: Tc is incremented "
                   "by one if below CBS, else Te is incremented by one if below EBS, else neither "
                   "— so each count is capped at its bucket capacity (the token-bucket capacity "
                   "invariant). Packets are marked green, yellow, or red depending on whether "
                   "sufficient tokens are available in C, then E. Published as an Informational "
                   "RFC, it is the canonical IETF specification of srTCM token-bucket metering "
                   "over a chronological trace of packet arrivals.",
    },
    {
        "id": "brooker-2015",
        "title": "Exponential Backoff And Jitter",
        "authors": ["Marc Brooker"],
        "publisher": "Amazon Web Services",
        "year": 2015,
        "kind": "paper",
        "identifier": "AWS Architecture Blog, 4 March 2015",
        "url": "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/",
        "summary": "Analyzes retry storms under capped exponential backoff for "
                   "optimistic-concurrency clients and shows via simulation that adding "
                   "randomness to backoff reduces contention, total client work, and completion "
                   "time. Defines the Full Jitter strategy as sleep = random_between(0, min(cap, "
                   "base * 2^attempt)), i.e. the delay is drawn uniformly from [0, capped "
                   "exponential], and compares it against Equal Jitter and Decorrelated Jitter. "
                   "This post is the origin of the 'full jitter' terminology and formula used by "
                   "retry libraries.",
    },
    {
        "id": "google-sre-2016",
        "title": "Site Reliability Engineering: How Google Runs Production Systems",
        "authors": ["Betsy Beyer", "Chris Jones", "Jennifer Petoff", "Niall Richard Murphy"],
        "publisher": "O'Reilly Media",
        "year": 2016,
        "kind": "book",
        "identifier": "ISBN 978-1-491-92912-4",
        "url": "https://sre.google/sre-book/table-of-contents/",
        "summary": "Google's SRE book defines the discipline's core quantitative machinery: "
                   "availability as the ratio of successful requests to total requests, service "
                   "level indicators and objectives (Chapter 4, 'Service Level Objectives'), and "
                   "the error budget as 1 minus the availability target (Chapter 3, 'Embracing "
                   "Risk'). The error budget is spent by failed requests and the remaining budget "
                   "gates release velocity. These chapters are the canonical source of the "
                   "textbook SLO and error-budget arithmetic.",
    },
    {
        "id": "mattson-1970",
        "title": "Evaluation Techniques for Storage Hierarchies",
        "authors": ["Richard L. Mattson", "Jan Gecsei", "Donald R. Slutz", "Irving L. Traiger"],
        "publisher": "IBM",
        "year": 1970,
        "kind": "paper",
        "identifier": "IBM Systems Journal, vol. 9, no. 2, pp. 78-117, doi:10.1147/sj.92.0078",
        "url": "https://doi.org/10.1147/sj.92.0078",
        "summary": "Introduces stack processing, a one-pass technique for evaluating demand-paged "
                   "storage hierarchies, and formalizes the class of stack replacement algorithms "
                   "with the inclusion property. Least-recently-used (LRU) replacement is the "
                   "canonical stack algorithm analyzed: pages are ordered by recency of reference "
                   "and the least recently used page is evicted when a fixed-capacity level is "
                   "full. This paper is the standard scholarly reference for LRU eviction "
                   "semantics and its capacity-inclusion behavior.",
    },
    {
        "id": "apdex-spec",
        "title": "Application Performance Index — Apdex Technical Specification",
        "authors": ["Apdex Alliance"],
        "publisher": "Apdex Alliance",
        "year": 2007,
        "kind": "specification",
        "identifier": "Apdex Technical Specification, Version 1.1 (22 January 2007)",
        "url": "https://www.apdex.org/wp-content/uploads/2020/09/ApdexTechnicalSpecificationV11_000.pdf",
        "summary": "Defines Apdex, an index from 0 to 1 measuring user satisfaction with "
                   "application response time. Samples are partitioned into Satisfied, "
                   "Tolerating, and Frustrated zones by a target threshold T and a frustration "
                   "threshold F = 4T, and the index is computed as Apdex_T = (Satisfied count + "
                   "Tolerating count / 2) / Total samples. The specification also defines "
                   "report-group requirements and how the index and its threshold must be "
                   "displayed (e.g. 0.85 [4.0]).",
    },
    {
        "id": "hyndman-1996",
        "title": "Sample Quantiles in Statistical Packages",
        "authors": ["Rob J. Hyndman", "Yanan Fan"],
        "publisher": "American Statistical Association",
        "year": 1996,
        "kind": "paper",
        "identifier": "The American Statistician, vol. 50, no. 4, pp. 361-365, doi:10.1080/00031305.1996.10473566",
        "url": "https://www.tandfonline.com/doi/abs/10.1080/00031305.1996.10473566",
        "summary": "Surveys and systematizes the nine sample-quantile definitions (types 1-9) "
                   "implemented across statistical packages, expressing each as a weighted "
                   "average of order statistics and analyzing their motivating properties such as "
                   "median-unbiasedness. This taxonomy is the reference for quantile-estimation "
                   "methods in modern software: Python's statistics.quantiles 'exclusive' and "
                   "'inclusive' methods correspond to types 6 and 7 in this paper, so percentile "
                   "computations validated against the Python statistics module implement "
                   "estimators defined here.",
    },
    {
        "id": "rfc-4632",
        "title": "Classless Inter-domain Routing (CIDR): The Internet Address Assignment and "
                 "Aggregation Plan",
        "authors": ["Vince Fuller", "Tony Li"],
        "publisher": "IETF",
        "year": 2006,
        "kind": "rfc",
        "identifier": "RFC 4632 (BCP 122)",
        "url": "https://www.rfc-editor.org/info/rfc4632",
        "summary": "Defines Classless Inter-domain Routing: prefix/length notation and the "
                   "allocation and aggregation of the 32-bit IPv4 address space without classful "
                   "boundaries. Specifies how an address block is characterized by a prefix and "
                   "mask length, and the rules for hierarchical aggregation of routes. Best "
                   "Current Practice (BCP 122); obsoletes RFC 1519. This is the authoritative "
                   "reference for CIDR subnet arithmetic (network/broadcast derivation, prefix "
                   "containment, block splitting).",
    },
    {
        "id": "rfc-4291",
        "title": "IP Version 6 Addressing Architecture",
        "authors": ["Robert Hinden", "Stephen Deering"],
        "publisher": "IETF",
        "year": 2006,
        "kind": "rfc",
        "identifier": "RFC 4291",
        "url": "https://www.rfc-editor.org/info/rfc4291",
        "summary": "Defines the IPv6 addressing architecture: the addressing model, "
                   "unicast/anycast/multicast address types, and the three text representations "
                   "of IPv6 addresses (eight colon-separated 16-bit hex groups, '::' zero "
                   "compression, and the embedded-IPv4 form x:x:x:x:x:x:d.d.d.d). Obsoletes RFC "
                   "3513 and is the base specification any IPv6 parser must accept. Updated for "
                   "output formatting by RFC 5952.",
    },
    {
        "id": "rfc-5952",
        "title": "A Recommendation for IPv6 Address Text Representation",
        "authors": ["Seiichi Kawamura", "Masanobu Kawashima"],
        "publisher": "IETF",
        "year": 2010,
        "kind": "rfc",
        "identifier": "RFC 5952",
        "url": "https://www.rfc-editor.org/info/rfc5952",
        "summary": "Specifies the single canonical text form for IPv6 addresses among the many "
                   "representations RFC 4291 permits: leading zeros in each field must be "
                   "suppressed, '::' must be used to its maximum extent on the longest run of "
                   "zero fields (first such run on a tie) and must not compress a single zero "
                   "field, and hexadecimal digits must be lowercase. Systems should emit this "
                   "canonical form while still accepting all RFC 4291 forms on input. Updates RFC "
                   "4291.",
    },
    {
        "id": "ieee-802",
        "title": "IEEE Standard for Local and Metropolitan Area Networks: Overview and "
                 "Architecture",
        "authors": ["IEEE"],
        "publisher": "IEEE",
        "year": 2024,
        "kind": "standard",
        "identifier": "IEEE Std 802-2024",
        "url": "https://standards.ieee.org/ieee/802/10894/",
        "summary": "Base standard of the IEEE 802 family; specifies the structure of IEEE 802 MAC "
                   "addresses, including 48-bit (EUI-48-based) universal addresses. Defines the "
                   "two flag bits of the first octet: the I/G bit (least significant bit; 0 = "
                   "individual/unicast, 1 = group/multicast) and the U/L bit (second least "
                   "significant bit; 0 = universally administered, 1 = locally administered), "
                   "together with the hexadecimal representation of addresses. Approved "
                   "2024-12-11 as the revision of IEEE Std 802-2014.",
    },
    {
        "id": "ieee-ra-eui-guidelines",
        "title": "Guidelines for Use of Extended Unique Identifier (EUI), Organizationally Unique "
                 "Identifier (OUI), and Company ID (CID)",
        "authors": ["IEEE Registration Authority"],
        "publisher": "IEEE",
        "year": 2017,
        "kind": "specification",
        "identifier": "IEEE RA Guidelines for Use of EUI, OUI, and CID (2017-08-03)",
        "url": "https://standards.ieee.org/wp-content/uploads/import/documents/tutorials/eui.pdf",
        "summary": "IEEE Registration Authority tutorial defining the formats and assignment "
                   "rules of organizational identifiers (OUI, CID) and the extended identifiers "
                   "built on them, EUI-48 and EUI-64, including their hexadecimal representation "
                   "conventions and the semantics of the I/G and U/L bits when an EUI-48 is used "
                   "as a MAC address. Supersedes the RA's separate 'Guidelines for 48-Bit Global "
                   "Identifier (EUI-48)' and EUI-64/OUI documents. Dated 2017-08-03.",
    },
    {
        "id": "rfc-4271",
        "title": "A Border Gateway Protocol 4 (BGP-4)",
        "authors": ["Yakov Rekhter", "Tony Li", "Susan Hares"],
        "publisher": "IETF",
        "year": 2006,
        "kind": "rfc",
        "identifier": "RFC 4271",
        "url": "https://www.rfc-editor.org/info/rfc4271",
        "summary": "Defines version 4 of the Border Gateway Protocol, the inter-domain routing "
                   "protocol of the Internet. Specifies the AS_PATH attribute, including "
                   "AS_SEQUENCE and AS_SET segment types, AS-path-based loop detection, and "
                   "AS-path length as a route-selection criterion. Obsoletes RFC 1771; the "
                   "authoritative reference for AS-path structure and interpretation.",
    },
    {
        "id": "rfc-6996",
        "title": "Autonomous System (AS) Reservation for Private Use",
        "authors": ["Jon Mitchell"],
        "publisher": "IETF",
        "year": 2013,
        "kind": "rfc",
        "identifier": "RFC 6996 (BCP 6)",
        "url": "https://www.rfc-editor.org/info/rfc6996",
        "summary": "Reserves two contiguous blocks of Autonomous System numbers for private use: "
                   "64512-65534 in the 16-bit ASN registry and 4200000000-4294967294 in the "
                   "32-bit ASN registry. These ASNs must not be advertised to the global "
                   "Internet. Best Current Practice (BCP 6); the authoritative source for "
                   "classifying an ASN as private-use.",
    },
    {
        "id": "rfc-5398",
        "title": "Autonomous System (AS) Number Reservation for Documentation Use",
        "authors": ["Geoff Huston"],
        "publisher": "IETF",
        "year": 2008,
        "kind": "rfc",
        "identifier": "RFC 5398",
        "url": "https://www.rfc-editor.org/info/rfc5398",
        "summary": "Reserves ASN ranges for use in documentation and sample code: 64496-64511 "
                   "from the 16-bit ASN pool and 65536-65551 from the 32-bit ASN pool, to reduce "
                   "conflict and confusion between documented examples and deployed systems. The "
                   "authoritative source for classifying an ASN as documentation-reserved.",
    },
    {
        "id": "rfc-6793",
        "title": "BGP Support for Four-Octet Autonomous System (AS) Number Space",
        "authors": ["Quaizar Vohra", "Enke Chen"],
        "publisher": "IETF",
        "year": 2012,
        "kind": "rfc",
        "identifier": "RFC 6793",
        "url": "https://www.rfc-editor.org/info/rfc6793",
        "summary": "Extends BGP to carry Autonomous System numbers as four-octet entities, "
                   "defining how two-octet ASNs map into the four-octet space (high-order octets "
                   "zero) and reserving the special two-octet value AS_TRANS (23456) to represent "
                   "non-mappable four-octet ASNs toward legacy speakers. Defines the "
                   "AS4_PATH/AS4_AGGREGATOR attributes for transition. Obsoletes RFC 4893 and "
                   "updates RFC 4271; the authoritative reference for 4-byte ASN classification.",
    },
    {
        "id": "rfc-1071",
        "title": "Computing the Internet Checksum",
        "authors": ["Robert Braden", "David Borman", "Craig Partridge"],
        "publisher": "IETF",
        "year": 1988,
        "kind": "rfc",
        "identifier": "RFC 1071",
        "url": "https://www.rfc-editor.org/info/rfc1071",
        "summary": "Describes techniques for efficiently computing the 16-bit one's-complement "
                   "Internet checksum used by IP, TCP, and UDP, exploiting its commutative, "
                   "associative, and byte-order-independent properties. Covers deferred carries, "
                   "loop unrolling, incremental update, and gives worked numerical examples and "
                   "reference implementations. The canonical specification of the checksum "
                   "computation itself.",
    },
    {
        "id": "rfc-791",
        "title": "Internet Protocol",
        "authors": ["Jon Postel"],
        "publisher": "IETF",
        "year": 1981,
        "kind": "rfc",
        "identifier": "RFC 791 (STD 5)",
        "url": "https://www.rfc-editor.org/info/rfc791",
        "summary": "The Internet Protocol version 4 specification, defining the IPv4 datagram "
                   "format including the header layout and the Header Checksum field: the 16-bit "
                   "one's complement of the one's-complement sum of all 16-bit words in the "
                   "header, with the checksum field taken as zero during computation. Internet "
                   "Standard STD 5; the source of the IPv4-header checksum that RFC 1071 shows "
                   "how to compute efficiently.",
    },
    {
        "id": "ieee-802-1q",
        "title": "IEEE Standard for Local and Metropolitan Area Networks—Bridges and Bridged "
                 "Networks",
        "authors": ["IEEE"],
        "publisher": "IEEE",
        "year": 2022,
        "kind": "standard",
        "identifier": "IEEE Std 802.1Q-2022",
        "url": "https://standards.ieee.org/ieee/802.1Q/10323/",
        "summary": "Specifies MAC Bridges and VLAN Bridges, including the 802.1Q tag format with "
                   "its 12-bit VLAN Identifier (VID). Defines the reserved VID values: 0 (the "
                   "null VID, indicating a priority-tagged frame carrying no VLAN identifier) and "
                   "4095 (0xFFF, reserved for implementation use), leaving 1-4094 as valid VLAN "
                   "IDs with VID 1 as the default PVID. Published December 2022; the current "
                   "consolidated revision of 802.1Q.",
    },
    {
        "id": "itu-e164",
        "title": "The international public telecommunication numbering plan",
        "authors": ["ITU-T"],
        "publisher": "ITU-T",
        "year": 2026,
        "kind": "standard",
        "identifier": "ITU-T E.164 (02/2026)",
        "url": "https://www.itu.int/rec/T-REC-E.164/en",
        "summary": "Defines the number structure and functionality for international public "
                   "telecommunication numbers: digits only, a maximum length of 15 digits, and a "
                   "country code of 1 to 3 digits followed by a national (significant) number. "
                   "Covers the five number categories (geographic areas, global services, "
                   "networks, groups of countries, and trials) and the digit analysis needed to "
                   "route calls. This in-force edition was approved 13 February 2026, superseding "
                   "the 11/2010 edition.",
    },
    {
        "id": "3gpp-ts-23-003",
        "title": "Numbering, addressing and identification",
        "authors": ["3GPP"],
        "publisher": "3GPP",
        "year": 2025,
        "kind": "specification",
        "identifier": "3GPP TS 23.003 (Release 19)",
        "url": "https://www.3gpp.org/dynareport/23003.htm",
        "summary": "Defines the identifiers used in 3GPP systems, including the International "
                   "Mobile station Equipment Identity (IMEI): an 8-digit Type Allocation Code, a "
                   "6-digit serial number, and a check digit. The check digit is computed over "
                   "the 14 leading digits using the Luhn formula as defined in Annex B of ISO/IEC "
                   "7812, and exists to catch manual transmission errors such as mistyped IMEIs "
                   "at operator customer-care desks.",
    },
    {
        "id": "nmea-0183",
        "title": "NMEA 0183 Interface Standard",
        "authors": ["NMEA"],
        "publisher": "National Marine Electronics Association",
        "year": 2023,
        "kind": "standard",
        "identifier": "NMEA 0183 v4.30",
        "url": "https://www.nmea.org/nmea-0183.html",
        "summary": "Defines electrical signal requirements, data transmission protocol, and "
                   "sentence formats for 4800-baud serial communication between marine electronic "
                   "devices such as GNSS receivers, sounders, and autopilots. Sentences begin "
                   "with '$' or '!' and end with an optional '*'-delimited checksum: the 8-bit "
                   "XOR of all characters between (but excluding) '$' and '*', transmitted as two "
                   "uppercase hexadecimal characters. Version 4.30 was published in December "
                   "2023, replacing v4.11 (2018).",
    },
    {
        "id": "modbus-serial-v1.02",
        "title": "MODBUS over Serial Line Specification and Implementation Guide V1.02",
        "authors": ["Modbus Organization"],
        "publisher": "Modbus Organization",
        "year": 2006,
        "kind": "specification",
        "identifier": "MODBUS over Serial Line Specification and Implementation Guide V1.02 (2006-12-20)",
        "url": "https://www.modbus.org/file/secure/modbusoverserial.pdf",
        "summary": "Defines the Modbus master/slave protocol over serial lines (RS-485/RS-232) in "
                   "its RTU and ASCII transmission modes. For RTU mode it specifies the 16-bit "
                   "CRC error-checking field: a register pre-loaded to 0xFFFF, processed with the "
                   "reflected generating polynomial 0xA001 (bit-reversed 0x8005), no final XOR, "
                   "appended low byte first. Appendix B gives the reference CRC generation "
                   "implementation. Published 20 December 2006.",
    },
    {
        "id": "nakajima-1988",
        "title": "Introduction to TPM: Total Productive Maintenance",
        "authors": ["Seiichi Nakajima"],
        "publisher": "Productivity Press",
        "year": 1988,
        "kind": "book",
        "identifier": "ISBN 0-915299-23-2",
        "url": "https://search.worldcat.org/title/Introduction-to-TPM-:-total-productive-maintenance/oclc/18441684",
        "summary": "The first English-language book on Total Productive Maintenance, translated "
                   "from Nakajima's Japanese original. Defines Overall Equipment Effectiveness "
                   "(OEE) as the product of availability, performance rate, and quality rate, "
                   "derived from the six big equipment losses, with worked calculation examples "
                   "and the widely cited ~85% world-class benchmark. This is the canonical origin "
                   "of the OEE metric implemented by the module.",
    },
    {
        "id": "hamming-1950",
        "title": "Error Detecting and Error Correcting Codes",
        "authors": ["R. W. Hamming"],
        "publisher": "Bell System Technical Journal",
        "year": 1950,
        "kind": "paper",
        "identifier": "Bell System Technical Journal, vol. 29, no. 2, pp. 147-160, doi:10.1002/j.1538-7305.1950.tb00463.x",
        "url": "https://doi.org/10.1002/j.1538-7305.1950.tb00463.x",
        "summary": "Introduces systematic error-detecting and error-correcting block codes, "
                   "establishing the concepts of minimum distance and parity-check positions at "
                   "powers of two. Presents the single-error-correcting (7,4) code — four data "
                   "bits protected by three parity bits — where the syndrome directly gives the "
                   "position of any single bit error. Published in the April 1950 issue of the "
                   "Bell System Technical Journal.",
    },
    {
        "id": "levenshtein-1966",
        "title": "Binary Codes Capable of Correcting Deletions, Insertions and Reversals",
        "authors": ["Vladimir I. Levenshtein"],
        "publisher": "American Institute of Physics (Soviet Physics Doklady)",
        "year": 1966,
        "kind": "paper",
        "identifier": "Soviet Physics Doklady, Vol. 10, No. 8, pp. 707-710",
        "url": "https://ui.adsabs.harvard.edu/abs/1966SPhD...10..707L",
        "summary": "Introduces the edit-distance metric now known as Levenshtein distance: the "
                   "minimum number of single-symbol deletions, insertions, and substitutions "
                   "needed to transform one sequence into another. The paper studies binary codes "
                   "capable of correcting such errors, and its distance metric became the "
                   "standard measure of string similarity. This is the defining source for the "
                   "semantics of the levenshtein module's distance function.",
    },
    {
        "id": "wagner-1974",
        "title": "The String-to-String Correction Problem",
        "authors": ["Robert A. Wagner", "Michael J. Fischer"],
        "publisher": "ACM",
        "year": 1974,
        "kind": "paper",
        "identifier": "Journal of the ACM, Vol. 21, No. 1, pp. 168-173; doi:10.1145/321796.321811",
        "url": "https://dl.acm.org/doi/10.1145/321796.321811",
        "summary": "Formalizes the string-to-string correction problem as finding the "
                   "minimum-cost sequence of edit operations (substitute, delete, insert) "
                   "transforming one string into another, and gives the dynamic-programming "
                   "algorithm that solves it in time proportional to the product of the string "
                   "lengths. This Wagner-Fischer matrix algorithm is the textbook method for "
                   "computing Levenshtein distance and is the algorithm the levenshtein module "
                   "implements.",
    },
    {
        "id": "kahn-1962",
        "title": "Topological sorting of large networks",
        "authors": ["Arthur B. Kahn"],
        "publisher": "ACM",
        "year": 1962,
        "kind": "paper",
        "identifier": "Communications of the ACM, Vol. 5, No. 11, pp. 558-562; doi:10.1145/368996.369025",
        "url": "https://dl.acm.org/doi/10.1145/368996.369025",
        "summary": "Presents the in-degree-based topological sorting procedure now known as "
                   "Kahn's algorithm: repeatedly emit a node with no unprocessed predecessors and "
                   "remove its outgoing edges. Developed for PERT-style network analysis at "
                   "Westinghouse, it orders a directed acyclic graph in linear time; failure to "
                   "consume all nodes detects a cycle. The topo_sort module implements this "
                   "algorithm with a deterministic tie-break on the ready set.",
    },
    {
        "id": "whatwg-url",
        "title": "URL Standard",
        "authors": ["Anne van Kesteren"],
        "publisher": "WHATWG",
        "year": 2026,
        "kind": "specification",
        "identifier": "WHATWG URL Living Standard (last updated 6 July 2026)",
        "url": "https://url.spec.whatwg.org/",
        "summary": "The WHATWG living standard defining URLs, domains, IP addresses, and their "
                   "API, superseding RFC 3986/3987 for web content. Section 5 specifies the "
                   "application/x-www-form-urlencoded format: the parser that splits input on "
                   "'&', treats '+' as space, and percent-decodes UTF-8 name/value tuples (5.1), "
                   "and the corresponding serializer (5.2). These algorithms define the "
                   "parse/stringify semantics the parseQuery module implements.",
    },
    {
        "id": "wadler-1995",
        "title": "Monads for functional programming",
        "authors": ["Philip Wadler"],
        "publisher": "Springer",
        "year": 1995,
        "kind": "paper",
        "identifier": "Advanced Functional Programming (J. Jeuring & E. Meijer, eds.), LNCS 925:24-52, doi:10.1007/3-540-59451-5_2",
        "url": "https://doi.org/10.1007/3-540-59451-5_2",
        "summary": "Wadler's tutorial presentation of monads as a technique for structuring pure "
                   "functional programs, covering the unit and bind operators and their laws. It "
                   "develops the exception (error) monad in detail: a computation yields either a "
                   "success value or an error, unit injects a success, and bind short-circuits on "
                   "the first error while chaining fallible steps. A Result<T,E> type with ok/err "
                   "constructors, functor map, and an andThen bind combinator implements exactly "
                   "this monad.",
    },
    {
        "id": "ecma-262-2024",
        "title": "ECMAScript® 2024 Language Specification",
        "authors": ["Ecma International"],
        "publisher": "Ecma International",
        "year": 2024,
        "kind": "standard",
        "identifier": "ECMA-262, 15th edition (June 2024)",
        "url": "https://262.ecma-international.org/15.0/",
        "summary": "The 15th edition of the ECMAScript language standard. Defines the SameValue "
                   "and SameValueZero abstract equality operations, under which NaN equals NaN "
                   "and SameValue distinguishes +0 from -0 (the semantics exposed as Object.is "
                   "and followed by structural deep-equality at the leaves). Also introduces "
                   "Object.groupBy and Map.groupBy via the GroupBy abstract operation: elements "
                   "are partitioned by a callback-produced key, groups are created in "
                   "first-encounter order, and elements within a group keep source iteration "
                   "order, materialised on a null-prototype object so keys like \"__proto__\" "
                   "become ordinary buckets.",
    },
    {
        "id": "rfc-8439",
        "title": "ChaCha20 and Poly1305 for IETF Protocols",
        "authors": ["Y. Nir", "A. Langley"],
        "publisher": "IETF",
        "year": 2018,
        "kind": "rfc",
        "identifier": "RFC 8439",
        "url": "https://www.rfc-editor.org/rfc/rfc8439",
        "summary": "Specifies the ChaCha20 stream cipher (the IETF variant with a 96-bit nonce "
                   "and 32-bit block counter) and the Poly1305 authenticator, and their AEAD "
                   "composition. Defines the quarter round, the 20-round block function over a "
                   "4x4 state of little-endian 32-bit words, and provides the reference test "
                   "vectors (quarter round, block function keystream, and the 'sunscreen' "
                   "encryption example) that conforming implementations must reproduce.",
    },
    {
        "id": "rfc-7515",
        "title": "JSON Web Signature (JWS)",
        "authors": ["M. Jones", "J. Bradley", "N. Sakimura"],
        "publisher": "IETF",
        "year": 2015,
        "kind": "rfc",
        "identifier": "RFC 7515",
        "url": "https://www.rfc-editor.org/rfc/rfc7515",
        "summary": "Defines JSON Web Signature: digitally signed or MACed content represented "
                   "with base64url-encoded header, payload and signature segments, including the "
                   "compact serialization 'header.payload.signature' used by JWTs. Appendix A.1 "
                   "gives the complete worked HS256 example -- exact octets of the protected "
                   "header and payload and the resulting signature -- used as a conformance "
                   "vector.",
    },
    {
        "id": "rfc-7519",
        "title": "JSON Web Token (JWT)",
        "authors": ["M. Jones", "J. Bradley", "N. Sakimura"],
        "publisher": "IETF",
        "year": 2015,
        "kind": "rfc",
        "identifier": "RFC 7519",
        "url": "https://www.rfc-editor.org/rfc/rfc7519",
        "summary": "Defines the JSON Web Token: a compact claims representation carried as the "
                   "payload of a JWS or JWE. Registers the standard claims -- iss, sub, aud, exp, "
                   "nbf, iat, jti -- and their processing rules, including that expiration "
                   "('exp') and not-before ('nbf') are NumericDate values compared against "
                   "current time with optional small leeway.",
    },
    {
        "id": "rfc-3492",
        "title": "Punycode: A Bootstring encoding of Unicode for Internationalized Domain Names "
                 "in Applications (IDNA)",
        "authors": ["A. Costello"],
        "publisher": "IETF",
        "year": 2003,
        "kind": "rfc",
        "identifier": "RFC 3492",
        "url": "https://www.rfc-editor.org/rfc/rfc3492",
        "summary": "Defines Bootstring, a family of encodings of Unicode strings into the basic "
                   "code points, and Punycode, its instantiation with the DNS parameters (base "
                   "36, tmin 1, tmax 26, skew 38, damp 700, initial bias 72). Specifies the "
                   "encoding and decoding algorithms, the bias adaptation function, overflow "
                   "handling, and section 7.1's sample strings in eleven languages that "
                   "implementations reproduce as conformance vectors.",
    },
    {
        "id": "rfc-1035",
        "title": "Domain names - implementation and specification",
        "authors": ["P. Mockapetris"],
        "publisher": "IETF",
        "year": 1987,
        "kind": "rfc",
        "identifier": "RFC 1035 (STD 13)",
        "url": "https://www.rfc-editor.org/rfc/rfc1035",
        "summary": "The core DNS specification: message formats, resource records, name "
                   "compression, and the size limits of section 2.3.4 -- labels of at most 63 "
                   "octets and names of at most 255 octets in wire encoding -- together with the "
                   "preferred letter-digit-hyphen name syntax of section 2.3.1.",
    },
    {
        "id": "rfc-1123",
        "title": "Requirements for Internet Hosts - Application and Support",
        "authors": ["R. Braden (ed.)"],
        "publisher": "IETF",
        "year": 1989,
        "kind": "rfc",
        "identifier": "RFC 1123 (STD 3)",
        "url": "https://www.rfc-editor.org/rfc/rfc1123",
        "summary": "Host requirements for application-layer protocols. Section 2.1 relaxes the "
                   "RFC 952 hostname syntax to permit labels beginning with a digit, keeps the "
                   "letter-digit-hyphen alphabet and per-label limits, and is the reason names "
                   "like '3com.com' are valid hostnames.",
    },
    {
        "id": "erlang-1917",
        "title": "Solution of some Problems in the Theory of Probabilities of Significance in "
                 "Automatic Telephone Exchanges",
        "authors": ["A. K. Erlang"],
        "publisher": "Elektroteknikeren (English translation: The Post Office Electrical Engineers' Journal, 1918)",
        "year": 1917,
        "kind": "paper",
        "identifier": "Elektroteknikeren, vol. 13 (1917); P.O.E.E.J. vol. 10 (1918), pp. 189-197",
        "url": "https://en.wikipedia.org/wiki/Erlang_(unit)#cite_note-erlang1917-4",
        "summary": "Erlang's derivation of the loss and waiting-time formulas for telephone "
                   "exchanges under Poisson traffic, including the B-formula giving the "
                   "probability that a call offered to a fully occupied group of circuits is "
                   "lost. The foundation of teletraffic engineering: circuit-group dimensioning "
                   "tables used for a century derive from this paper's formulas.",
    },
    {
        "id": "nets-ocr-giro",
        "title": "Systemspesifikasjon OCR giro",
        "authors": ["Nets Norway / Mastercard Payment Services"],
        "publisher": "Mastercard Payment Services (formerly Nets)",
        "year": 2018,
        "kind": "specification",
        "identifier": "OCR giro systemdokumentasjon, versjon 4.0 (2018)",
        "url": "https://www.mastercardpaymentservices.com/media/ruqn3ort/ocr-systemspesifikasjon_no_mps.pdf",
        "summary": "The system specification for the Norwegian OCR giro payment-collection "
                   "service: record types and layouts for transaction files, and the KID "
                   "(kundeidentifikasjon) rules -- a 2-25 digit customer reference whose final "
                   "check digit is computed under modulus 10 (Luhn weights 2,1) or modulus 11 "
                   "(weights 2-7), both applied right to left, with worked examples of both "
                   "calculations.",
    },
    {
        "id": "kellison-2009",
        "title": "The Theory of Interest",
        "authors": ["Stephen G. Kellison"],
        "publisher": "McGraw-Hill/Irwin",
        "year": 2009,
        "kind": "book",
        "identifier": "3rd edition, ISBN 978-0-07-338244-9",
        "url": "https://www.mheducation.com/highered/product/theory-interest-kellison/M9780073382449.html",
        "summary": "The standard actuarial text on interest theory: accumulation and discount, "
                   "annuities-certain and their present values, amortization schedules and "
                   "sinking funds. Chapter 5 develops exactly the loan-amortization identities "
                   "this module enforces -- the level payment P*i/(1-(1+i)^-n), "
                   "interest-then-principal splitting, and the balance recursion that terminates "
                   "at zero.",
    },
    {
        "id": "bloom-1970",
        "title": "Space/Time Trade-offs in Hash Coding with Allowable Errors",
        "authors": ["Burton H. Bloom"],
        "publisher": "ACM",
        "year": 1970,
        "kind": "paper",
        "identifier": "Communications of the ACM, vol. 13, no. 7, pp. 422-426; doi:10.1145/362686.362692",
        "url": "https://doi.org/10.1145/362686.362692",
        "summary": "Introduces the Bloom filter: hash-coded set membership that permits a "
                   "controlled rate of false positives in exchange for dramatic space savings, "
                   "with no false negatives. Derives the space/error trade-off analysis from "
                   "which the standard false-positive formula and the optimal number of hash "
                   "functions follow.",
    },
    {
        "id": "rfc-9562",
        "title": "Universally Unique IDentifiers (UUIDs)",
        "authors": ["K. Davis", "B. Peabody", "P. Leach"],
        "publisher": "IETF",
        "year": 2024,
        "kind": "rfc",
        "identifier": "RFC 9562 (STD 97)",
        "url": "https://www.rfc-editor.org/rfc/rfc9562",
        "summary": "The current UUID standard, obsoleting RFC 4122: defines the 128-bit layout, "
                   "the variant and version fields, and generation algorithms for versions 1-8, "
                   "including the name-based v3 (MD5) and v5 (SHA-1) constructions over a "
                   "namespace UUID concatenated with a name, and the new time-ordered v6/v7. "
                   "Provides test vectors for each version that implementations reproduce.",
    },
    {
        "id": "base58-draft",
        "title": "The Base58 Encoding Scheme",
        "authors": ["M. Sporny (ed.)"],
        "publisher": "IETF (Internet-Draft, work in progress)",
        "year": 2021,
        "kind": "specification",
        "identifier": "draft-msporny-base58-03",
        "url": "https://datatracker.ietf.org/doc/html/draft-msporny-base58-03",
        "summary": "An Internet-Draft documenting the Base58 encoding as used by Bitcoin and "
                   "IPFS: the 58-character alphabet omitting 0, O, I and l, big-integer base "
                   "conversion, and the preservation of leading zero bytes as leading '1' "
                   "characters. Includes the test vectors ('Hello World!', the '11233QC4' "
                   "leading-zero case) that implementations reproduce. Never published as an RFC "
                   "-- cited as the de facto written specification of the scheme.",
    },
    {
        "id": "iec-60751",
        "title": "Industrial platinum resistance thermometers and platinum temperature sensors",
        "authors": ["IEC"],
        "publisher": "IEC",
        "year": 2022,
        "kind": "standard",
        "identifier": "IEC 60751:2022 (Edition 3.0)",
        "url": "https://webstore.iec.ch/en/publication/63753",
        "summary": "Specifies the resistance-versus-temperature relationship for industrial "
                   "platinum resistance thermometers over -200 degC to +850 degC -- the "
                   "Callendar-Van Dusen equations with the standard alpha = 0.00385 coefficients "
                   "-- together with tolerance classes (AA, A, B, C) and their validity ranges. "
                   "The standard's reference table of R(t) values is the conformance oracle for "
                   "RTD conversion code.",
    },
    {
        "id": "sre-workbook-2018",
        "title": "The Site Reliability Workbook: Practical Ways to Implement SRE",
        "authors": ["B. Beyer", "N. R. Murphy", "D. K. Rensin", "K. Kawahara", "S. Thorne (eds.)"],
        "publisher": "O'Reilly Media",
        "year": 2018,
        "kind": "book",
        "identifier": "ISBN 978-1-492-02950-2",
        "url": "https://sre.google/workbook/table-of-contents/",
        "summary": "The companion volume to Site Reliability Engineering with concrete "
                   "implementation practice. Chapter 5, 'Alerting on SLOs', develops error-budget "
                   "burn-rate alerting and publishes the recommended multiwindow, multi-burn-rate "
                   "policy for a 30-day period: burn rate 14.4 over 1 hour and 6 over 6 hours as "
                   "pages, 1 over 3 days as a ticket, each long window paired with a 1/12 short "
                   "confirmation window.",
    },
    {
        "id": "roberts-1959",
        "title": "Control Chart Tests Based on Geometric Moving Averages",
        "authors": ["S. W. Roberts"],
        "publisher": "Taylor & Francis (Technometrics)",
        "year": 1959,
        "kind": "paper",
        "identifier": "Technometrics, vol. 1, no. 3, pp. 239-250; doi:10.1080/00401706.1959.10489860",
        "url": "https://doi.org/10.1080/00401706.1959.10489860",
        "summary": "Introduces the geometric (exponentially weighted) moving-average control "
                   "chart: each point is a weighted average of the current observation and the "
                   "previous chart value, giving memory that detects small persistent shifts "
                   "faster than Shewhart charts. The origin of the EWMA chart and its "
                   "control-limit analysis.",
    },
    {
        "id": "nist-sematech",
        "title": "NIST/SEMATECH e-Handbook of Statistical Methods",
        "authors": ["NIST/SEMATECH"],
        "publisher": "NIST",
        "year": 2012,
        "kind": "book",
        "identifier": "doi:10.18434/M32189, section 6.3.2.4 (EWMA Control Charts)",
        "url": "https://www.itl.nist.gov/div898/handbook/",
        "summary": "NIST's online engineering-statistics handbook. Section 6.3.2.4 defines the "
                   "EWMA control chart, its variance factor "
                   "lambda/(2-lambda)*(1-(1-lambda)^(2i)), and publishes a complete worked "
                   "example -- a 20-point dataset with target 50, lambda 0.3 and the resulting "
                   "EWMA series and control limits -- that implementations can reproduce "
                   "value-for-value.",
    },
    {
        "id": "cis-controls-v8-1",
        "title": "CIS Critical Security Controls, Version 8.1",
        "authors": ["Center for Internet Security"],
        "publisher": "Center for Internet Security",
        "year": 2024,
        "kind": "framework",
        "identifier": "CIS Controls v8.1",
        "url": "https://www.cisecurity.org/controls/v8-1",
        "summary": "The 2024 revision of the CIS Critical Security Controls: 18 prioritized "
                   "Controls comprising 153 Safeguards, each assigned to cumulative "
                   "Implementation Groups (IG1 essential cyber hygiene with 56 safeguards, IG2 "
                   "with 130, IG3 with all 153). v8.1 aligns the Controls with NIST CSF 2.0 "
                   "governance and adds asset-class and documentation refinements over v8.0 "
                   "without changing the Control count.",
    },
    {
        "id": "gdpr-2016-679",
        "title": "Regulation (EU) 2016/679 (General Data Protection Regulation)",
        "authors": ["European Parliament and Council of the European Union"],
        "publisher": "Publications Office of the European Union",
        "year": 2016,
        "kind": "regulation",
        "identifier": "Regulation (EU) 2016/679, OJ L 119, 4.5.2016, p. 1-88",
        "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "summary": "The General Data Protection Regulation: 99 articles in 11 chapters governing "
                   "the processing of personal data in the EU. Article 5 states the processing "
                   "principles (lawfulness/fairness/transparency, purpose limitation, data "
                   "minimisation, accuracy, storage limitation, integrity and confidentiality, "
                   "accountability); Article 32 requires appropriate technical and organisational "
                   "security measures including pseudonymisation/encryption, resilience, "
                   "recoverability and regular effectiveness testing.",
    },
    {
        "id": "hardt-2016",
        "title": "Equality of Opportunity in Supervised Learning",
        "authors": ["Moritz Hardt", "Eric Price", "Nathan Srebro"],
        "publisher": "Advances in Neural Information Processing Systems 29 (NIPS 2016), Curran Associates",
        "year": 2016,
        "kind": "paper",
        "identifier": "NIPS 2016, pp. 3315-3323; arXiv:1610.02413",
        "url": "https://papers.nips.cc/paper/6374-equality-of-opportunity-in-supervised-learning",
        "summary": "Proposes equalized odds and equal opportunity as fairness criteria for "
                   "supervised learning: a predictor satisfies equalized odds if it is "
                   "independent of the protected attribute conditional on the true outcome, "
                   "equalizing both true-positive and false-positive rates across groups. Shows "
                   "how to optimally post-process any learned predictor to satisfy the criterion "
                   "using only joint statistics of predictor, target, and protected attribute (an "
                   "'oblivious' adjustment). Published at NIPS 2016 (Advances in Neural "
                   "Information Processing Systems 29).",
    },
    {
        "id": "feldman-2015",
        "title": "Certifying and Removing Disparate Impact",
        "authors": ["Michael Feldman", "Sorelle A. Friedler", "John Moeller", "Carlos Scheidegger", "Suresh Venkatasubramanian"],
        "publisher": "Proceedings of the 21st ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD '15), ACM",
        "year": 2015,
        "kind": "paper",
        "identifier": "doi:10.1145/2783258.2783311; KDD '15 pp. 259-268; arXiv:1412.3756",
        "url": "https://doi.org/10.1145/2783258.2783311",
        "summary": "Formalizes the legal notion of disparate impact as the '80% rule': a dataset "
                   "exhibits disparate impact when Pr(C=YES|X=0)/Pr(C=YES|X=1) ≤ 0.8 for "
                   "protected attribute X, generalizing the EEOC four-fifths rule from the 1978 "
                   "Uniform Guidelines on Employee Selection Procedures (29 CFR 1607.4(D)). Links "
                   "disparate impact to the balanced error rate of predicting the protected "
                   "attribute from the other features, and gives procedures to certify a dataset "
                   "free of disparate impact and to repair data while preserving rank within "
                   "groups. Published at KDD 2015.",
    },
    {
        "id": "guo-2017",
        "title": "On Calibration of Modern Neural Networks",
        "authors": ["Chuan Guo", "Geoff Pleiss", "Yu Sun", "Kilian Q. Weinberger"],
        "publisher": "Proceedings of the 34th International Conference on Machine Learning (ICML 2017), PMLR",
        "year": 2017,
        "kind": "paper",
        "identifier": "PMLR 70:1321-1330; arXiv:1706.04599",
        "url": "https://proceedings.mlr.press/v70/guo17a.html",
        "summary": "Shows that modern deep neural networks are poorly calibrated compared to "
                   "older models, with depth, width, weight decay, and batch normalization "
                   "identified as influencing factors. Defines Expected Calibration Error (ECE) "
                   "as the bin-size-weighted average absolute gap between per-bin accuracy and "
                   "per-bin mean confidence over M equally-spaced confidence bins, plus Maximum "
                   "Calibration Error (MCE) as the worst-case bin gap. Finds temperature scaling "
                   "— a single-parameter variant of Platt scaling — surprisingly effective at "
                   "calibrating predictions. Published at ICML 2017, PMLR volume 70, pages "
                   "1321-1330.",
    },
    {
        "id": "dwork-roth-2014",
        "title": "The Algorithmic Foundations of Differential Privacy",
        "authors": ["Cynthia Dwork", "Aaron Roth"],
        "publisher": "Foundations and Trends in Theoretical Computer Science, Now Publishers",
        "year": 2014,
        "kind": "book",
        "identifier": "doi:10.1561/0400000042; Found. Trends Theor. Comput. Sci. Vol. 9, Nos. 3-4 (2014), pp. 211-407",
        "url": "https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf",
        "summary": "The standard monograph on differential privacy, covering the definition, the "
                   "Laplace and exponential mechanisms, and composition theorems. Theorem 3.16 "
                   "(basic/sequential composition) states that the composition of k mechanisms "
                   "that are each (ε_i, δ_i)-differentially private is (Σε_i, "
                   "Σδ_i)-differentially private; Theorem 3.20 gives the stronger advanced "
                   "composition bound. The book does not state a parallel composition theorem — "
                   "that result (disjoint input subsets yield max_i ε_i privacy) is Theorem 4 of "
                   "McSherry's PINQ paper (SIGMOD 2009). Published as Foundations and Trends in "
                   "Theoretical Computer Science Vol. 9, Nos. 3-4, pages 211-407 (2014), DOI "
                   "10.1561/0400000042.",
    },
    {
        "id": "eu-ai-act-2024-1689",
        "title": "Regulation (EU) 2024/1689 (Artificial Intelligence Act)",
        "authors": ["European Parliament", "Council of the European Union"],
        "publisher": "Official Journal of the European Union (Publications Office of the European Union)",
        "year": 2024,
        "kind": "regulation",
        "identifier": "OJ L, 2024/1689, 12.7.2024; CELEX: 32024R1689; ELI: http://data.europa.eu/eli/reg/2024/1689/oj",
        "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "summary": "The EU Artificial Intelligence Act lays down harmonised rules for AI in the "
                   "Union: it prohibits eight AI practices (Article 5(1)(a)-(h)), regulates "
                   "high-risk AI systems (Article 6, Annex III's eight areas), sets transparency "
                   "obligations for certain AI systems (Article 50), and governs general-purpose "
                   "AI models including a systemic-risk subcategory (Article 51). The final OJ "
                   "text comprises 13 chapters, 113 articles and 13 annexes. Adopted 13 June 2024 "
                   "and published in OJ L on 12 July 2024, it entered into force on 1 August 2024 "
                   "and applies in stages: Chapters I-II from 2 February 2025; GPAI, governance "
                   "and penalties provisions from 2 August 2025; general application from 2 "
                   "August 2026; Article 6(1) from 2 August 2027.",
    },
    {
        "id": "nist-ai-rmf-1-0-2023",
        "title": "Artificial Intelligence Risk Management Framework (AI RMF 1.0)",
        "authors": ["National Institute of Standards and Technology"],
        "publisher": "National Institute of Standards and Technology, U.S. Department of Commerce",
        "year": 2023,
        "kind": "framework",
        "identifier": "NIST AI 100-1; DOI 10.6028/NIST.AI.100-1",
        "url": "https://doi.org/10.6028/NIST.AI.100-1",
        "summary": "Voluntary, rights-preserving, non-sector-specific framework published in "
                   "January 2023, as directed by the National Artificial Intelligence Initiative "
                   "Act of 2020 (P.L. 116-283), to help organizations manage the risks of AI "
                   "systems and promote trustworthy and responsible development and use of AI. "
                   "Its Core comprises four functions - GOVERN, MAP, MEASURE, and MANAGE - "
                   "subdivided into 19 categories and 72 subcategories. The framework articulates "
                   "seven characteristics of trustworthy AI systems: valid and reliable; safe; "
                   "secure and resilient; accountable and transparent; explainable and "
                   "interpretable; privacy-enhanced; and fair with harmful bias managed. It is "
                   "accompanied by the companion AI RMF Playbook hosted in NIST's Trustworthy and "
                   "Responsible AI Resource Center (airc.nist.gov).",
    },
    {
        "id": "iso-iec-42001-2023",
        "title": "ISO/IEC 42001:2023 — Information technology — Artificial intelligence — "
                 "Management system",
        "authors": ["ISO/IEC JTC 1/SC 42 Artificial intelligence"],
        "publisher": "International Organization for Standardization / International Electrotechnical Commission",
        "year": 2023,
        "kind": "standard",
        "identifier": "ISO/IEC 42001:2023",
        "url": "https://www.iso.org/standard/81230.html",
        "summary": "First edition (December 2023) management-system standard specifying "
                   "requirements for establishing, implementing, maintaining and continually "
                   "improving an artificial intelligence management system (AIMS) within an "
                   "organization. Prepared by ISO/IEC JTC 1/SC 42 and structured on the ISO "
                   "harmonized structure with requirement clauses 4-10 (Context of the "
                   "organization, Leadership, Planning, Support, Operation, Performance "
                   "evaluation, Improvement). Annex A (normative) provides 38 reference controls "
                   "organized into 9 control objectives (A.2-A.10), with Annex B (normative) "
                   "giving implementation guidance for those controls, Annex C (informative) "
                   "listing potential AI-related organizational objectives and risk sources, and "
                   "Annex D (informative) covering use of the AIMS across domains or sectors. "
                   "Applicable to any organization that develops, provides or uses products or "
                   "services utilizing AI systems; its sole normative reference is ISO/IEC "
                   "22989:2022.",
    },
    {
        "id": "eu-dora-2022-2554",
        "title": "Regulation (EU) 2022/2554 (Digital Operational Resilience Act, DORA)",
        "authors": ["European Parliament", "Council of the European Union"],
        "publisher": "Official Journal of the European Union (Publications Office of the European Union)",
        "year": 2022,
        "kind": "regulation",
        "identifier": "CELEX:32022R2554; OJ L 333, 27.12.2022, p. 1-79; ELI: http://data.europa.eu/eli/reg/2022/2554/oj",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/2554/oj",
        "summary": "DORA establishes uniform requirements for the digital operational resilience "
                   "of the EU financial sector across five requirement areas: ICT risk management "
                   "(Ch. II), ICT-related incident management, classification and reporting (Ch. "
                   "III), digital operational resilience testing (Ch. IV), managing of ICT "
                   "third-party risk including an Oversight Framework for critical ICT "
                   "third-party service providers (Ch. V), and information-sharing arrangements "
                   "(Ch. VI). The regulation comprises 9 chapters and 64 articles and applies to "
                   "21 entity types enumerated in Article 2(1)(a)-(u), of which points (a)-(t) "
                   "are collectively defined as 'financial entities'. Adopted 14 December 2022, "
                   "published in OJ L 333 on 27 December 2022, it entered into force on 16 "
                   "January 2023 and applies from 17 January 2025.",
    },
    {
        "id": "mitchell-2019",
        "title": "Model Cards for Model Reporting",
        "authors": ["Margaret Mitchell", "Simone Wu", "Andrew Zaldivar", "Parker Barnes", "Lucy Vasserman", "Ben Hutchinson", "Elena Spitzer", "Inioluwa Deborah Raji", "Timnit Gebru"],
        "publisher": "Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT* '19), ACM",
        "year": 2019,
        "kind": "paper",
        "identifier": "doi:10.1145/3287560.3287596; FAT* '19 pp. 220-229; arXiv:1810.03993",
        "url": "https://doi.org/10.1145/3287560.3287596",
        "summary": "Proposes 'model cards' — short standardized documents accompanying trained ML "
                   "models that report benchmarked evaluation across cultural, demographic, "
                   "phenotypic, and intersectional groups relevant to intended application "
                   "domains. The framework comprises nine sections: Model Details, Intended Use, "
                   "Factors, Metrics, Evaluation Data, Training Data, Quantitative Analyses "
                   "(unitary and intersectional results), Ethical Considerations, and Caveats and "
                   "Recommendations. Demonstrated with example cards for a smiling-detection "
                   "image model and a toxic-comment text classifier. Published at ACM FAT* 2019 "
                   "(now FAccT).",
    },
]

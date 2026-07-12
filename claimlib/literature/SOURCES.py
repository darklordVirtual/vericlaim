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
]

# TODO — MCP Spec Compliance & Trends 2026

> Contenu genere par IA — validation humaine requise avant utilisation.
>
> Genere le 1er mars 2026 suite a l'audit cross-spec des repos mcp-openclaw-extensions
> et setup-vs-agent-firm. Base sur MCP 2025-03-26 -> 2025-11-25 et A2A v0.4.0.
>
> **Derniere mise a jour**: Tous les 20 items TERMINES — 113 tools / 25 modules / 311 tests / v2.2.0

---

## Sprint 1 — Conformite MCP 2025-11-25 (CRITICAL) DONE

### S1. Ajouter title aux 113 tools — DONE
### S2. Ajouter annotations aux 113 tools — DONE
### S3. Ajouter outputSchema aux 113 tools — DONE
### S4. Tool d'audit Elicitation compliance — DONE (spec_compliance.py)
### S5. Tool d'audit Tasks (durable requests) — DONE (spec_compliance.py)
### S6. Exposer Resources et Prompts — DONE (spec_compliance.py)

---

## Sprint 2 — Avantage competitif (HIGH) DONE

### H1. Aligner A2A Bridge sur v0.4.0 — DONE (a2a_bridge.py)
### H2. Prompt injection detection — DONE (prompt_security.py, 2 tools)
### H3. Audio content audit — DONE (spec_compliance.py)
### H4. OAuth / OIDC compliance audit — DONE (auth_compliance.py, 2 tools)
### H5. JSON Schema 2020-12 dialect — DONE (spec_compliance.py)
### H6. SSE polling / resumption audit — DONE (spec_compliance.py)
### H7. Icon metadata support — DONE (spec_compliance.py)

---

## Sprint 3 — Nice-to-have (MEDIUM) DONE

### M1. Tool deprecation lifecycle — DONE (compliance_medium.py)
### M2. Circuit breaker pattern audit — DONE (compliance_medium.py)
### M3. GDPR / data residency audit — DONE (compliance_medium.py)
### M4. Agent identity / DID — DONE (compliance_medium.py)
### M5. Multi-model routing audit — DONE (compliance_medium.py)
### M6. Resource links dans tool results — DONE (compliance_medium.py)
### M7. PRs manquantes — DONE (PR #3 parent + PR #6 extensions)

---

## Resume final

| Sprint | Items | Status | Resultat |
|--------|-------|--------|----------|
| Sprint 1 | S1-S6 | DONE | 113 tools avec title + annotations + outputSchema |
| Sprint 2 | H1-H7 | DONE | A2A v0.4.0 + 11 nouveaux tools + 3 modules |
| Sprint 3 | M1-M7 | DONE | 6 nouveaux tools + 2 PRs |
| **Total** | **20/20** | **ALL DONE** | **113 tools / 25 modules / 311 tests / v2.2.0** |

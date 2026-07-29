# Meridian Knowledge Store documents

Policy and SOP documents the AI reasons over. **Policy lives here; operational data (catalog, CRM,
orders) lives in the mock API** — the knowledge split that makes the demo honest: the AI *reasons* from
the store and *acts* on the API.

| Doc | Role in the demo |
|---|---|
| MER-POL-01 Returns & Refunds | 30-day standard window; §5.1 lets Care re-evaluate the store's denial |
| MER-POL-02 Northlight Circle Loyalty | **§3.1 the demo's hinge clause** — Summit = 45-day accessory window; §3.2 no approval needed; §4 bundle credit into the new purchase |
| MER-POL-03 Price Match & Credits | credit-stacking rules; §3.1 guardrail: no ad-hoc discounts |
| MER-POL-04 Shipping & Delivery | same-day dispatch cutoff; §3.2 SMS receipt consent |
| MER-POL-05 Recommendation Guidance | the SOP behind the comparison cards: stated needs, honest tradeoffs, never oversell, max two options |

## Workflow

1. Author/edit the `.md` files here (they are the source of truth).
2. Run `python tools/make_knowledge_txt.py` → writes `knowledge/upload/*.txt` (the store rejects `.md`).
3. Upload the `.txt` files to the `Meridian_Knowledge` store (or rebuild the package — the store ships
   bundled in the zip with chunks + embeddings).
4. Wait for each source to show status **ready** before demoing.

Clause numbers matter: the Policy Analyst quotes clauses verbatim on recommendation cards
(e.g. "MER-POL-02 §3.1"), so keep the §-numbering stable when editing.

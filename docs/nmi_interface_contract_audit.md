# NMI C_self interface-contract audit

This audit used frozen raw responses only and made zero model calls.

## Findings

- Matched DeepSeek: 288 proposal calls; 0 strict whole-response JSON; 0/4608 executable plan opportunities.
- Native DeepSeek: 288 proposal calls; reasoning was present in 288, but content was present in 0; 0/4608 executable plan opportunities.
- The proposal prompt listed operator names but not the exact parser-level argument contract. For example, the executor requires `node`/`other`/`kind`, while all matched proposal calls used at least one of the incompatible keys `source`/`target`/`type`.
- The permissive legacy extractor can recover an inner JSON object from a truncated outer response. Accordingly, 'JSON extractable' does not imply a valid top-level plan object.

## Interpretation

The observed autonomous failures are interface-confounded. They do not establish that the model failed to conceptualize an outside-space representation. A fair sensitivity must disclose the exact syntactic contract, reserve a separate final-answer budget and guarantee only grammar-level serialization, while keeping worlds, primitives, opportunities, hidden-information boundaries and J0-J5 unchanged.

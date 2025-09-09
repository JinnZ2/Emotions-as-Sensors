# Composite Emotions — Graph

> Atoms = circles; Composites = rounded boxes; family clusters shown with subgraphs.

```mermaid
graph TD
  %% Families
  subgraph Boundary
    A[anger]:::atom
    S[shame]:::atom
  end
  subgraph Loss
    G[grief]:::atom
    AB[abandonment]:::atom
  end
  subgraph Resonance
    L[love]:::atom
    C[compassion]:::atom
  end
  subgraph Radiant
    J[joy]:::atom
    AD[admiration]:::atom
  end
  subgraph Sharp
    F[fear]:::atom
    SP[surprise]:::atom
  end
  subgraph Balanced
    P[peace]:::atom
    CT[contentment]:::atom
  end
  subgraph Subtle
    LO[longing]:::atom
  end

  %% Composites
  BS((bittersweet)):::comp
  AW((awe)):::comp
  PF((protective_fury)):::comp
  AA((anxious_anticipation)):::comp
  RS((resentment)):::comp

  %% Edges
  J --> BS
  G --> BS
  SP --> AW
  AD --> AW
  A --> PF
  L --> PF
  F --> AA
  SP --> AA
  LO --> AA
  A --> RS
  G --> RS

  classDef atom fill:#fff,stroke:#999,stroke-width:1px;
  classDef comp fill:#f6f6ff,stroke:#6b6bff,stroke-width:1.5px;

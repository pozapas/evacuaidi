# V4 documentation-scope release

Date: 2026-07-19

This is a documentation-and-comment correction only.  It aligns the public
repository with the V4 manuscript scope and does not change source-code
algorithms, calibration inputs, random seeds, archived numerical results,
figures, or tables.

The release documents four facts that are material to interpretation:

1. the reported physical boundary force is a four-side outer-domain
   approximation, not a CAD-wall/obstacle force model;
2. the active social term uses continuous delayed directional-alignment
   weights, not an FDR-screened leader--follower network;
3. in the archived calibration `guidance_doors` is not supplied, so the
   formal guidance force is zero and `k_AI` is non-identifiable; and
4. the controlled scenarios record scenario status and available doors, not
   person-level directives, receipt, or response.

Accordingly, this release does not claim a new clean-environment reproduction
or a new empirical/causal marshal- or AI-guidance result.  The Git tag
`v4-documentation-scope-20260719` identifies this documentation release.

# Quality appraisal rubric

The two instruments used to appraise the studies reviewed in *Who Leads, Who Follows? A Review of Leadership and Guidance Dynamics in Evacuation*, with the anchors applied to each criterion.

Two instruments. Empirical and experimental studies are appraised with instrument A, simulation studies with instrument B, mixed studies with both. Each criterion is scored on three levels. No composite score is produced.

---

## Why three levels and no composite

Criterion-level frequencies are reported, not a ranked quality score. A composite invites a dispute about weighting that adds nothing: the appraisal exists to characterize the evidence base, not to rank individual studies. Three levels keep each judgment defensible from the text of the paper.

| Level | Meaning |
|---|---|
| **R** Reported | The item is present and specific enough to be checked or reproduced |
| **P** Partially reported | The item is addressed but incompletely, vaguely, or by reference only |
| **N** Not reported | No statement in the paper addresses the item |

`NA` is available where a criterion genuinely does not apply, and is reported separately rather than folded into `N`.

---

## Instrument A: empirical, experimental, and VR studies

Anchored in the Mixed Methods Appraisal Tool (MMAT), version 2018, adapted to evacuation research. The MMAT's two screening questions are applied first; a study failing both is recorded as not appraisable.

**Screening:** Are there clear research questions? Do the collected data address them?

| ID | Criterion |
|---|---|
| **A1** | Research question stated and the study design is appropriate to answer it |
| **A2** | Participants described (number, recruitment, relevant characteristics) and appropriate to the question |
| **A3** | Measurements and instruments described clearly enough to be repeated, including apparatus, scenario, and what was recorded |
| **A4** | Outcome data complete, with attrition, exclusions, or missing data addressed |
| **A5** | Confounders and sources of bias identified and accounted for, including the effect of the experimental setting on behavior |

**Reference:** Hong QN, Fàbregues S, Bartlett G, Boardman F, Cargo M, Dagenais P, et al. The Mixed Methods Appraisal Tool (MMAT) version 2018 for information professionals and researchers. *Education for Information*. 2018. doi:10.3233/efi-180221

---

## Instrument B: simulation studies

Anchored in the established verification and validation framework for building fire evacuation models.

| ID | Criterion |
|---|---|
| **B1** | Model description complete: governing rules or equations, behavioral assumptions, and geometry |
| **B2** | Parameter values sourced and justified, with an empirical or literature basis rather than assertion |
| **B3** | Verification or validation reported against analytical results, experimental data, other models, or documented incidents |
| **B4** | Sensitivity or robustness analysis reported, including the number of stochastic repeat runs where the model is non-deterministic |
| **B5** | Setup reproducible: software and version, scenario configuration, population, and initial conditions |

**References:**
- Ronchi E, Kuligowski ED, Reneke PA, Peacock RD, Nilsson D. *The Process of Verification and Validation of Building Fire Evacuation Models*. NIST Technical Note 1822. National Institute of Standards and Technology; 2013. doi:10.6028/NIST.TN.1822
- Ronchi E, Kuligowski ED, Nilsson D, Peacock RD, Reneke PA. Assessing the Verification and Validation of Building Fire Evacuation Models. *Fire Technology*. 2014. doi:10.1007/s10694-014-0432-3

**Handle with care.** The Associate Editor for this submission is an author of both references. That makes the framework the correct choice for the instrument, and it makes precision mandatory: B1 to B5 operationalize the verification and validation concepts described in that work for the purpose of appraising reporting completeness. The instrument must not be described as the authors' own V&V protocol, nor as an endorsement of this review by those authors. Every sentence written about this framework in §3.4 is to be checked against the source documents before submission.

---

## Application

1. Studies are triaged into simulation, empirical, mixed, or other from the coded data (`w2_classification.csv`), then confirmed against the full text when scored.
2. Scoring is done from each study's full text, not from the coding spreadsheet. The spreadsheet's Methodology column is AI-generated summary prose on a fixed template; it repeats the phrase "Experimental Design" for every study regardless of design, and it is not a sound basis for appraisal.
3. Each score carries a one-line justification quoting or pointing to the location in the paper.
4. Results are reported as criterion-level frequencies, with a stacked-bar summary figure and a study-by-criterion appendix table.

## Framing in the manuscript and response

§3.4 reports the appraisal as the execution of step three of the Khan et al. framework already cited in the Methods. The text states what the appraisal does and what it found. It does not narrate the reporting history of the submission.

Khan KS, Kunz R, Kleijnen J, Antes G. Five Steps to Conducting a Systematic Review. *Journal of the Royal Society of Medicine*. 2003. doi:10.1177/014107680309600304

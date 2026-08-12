# Consistency check

Ten studies were scored a second time, independently of the first pass, to measure the consistency of the appraisal. Exact agreement was 63 of 75 applicable criterion ratings.

---

## First scoring pass

```jsonl
{"id":"101","instrument":"A","study_type":"empirical","scores":{"A1":"R","A2":"P","A3":"R","A4":"P","A5":"P"},"evidence":{"A1":"Secs. 3-5 state a personal-network survey design and regression analyses for hurricane decision consistency and sharing.","A2":"Sec. 4 reports 90 online responses from FIU/South Florida networks, but convenience recruitment limits representativeness.","A3":"Sec. 4 describes a 70-question Qualtrics survey covering demographics, relationships, travel and evacuation scenarios.","A4":"Sec. 4 reports received responses but does not fully address item nonresponse, exclusions or analytic missingness.","A5":"Sec. 8 acknowledges survey and sampling limitations; self-report and FIU-network selection bias remain."},"coding":{"study_type":"empirical","participants_n":90,"setting":"survey","instrument":["questionnaire"],"model_class":["statistical"],"validation_reported":"no","leader_type":["none"]},"flags":["class-corrected"]}
{"id":"102","instrument":"A+B","study_type":"mixed","scores":{"A1":"R","A2":"R","A3":"R","A4":"P","A5":"P","B1":"R","B2":"P","B3":"R","B4":"R","B5":"P"},"evidence":{"A1":"Secs. 2-7 develop hidden-leader crowd control and test feasibility in a real student evacuation experiment.","A2":"Sec. 7 reports 76 first-year students (39 girls, 37 boys), randomly split into groups of 42 and 34.","A3":"Sec. 7 describes unfamiliar building routes, instructions, hidden leaders and video-derived participant trajectories.","A4":"Sec. 7 reports the two experimental groups, but exclusions and trajectory-data completeness are not addressed.","A5":"Unfamiliarity and random grouping are described, but class-student sampling and experiment setting effects are not controlled.","B1":"Secs. 2-6 give microscopic alignment/random-walk rules, leader dynamics, mesoscopic model and optimal-control formulation.","B2":"Secs. 2-6 specify model constants and scenarios, but most control/interaction values lack empirical calibration.","B3":"Sec. 7 compares predicted hidden-leader behavior with the real experiment and observed trajectories.","B4":"Secs. 5-6 compare control strategies and Table 5.2 reports multiple random-initial-condition runs.","B5":"Secs. 2-7 detail equations, rooms, leaders and experiments, but software/version and full numerical setup are absent."},"coding":{"study_type":"mixed","participants_n":76,"setting":"lab","instrument":["camera","tracking"],"model_class":["ABM","other"],"validation_reported":"yes","leader_type":["human"]},"flags":["class-corrected"]}
{"id":"114","instrument":"A","study_type":"empirical","scores":{"A1":"R","A2":"R","A3":"R","A4":"R","A5":"P"},"evidence":{"A1":"Sec. 2 tests how signs, simulated crowd movement and memory affect exit choices in a controlled virtual evacuation.","A2":"Sec. 2 reports a total of 570 participants and the analyzed experimental samples.","A3":"Secs. 2.1-2.4 describe the interactive virtual environment, treatments, simulated crowds and recorded route choices.","A4":"Sec. 2 reports treatment samples and Sec. 3 analyzes the route-choice outcomes for the completed trials.","A5":"Treatment contrasts are controlled, but virtual setting and participant-sampling effects on real evacuation behavior remain."},"coding":{"study_type":"empirical","participants_n":570,"setting":"VR","instrument":["HMD","tracking"],"model_class":["none"],"validation_reported":"no","leader_type":["signage"]},"flags":[]}
{"id":"115","instrument":"A","study_type":"empirical","scores":{"A1":"R","A2":"P","A3":"R","A4":"R","A5":"P"},"evidence":{"A1":"Secs. 1-5 use a computer experiment and Bayesian model selection to examine dynamic virtual-evacuation route choice.","A2":"Methods report 464 participants, but recruitment and participant characteristics are incompletely described.","A3":"Secs. 3-5 specify virtual route-choice scenarios, changing queues/exits, pressure treatment and recorded choices.","A4":"Secs. 3-5 analyze the completed route-choice trials and model-selection results; missing data are not prominent.","A5":"Experimental treatments are controlled, but virtual behavior and stress manipulation are not direct real-evacuation evidence."},"coding":{"study_type":"empirical","participants_n":464,"setting":"VR","instrument":["tracking"],"model_class":["statistical"],"validation_reported":"no","leader_type":["signage"]},"flags":[]}
{"id":"131","instrument":"A+B","scores":{"A1":"R","A2":"P","A3":"R","A4":"P","A5":"P","B1":"R","B2":"R","B3":"P","B4":"R","B5":"P"}}
{"id":"134","instrument":"A","scores":{"A1":"R","A2":"R","A3":"R","A4":"P","A5":"P"}}
{"id":"135","instrument":"A+B","scores":{"A1":"R","A2":"R","A3":"R","A4":"P","A5":"P","B1":"R","B2":"R","B3":"R","B4":"R","B5":"P"}}
{"id":"144","instrument":"B","scores":{"B1":"R","B2":"P","B3":"N","B4":"P","B5":"P"}}
{"id":"176","instrument":"A+B","scores":{"A1":"R","A2":"P","A3":"R","A4":"P","A5":"P","B1":"R","B2":"R","B3":"R","B4":"P","B5":"P"}}
{"id":"209","instrument":"A+B","scores":{"A1":"R","A2":"R","A3":"R","A4":"P","A5":"P","B1":"R","B2":"R","B3":"R","B4":"R","B5":"P"}}
```

## Second scoring pass, scored independently

| ID | Scores in criterion order |
|---|---|
| 101 | A1-A5: R,P,R,P,P |
| 102 | A1-A5: R,P,P,P,P; B1-B5: R,P,P,P,P |
| 114 | A1-A5: R,R,R,R,P |
| 115 | A1-A5: R,P,R,P,P |
| 131 | A1-A5: R,P,R,P,P; B1-B5: R,R,P,P,P |
| 134 | A1-A5: R,R,R,P,P |
| 135 | A1-A5: R,R,R,P,P; B1-B5: R,P,R,P,P |
| 144 | B1-B5: R,N,N,P,P |
| 176 | A1-A5: R,R,R,P,P; B1-B5: R,P,R,P,P |
| 209 | A1-A5: R,R,R,R,P; B1-B5: R,R,R,R,P |

## Agreement

Exact code agreement was 63/75 applicable criterion ratings (84.0%). The two passes were made independently, without reference to the first set of codes.

| Criterion | Agreement |
|---|---:|
| A1 | 9/9 (100.0%) |
| A2 | 7/9 (77.8%) |
| A3 | 8/9 (88.9%) |
| A4 | 7/9 (77.8%) |
| A5 | 9/9 (100.0%) |
| B1 | 6/6 (100.0%) |
| B2 | 3/6 (50.0%) |
| B3 | 5/6 (83.3%) |
| B4 | 3/6 (50.0%) |
| B5 | 6/6 (100.0%) |

Disagreements clustered in evidence thresholds for parameter justification (B2) and sensitivity/repeat-run reporting (B4), rather than study-type classification or model-description completeness.

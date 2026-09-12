# Evaluator review and corrections

Code-owl reviews ran in a GPT Terra-class subagent as required by AGENTS.md.
The reviewer did not participate in consumer trials and received the evaluator
contract. No findings were silently counted as product failures.

| Finding | Disposition |
|---|---|
| Consumer/oracle sibling paths were guessable | Unrelated consumer roots before native probes; later added private parent for nested traversal. Known cross-trial trace exposure invalidates a trial. OS-wide read isolation is not claimed. |
| Process exit zero could be confused with a pass | Extractor never grants semantic passes. Every gate remains failed/unknown until evidence supports it. |
| Native self-report insufficient | Codex raw host instruction events retained, including formatting. Claude injection bytes remain unknown. |
| Model/version missing | Host version and model identity retained per trial; unavailable astra probe and gpt-5.5 scope change disclosed. |
| Oracle coupled to generated routing | Separate evaluator-owned semantic oracle frozen before behavior; candidate-generated views do not author expected answers. |
| Missing failed-attempt ledger / host stop | Later batch scheduler records plans and launch failures, examines stderr/result status and stops after repeated host failures. Original active candidate batch was monitored and completed all 78 attempts without process failures. |
| Shell read counts could include echo/redirection targets | Conservative operand parser; globs/variables remain unknown; six regression checks cover false counting and duplicate reads. |
| Write actions could be missed | Direct write counts labeled lower bounds; raw calls and Git diffs/commit paths retained for adjudication. |
| Human task 3 lacked retry objective / had wrong key | Corrected before issuing any reader packages; zip refreshed; zero readers have participated. |
| Delegated role ambiguous | Original "new implementer" prompts excluded from the subagent-role gate; explicit-role repetitions 4–6 precede actual fresh-session child trials. |

Maintenance prompts were corrected before execution to permit local commits in
disposable consumer repositories. Pushes/network services remain forbidden. Refused
commits will be marked unavailable, not counted as zero maintenance burden.

No product code changed. Native startup/read-budget failures are evaluation outcomes;
no speculative instruction rewrite was used to turn failed trials into passes.

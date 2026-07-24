# Code Merging (v0 to v1)

- unified references to system to "LLM" (previously "chatbot" or "LLM")
- unified casing across several codes
- merged sub- or superstring codes (e.g. "[some action] (contd.)" to "[some action]")
- corrected one problematic code ([13.014.5]): "correcting" usually used when the LLM was perceived wrong, this case was a self-correction
- merge identical or very similar codes to the same wording

# Pattern Coding (v1 to v2)

- introduce pattern codes "restating given information", "restating solution step", "restating problem goal", and "Restating LLM approach"
- introduced pattern codes "deciding to ask LLM for information", "deciding to ask LLM for verification", "deciding to ask LLM for guidance", "deciding to ask LLM for solution", "deciding next solution step", "Deciding to manually validate", "Deciding to update the LLM information", "Deciding to follow LLM advice", "Deciding to verify LLM output", and "Deciding to attempt solution without LLM"
- re-coded all statements previously coded with "Reading LLM response aloud" to reflect content detail
- re-coded 05.005.9 and 04.036.1 to better fit new pattern codes
- introduced pattern codes "reading LLM's CoT", "reading LLM's guidance", "reading LLM's questions", "reading LLM's restaded known information", "reading LLM's feedback", "reading given information", "reading problem statement"
- introduce pattern codes "identifying mistake", "identifying given information", "identifying unkown information", "identifying solution step", "identifying problem solvability", and "identifying own knowledge gap"
- "confirming solution steps", "confirmation of problem facts", "confirming LLM's guidance", "accpeting LLM's assertions", "deriving solution step", "Requesting formula from LLM", "Requesting formula confirmation from LLM", "managing experiment logistics"
- remapped several codes from "confirming" family to existing codes
- introduced pattern codes "expressing confidence", "expressing satisfaction", "expressing uncertainty", "expressing doubt", "expressing insight", "expressing frustration", "Considering querying LLM as fallback", "expressing surprise", "Encountering impasse"
- remapped several codes from "expressing" family to existing codes
- introduced pattern codes "requesting information from LLM", "requesting verification by LLM", "requesting guidance from LLM", "requesting clarification from LLM", "requesting clarification from researcher", "requesting solution from LLM", "Encountering impasse"
- introduced pattern codes "planning next solution step", "planning LLM message"
- introduced pattern codes "managing experiment logistics", "questioning problem language", "questioning oneself", "questioning LLM output"
- introduced pattern codes "recognizing own error", "recognizing error (no fault)", "recognizing solution step"
- introduced pattern codes "submitting information to LLM", "answering the LLM"
- introduced pattern codes "correcting the LLM", "correcting own solution step", "correcting own understanding", "correcting own terminology"
- mapped "calculation" and "performing" family to "deriving solution step"
- introduced pattern code "Verifying solution"
- introduced pattern codes "recalling earlier LLM feedback", "noticing problem", "noting given information", "evaluating response as unhelpful"

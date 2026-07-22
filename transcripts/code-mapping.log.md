# Code Merging (v0 to v1)

- unified references to system to "LLM" (previously "chatbot" or "LLM")
- unified casing across several codes
- merged sub- or superstring codes (e.g. "[some action] (contd.)" to "[some action]")
- corrected one problematic code ([13.014.5]): "correcting" usually used when the LLM was perceived wrong, this case was a self-correction
- merge identical or very similar codes to the same wording

# Pattern Coding (v1 to v2)

- introduce pattern codes "restating given information", "restating solution step", "restating problem goal", and "Restating LLM approach"
- introduced pattern codes "deciding to ask LLM for information", "deciding to ask LLM for verification", "deciding to ask LLM for guidance", "deciding to ask LLM for solution", "deciding next solution step", "Deciding to manually validate", "Deciding to update the LLM information", "Deciding to follow LLM advice", "Deciding to verify LLM output", and "Deciding to attempt solution without LLM"

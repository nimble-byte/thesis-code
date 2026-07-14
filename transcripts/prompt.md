I'm continuing my master's thesis (DSR, Moeller's MDPD reflective approach, RQ1–RQ3 on ToM attribution to LLMs with/without CoT explanations). This thread picks up Chapter 6 coding at the transcript-reformatting stage. The format below was finalized in a prior thread — apply it, don't re-derive it.

GOAL FOR THIS THREAD: transform participant transcripts (raw `NN.raw.txt`, one per participant) into the format below to prepare for coding. The actual coding work will be done in separate threads

FINALIZED TRANSCRIPT FORMAT:

* Every real speaker turn (Proband spoken, Proband written, LLM, Researcher) gets a sequential 3-digit turn number, continuous across the file, no participant prefix inside the file.
* Turn header line: [NNN CHANNEL], replacing the old speaker-label line entirely. CHANNEL is one of: SPOKEN, WRITTEN, LLM, RESEARCHER.
* Stage directions (e.g. "[Proband liest die Antwort]") get no ID and do NOT advance the turn counter — they stay as plain bracketed lines exactly where they occur.
* Within SPOKEN/WRITTEN turns only, each clause/statement gets its own line, tagged [NNN.n] (e.g. [004.1], [004.2]). LLM and RESEARCHER turns are not split — single uncoded block under their turn header.
* LLM output cleanup: unescape literal \n\n into real line breaks; normalize math notation to the plain-unicode style already used elsewhere in the transcripts (e.g. d = |A·a + B·b + C| / √(A² + B²)) rather than raw LaTeX escapes. Keep markdown bold (**text**) as literal asterisks — do not strip it.
* File-level YAML style header, first line of the file: [PARTICIPANT: <ID> | UUID: <UUID> | GROUP: <E/B>]. The information is available in the `participant_metadata.csv` file
* Task transition header, replacing the old "[Proband wechselt zur nächsten Aufgabe]" line: [TASK <task-id> | DIFFICULTY <medium/hard>]. The exact tasks and difficulty need to be filled afterwards manually. Please insert the example as placeholder.
* Old files and old codes (descriptive/process/axial/theoretical, from the prior thesis attempt) are NOT touched and NOT migrated — archived as-is. New transcripts are new files coexisting alongside the old ones.

Here is an example of the beginning of `12.raw.txt`:

```
---
PARTICIPANT: 12
UUID: 473ee59a-2809-485a-a7ca-5d2f8f776bca
GROUP: B
---
[001 RESEARCHER]
    So, wenn wir den anschmeißen, der schlägt aus. Das heißt, der ist happy, gibt ich dir das Aufgabenset.
[002 SPOKEN]
[002.1]    So, was haben wir hier?
[002.2]    Radius von 5.
[002.3]    So.
[Proband schreibt eine Nachricht]
[003 RESEARCHER]
    Bitte laut, was so bei dir im Kopf vorgeht.
[004 WRITTEN]
[004.1]    wie berechne ich eine linie zwischen zwei punkten im Kreis
[005 LLM]
    Um die Linie zwischen zwei Punkten in einem Kreis zu berechnen, gibt es mehrere Schritte, die du beachten musst. Lass uns gemeinsam überlegen, wie du vorgehen kannst:

    1. Punkte identifizieren: Hast du die Koordinaten der beiden Punkte, die du verbinden möchtest? Diese sind normalerweise als (x₁, y₁) und (x₂, y₂) gegeben.

    2. Kreisgleichung: Weißt du, wie die Gleichung des Kreises aussieht? ...
[Proband liest die Antwort]
```

ADDITIONAL REMARKS, on questions that might arise:

* there's no reliable log of whether group-E participants actually expanded the explanation panel versus it just being available. Treat "explanation available" and "explanation viewed" as indistinguishable in this dataset.
* Participant 12 is excluded from the study overall and does not need to be formatted into the new format. It was used as illustrative example for calibration in a previous thread, which is why it is included as example.
* participant numbering has gaps; the numerical IDs were assigned in the order the participants were contacted. Some did not respond, could not or did not want to participate.

Please consider the decisions made final. Ask questions if things are unclear, but do not challenge decisions, they have been weighed.

If this thread approaches its length limit before all files are done, stop cleanly after finishing the current file and let me know which files remain — we'll continue in a fresh thread rather than pushing through.

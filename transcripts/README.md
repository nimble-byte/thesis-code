# Transcript README

This README focuses on the transcriptions, the coding process and the tooling used for second cycle coding. The basic structure of the folder is as follows:

```

```

## Procedure

1. Transcripts were transformed from the raw format into a semi-structured format using an LLM
   1. Each transcript was transformed in a new session using the same prompt
   2. Once transformation was complete, the [`validate_transcripts.py`](./validate_transcripts.py) was used to check transcripts transformation failures
2. Each transcript was coded in a single pass for process codes with accompanying in vivo citations
3. Coded transcriptions were combined into a single codebook using the `build` command of [`codebook.py`](./codebook.py)
4. Codes were mechanically combined when they differed in casing of words or were direct sub- or super-codes of each other (Saldana pattern-mapping)
5. Codes were pattern coded in groups based on the primary verb in the process code (using the `--group-by-verb` flag of [`codebook.py`](./codebook.py)). Coding was ended, once verb families became too small (~8 codes) to meaningfully combine internally
6. Codes were pattern coded based on semantic blocks to clean up large batches of small verb family codes.

## Tools

Several small python tools have been purpose built for the coding procedure. The core is the [codebook tool](#codebook-tool) which was used to view and update the codebook variants throughout the coding process. Additional tools are the [transcript validator](#transcript-validator) and the [command generator](#command-generator).

### Transcript Validator

The [transcript validator](./validate_transcripts.py) was built to ensure the LLM transformed transcripts were functionally identical to the original raw transcribed versions with no material changes. It ran the following checks:

- correct transcription of the header metadata
- channel labels are in the set "SPOKEN", "WRITTEN", "LLM", "RESEARCHER"
- Turns are correctly ordered (in sequence, no gaps)
- Statements are correctly ordered and nested (in sequence, no gaps)
- stage directions / annotations are correctly transported
- dummy task headers are injected
- content is complete line by line (this included a warning for lines containing math, which were normalised during transformation)

```shell
# to run full check
python ./validate_transcripts.py
# to run individual participant check
python ./validate_transcripts.py 01
```

### Codebook Tool

The [codebook tool](./codebook.py) was the core tool used to generate and update codebooks during coding. The tool holds functionality to view, update and validate input codebook.

### Command Generator

Generated update commands using [`codebook.py`](./codebook.py) for changing batches of codes. Could be run in batch to speed up things.

## Coding Passes

### 2.2 Semantic Blocks

Once the verb based pattern coding was yielding limited benefits (verb groups smaller than 8), pattern coding was organised using semantic blocks. The used semantic blocks can be found below.

Codes were filtered using the below command and then checked one by one for a fitting cluster (including the option to create new clusters).

```shell
python ./codebook.py view ./codebooks/codebook_v2.csv --column pattern_code --group-by-verb -o ./semantic-block.csv --filter-verb reviewing, describing, seeking, specifying, orienting, reformulating, reiterating, summarizing, categorizing, commenting, consolidating, enumerating, extracting, understanding, decoding, asserting, relating, reframing
```

| Block                                                  | Verb set                                                                                                                                                                                                                                                | n   |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| B1 — Equation setup/manipulation                       | setting, completing, rearranging, assigning, substituting, mapping, canceling, adding, formalizing, introducing, reusing, simplifying, writing, reformatting                                                                                            | 38  |
| B2 — Calculations & solving                            | solving, applying, computing, converting, determining, estimating, predicting, summing, working, arriving, executing, miscalculating, obtaining, recalculating, redoing, resuming, rounding, taking, vocalizing                                         | 33  |
| B3 — LLM Message writing and logistics                 | composing, reporting, querying, verbalizing, providing, repeating, answering, answerig, framing, referencing, rehearsing, relaying, returning, sharing, deliberating                                                                                    | 41  |
| B4 — LLM response reading                              | locating, realizing, recounting, paraphrasing, misreading, following                                                                                                                                                                                    | 13  |
| B5 — Problem comprehension, restating & representation | reviewing, describing, seeking, specifying, orienting, reformulating, reiterating, summarizing, categorizing, commenting, consolidating, enumerating, extracting, understanding, decoding, asserting, relating, reframing                               | 49  |
| B6 — Verification & error detection                    | verifying, recomputing, comparing, searching, flagging, noticing, testing, detecting, judging, reconfirming, assessing, suspecting, pausing, appraising                                                                                                 | 31  |
| B7 — Hypothesis, strategy, reasoning & appraisal       | attempting, anticipating, extending, reassessing, beginning, elaborating, rejecting, adopting, connecting, declaring, forming, initiating, restarting, skipping, speculating, strategizing, trying, weighing, affirming, justifying, claiming, deriving | 37  |
| B8 — Answer selection & task/session closure           | selecting, eliminating, transitioning, committing, finalizing, matching                                                                                                                                                                                 | 13  |
| B9 — Diagram, sketch & paper/note work                 | labeling, placing, sketching, annotating, marking, transcribing, visualizing, accepting, counting, examining, redrawing, externalizing, constructing, copying                                                                                           | 36  |
| B10 — Stance, affect & self-monitoring                 | signaling, adjusting, abandoning, making, trailing, voicing, hesitating, reacting                                                                                                                                                                       | 14  |
| B11 — Tool & interface logistics / offloading channels | using, naming, agreeing, entering, improvising, navigating, retrieving, switching, typing, struggling                                                                                                                                                   | 12  |

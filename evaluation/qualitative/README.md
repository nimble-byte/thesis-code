# Transcript README

This README focuses on the transcriptions, the coding process and the tooling used for second cycle coding. The structure of the quantitative evaluation is documented for completeness. The basic structure of the folder is as follows:

```sh
evaluation/
├── qualitative/
│   ├── README.md
│   ├── codebook.py              # primary tool for codebook manipulation
│   ├── code-mapping.log.md      # working notes of coding changes
│   ├── codebooks/
│   ├── codes/                   # transcript codes
│   ├── formatted/               # formatted transcripts
│   ├── helpers/                 # helper scripts
│   ├── metadata/
│   ├── notes/
│   └── raw/                     # raw transcripts
└── quantitative/
    ├── README.md
    ├── evaluation.ipynb.        # main evaluation notebook
    ├── constants.py             # techincal constants
    ├── data/                    # input data for the quantitative evaluation
    └── out/                     # charts, data output of the quantitative evaluation
```

## Transcript Format

The raw transcripts were formatted with additional information to better support the coding process:

1. Formalisation of 4 channels: RESEARCHER, [PARTICIPANT] SPOKEN, [PARTICIPANT] WRITTEN, LLM
2. addition of turn IDs incrementing every time the channel changes
3. addition of statement IDs incrementing with each line break/statement from the raw transcript
4. addition of metadata header with: `PARTICIPANT`, `GROUP`, and `UUID` (*the UUID was intended to be used to reference questionnaire results, which was ultimately not done*)
5. task header containing the task ID and difficulty as coding context

## Procedure

1. Transcripts were preprocessed from the raw format into a semi-structured format
   1. Each transcript was transformed using [`transform_transcripts.py`](./helpers/transform_transcripts.py)
   2. Additional metadata (e.g., task ID and difficulty) were annotated manually
   3. Once transformation was complete, the [`validate_transcripts.py`](./helpers/validate_transcripts.py) was used to check transcripts for transformation errors
2. Each transcript was coded in a single pass for process codes with accompanying in vivo citations
3. Coded transcriptions were combined into a single codebook using the `build` command of [`codebook.py`](./codebook.py)
4. Codes were mechanically combined when they differed in casing of words or were direct sub- or super-codes of each other
5. Codes were pattern coded in groups based on the primary verb in the process code (using the `--group-by-verb` flag of [`codebook.py`](./codebook.py)). Coding was ended, once verb families became too small (~8 codes) to meaningfully combine internally
6. Codes were pattern coded based on semantic blocks to clean up large batches of small verb family codes.

## Tools

Several small python tools have been purpose built for the coding procedure. The core is the [codebook tool](#codebook-tool) which was used to view and update the codebook variants throughout the coding process. Additional tools are the [transcript validator](#transcript-validator) and the [command generator](#command-generator).

### Transcript Validator

The [transcript validator](./helpers/validate_transcripts.py) was built to ensure the LLM transformed transcripts were functionally identical to the original raw transcribed versions with no material changes. It ran the following checks:

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

Generated update commands using [`codebook.py`](./codebook.py) for changing batches of codes ([code](./helpers/working_patterns_to_commands.py)).

## Second Cycle Coding Passes

### 2.1 Verb Groups

Initially codes were grouped by the lead verb of the process code. All codes were compared, and similar codes were combined into a `pattern_code`. Verbs were processed by the number of codes per lead verb in descending order.

### 2.2 Semantic Blocks

Once the verb based pattern coding was yielding limited benefits (verb groups smaller than 8), pattern coding was organised using semantic blocks. The used semantic blocks can be found below.

Codes were filtered using the below command and then checked one by one for a fitting cluster (including the option to create new clusters).

| Block                                  | Verb set                                                                                                                                                                                                                                                | n   |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- |
| B1 — Equation setup/manipulation       | setting, completing, rearranging, assigning, substituting, mapping, canceling, adding, formalizing, introducing, reusing, simplifying, writing, reformatting                                                                                            | 38  |
| B2 — Calculations and solving          | solving, applying, computing, converting, determining, estimating, predicting, summing, working, arriving, executing, miscalculating, obtaining, recalculating, redoing, resuming, rounding, taking, vocalizing                                         | 33  |
| B3 — LLM Message writing and logistics | composing, reporting, querying, verbalizing, providing, repeating, answering, answerig, framing, referencing, rehearsing, relaying, returning, sharing, deliberating                                                                                    | 41  |
| B4 — LLM response reading              | locating, realizing, recounting, paraphrasing, misreading, following                                                                                                                                                                                    | 13  |
| B5 — Problem reading                   | reviewing, describing, seeking, specifying, orienting, reformulating, reiterating, summarizing, categorizing, commenting, consolidating, enumerating, extracting, understanding, decoding, asserting, relating, reframing                               | 49  |
| B6 — Verification and error detection  | verifying, recomputing, comparing, searching, flagging, noticing, testing, detecting, judging, reconfirming, assessing, suspecting, pausing, appraising                                                                                                 | 31  |
| B7 — Hypothesis, strategy, reasoning   | attempting, anticipating, extending, reassessing, beginning, elaborating, rejecting, adopting, connecting, declaring, forming, initiating, restarting, skipping, speculating, strategizing, trying, weighing, affirming, justifying, claiming, deriving | 37  |
| B8 — Answer selection                  | selecting, eliminating, transitioning, committing, finalizing, matching                                                                                                                                                                                 | 13  |
| B9 — Note taking                       | labeling, placing, sketching, annotating, marking, transcribing, visualizing, accepting, counting, examining, redrawing, externalizing, constructing, copying                                                                                           | 36  |
| B10 — Self-monitoring                  | signalling, adjusting, abandoning, making, trailing, voicing, hesitating, reacting                                                                                                                                                                       | 14  |
| B11 — Tools and offloading             | using, naming, agreeing, entering, improvising, navigating, retrieving, switching, typing, struggling                                                                                                                                                   | 12  |

## Command Library

```shell
# codebook view based on relevant column
python ./codebook.py view ./codebooks/codebook_v3.csv --column theme_code
python ./codebook.py view ./codebooks/codebook_v2.csv --column pattern_code
python ./codebook.py view ./codebooks/codebook_v1.csv --column canonical_code
python ./codebook.py view ./codebooks/codebook_v0.csv --column raw_code

# create a specific semantic block view
python ./codebook.py view ./codebooks/codebook_v2.csv --column pattern_code --group-by-verb -o ./semantic-block.csv --filter-verb using, naming, agreeing, entering, improvising, navigating, retrieving, switching, typing, struggling

# build v0 codebook from scratch
python ./codebook.py build "./codes/**.codes.txt" --out ./codebooks/codebook_v0.csv

# validate all transcripts
python ./helpers/validate_transcripts.py [PARTICIPANT_ID]
```

Because shell reverse search sucks:

```shell
# code setup for "heuristic vs. deliberate acceptance"
python ./codebook.py view ./codebooks/codebook_v3.csv --column pattern_code --filter-code "confirming LLM's guidance", "accepting LLM's assertions", "deciding to follow LLM guidance", "following LLM guidance", "building on LLM's guidance", "deciding to update the LLM information", "rejecting LLM's guidance", "scrutinizing LLM response", "evaluating LLM response as unhelpful", "evaluating LLM as helpful", "questioning LLM output", "deciding to verify LLM output", "correcting the LLM", "criticizing the LLM", "judging LLM's statement as incorrect", "recognizing LLM error", "observing LLM as stuck"
```

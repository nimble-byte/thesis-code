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

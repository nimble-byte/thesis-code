The validation should at least check the following criteria (open to dicsussion):

- every content line from the raw file (Proband, LLM, Researcher, stage directions) survives somewhere in the reformatted file — nothing dropped or duplicated
- turn numbers are strictly sequential with no gaps or repeats
- every statement ID (NNN.n) nests under a turn number that actually exists
- channel tags are limited to the four allowed values
- stage directions are byte-identical to the raw file, unchanged
- the file header's participant ID, UUID, and group match participant_metadata.csv exactly — this one's worth having a script check by default now, given we just caught a manual mismatch on the P12 example by hand

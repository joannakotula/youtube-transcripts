DEFINITIONS_DATA_DIR=data/definitions
TRANSCRIPTS_DATA_DIR=data/transcripts

OUT_DIR=transcripts/

DEFINITIONS=$(wildcard ${DEFINITIONS_DATA_DIR}/*)
TARGETS=$(patsubst ${DEFINITIONS_DATA_DIR}/%.yaml,${OUT_DIR}/%.md,${DEFINITIONS})


all: ${TARGETS}

${OUT_DIR}/%.md: ${DEFINITIONS_DATA_DIR}/%.yaml ${TRANSCRIPTS_DATA_DIR}/%.yaml
	python3 scripts/generate_article.py -d ${DEFINITIONS_DATA_DIR}/$*.yaml -t ${TRANSCRIPTS_DATA_DIR}/$*.yaml -o $@


${TRANSCRIPTS_DATA_DIR}/%.yaml: ${DEFINITIONS_DATA_DIR}/%.yaml
	python3 scripts/download.py --definition $< --out $@

.PRECIOUS: ${TRANSCRIPTS_DATA_DIR}/%.yaml 
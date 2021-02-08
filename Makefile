SHELL:=/bin/bash

all:
	@echo "choose explicit target = type 'make ' and press TAB"

S=scripts


# ===== MAIN STUFF 

# basename of the text ('the book') for which we create an index
BOOK=mnym

# a general freqlist for comparison
GENE_FREQ=mnsz_fq_10.csv

# -----

BOOKDIR=$(BOOK)

# the original text as a pdf file
BOOK_INPUTPDF=$(BOOKDIR)/input.pdf
# the text for input as a .txt  file
BOOK_INPUTTXT=$(BOOKDIR)/input.txt
# the txt -- each line prepended with page number
BOOK_PAGENUMS=$(BOOKDIR)/pagenums.txt
BOOK_WITHPAGENUMS=$(BOOKDIR)/withpagenums.txt
BOOK_ONLYPAGENUMS=$(BOOKDIR)/onlypagenums.txt
# freqlist of BOOK
BOOK_FREQ=$(BOOKDIR)/fq.csv
# the final index file
BOOK_INDEX=$(BOOKDIR)/index.html
BOOK_INDEXPDF=$(BOOKDIR)/index.pdf

# analysed by emtsv
BOOK_ANA=$(BOOKDIR)/ana.csv
# lemmatized version = detokenized from $(BOOK_ANA)
BOOK_LEMMA=$(BOOKDIR)/lemma.txt

EXCLUDE=$(BOOKDIR)/exclude_list.txt
INCLUDE=$(BOOKDIR)/include_list.txt

full_run: ana index

N=500
index: freqlist pagenums
	@echo
	@echo " Creating the index -> '$(BOOK_INDEX)' and '$(BOOK_INDEXPDF)'"
	@echo
	python3 $S/create_index.py -b $(BOOK_PAGENUMS) -f $(BOOK_FREQ) -g $(GENE_FREQ) -n $N --exclude-list $(EXCLUDE) --include-list $(INCLUDE) | markdown_py > $(BOOK_INDEX)
	pandoc $(BOOK_INDEX) --pdf-engine=pdflatex -V 'fontfamily:dejavu' -o $(BOOK_INDEXPDF)


# XXX PAGES hardcoded, can be obtained from pdftotext output?
PAGES=204
pagenums: detok_lemma
	@echo
	@echo " Creating lemmatized txt version with page numbers -> '$(BOOK_PAGENUMS)'"
	@echo
	for i in $$(seq 1 $(PAGES)) ; do pdftotext -f $$i -l $$i $(BOOK_INPUTPDF) - | sed "s/^/$$i\t/"; done > $(BOOK_WITHPAGENUMS)
	cat $(BOOK_WITHPAGENUMS) | cols 1 > $(BOOK_ONLYPAGENUMS)
	paste $(BOOK_ONLYPAGENUMS) $(BOOK_LEMMA) > $(BOOK_PAGENUMS)

freqlist: detok_lemma
	@echo
	@echo " Creating freqlist -> '$(BOOK_FREQ)'"
	@echo
	cat $(BOOK_LEMMA) | wordperline | sstat | sstat2tsv | grep -v $$'\t$$' > $(BOOK_FREQ)

# skip emtsv header with `tail -n +2`
# prereq: `make ana` -- separated, because it takes time!
detok_lemma:
	@echo
	@echo " Detokenizing emtsv output -> '$(BOOK_LEMMA)'"
	@echo
	cat $(BOOK_ANA) | tail -n +2 | python3 $S/detok_lemma.py > $(BOOK_LEMMA)

# XXX remove line-ending TABs for emtsv by sed
ana: totxt
	@echo
	@echo " Lemmatizing '$(BOOK_INPUTTXT)' with emtsv -> '$(BOOK_ANA)' -- this step takes time!"
	@echo
	time cat $(BOOK_INPUTTXT) | brutetok | sed $$'s/\t*$$//' | docker run --rm -i mtaril/emtsv tok,morph,pos | cols 1-4 > $(BOOK_ANA)

# XXX igaziból ez nem is kell
# XXX elég lenne a 'pagenums' verzióból dolgozni
totxt:
	@echo
	@echo " Converting '$(BOOK_INPUTPDF)' to '$(BOOK_INPUTTXT)'"
	@echo
	pdftotext $(BOOK_INPUTPDF) $(BOOK_INPUTTXT)


# ===== OTHER STUFF

VERBOSE=-v
freqlists_test: freqlist
	@echo "--- $@" 1>&2
	python3 $S/freqlists.py -1 $(BOOK_FREQ) -2 $(GENE_FREQ) -H $N $(VERBOSE) > $(BOOKDIR)/compare.out

WORD=manysi
search_words:
	@echo "--- $@" 1>&2
	cat mnym_pagenums.txt | grep -i $(WORD) | sed "s/ === .*//" | sstat | sstat2tsv | colsortn 2


# ===== OBSOLETE

# XXX PAGES hardcoded, can be obtained from pdftotext output?
PAGES=204
wordform_pagenums:
	@echo
	@echo " Creating txt version with page numbers -> '$(BOOK_PAGENUMS)'"
	@echo
	for i in $$(seq 1 $(PAGES)) ; do pdftotext -f $$i -l $$i $(BOOK_INPUTPDF) - | sed "s/^/$$i\t/"; done > $(BOOK_PAGENUMS)

# XXX remove line-ending TABs for emtsv by sed
wordform_freqlist: totxt
	@echo
	@echo " Creating freqlist -> '$(BOOK_FREQ)'"
	@echo
	cat $(BOOK_INPUTTXT) | brutetok | sed $$'s/\t*$$//' | wordperline | sstat | sstat2tsv | grep -v $$'\t$$' > $(BOOK_FREQ)


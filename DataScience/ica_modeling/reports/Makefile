RM = rm -f
PDFLATEX = pdflatex
BIBTEX= bibtex
BIBER = biber

.SUFFIXES:	.pdf

all:       ica-based-source-extraction.pdf

ica-based-source-extraction.pdf: \
		ica-based-source-extraction.tex ica-based-source-extraction.bib macros.tex
	$(PDFLATEX) $*.tex
	$(BIBER) ica-based-source-extraction.bcf
	$(PDFLATEX) $*.tex
	$(PDFLATEX) $*.tex

clean:
	$(RM) *.aux *.log *.out *.run.xml
	$(RM) *.bbl *.bcf *.blg
	$(RM) *.pdf

RM = rm -f
PDFLATEX = pdflatex
BIBTEX= bibtex
BIBER = biber

.SUFFIXES:	.pdf

all:       single-sensor-ica-for-moving-sources.pdf

single-sensor-ica-for-moving-sources.pdf: \
		single-sensor-ica-for-moving-sources.tex \
		single-sensor-ica-for-moving-sources.bib \
		macros.tex
	$(PDFLATEX) $*.tex
	$(BIBER) single-sensor-ica-for-moving-sources.bcf
	$(PDFLATEX) $*.tex
	$(PDFLATEX) $*.tex

clean:
	$(RM) *.aux *.log *.out *.run.xml
	$(RM) *.bbl *.bcf *.blg
	$(RM) *.pdf

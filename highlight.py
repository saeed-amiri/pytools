"""
Highlight or delete highlights for the given word in the PDF.
"""


import os
import sys
import fitz  # PyMuPDF


def add_highlights(page, word, color):
    """Add highlights for the given word on the page."""
    counter = 0
    text_instances = page.search_for(word)
    for inst in text_instances:
        highlight = page.add_highlight_annot(inst)
        highlight.set_colors(stroke=color)
        highlight.update()
        counter += 1
    return counter


def delete_highlights(page, word):
    """Delete highlights for the given word on the page."""
    counter = 0
    text_instances = page.search_for(word)
    annots = page.annots()
    for inst in text_instances:
        for annot in annots:
            if annot.type[0] == 8:  # Highlight annotation type
                annot_rect = annot.rect
                if annot_rect.intersects(inst):
                    page.delete_annot(annot)
                    counter += 1
    return counter


def count_occurrences(page, word):
    """Count occurrences of the given word on the page."""
    text_instances = page.search_for(word)
    return len(text_instances)


def process_word_in_pdf(input_pdf: str,
                        word: str,
                        color: tuple[float, float, float],
                        delete_highlight: bool = False,
                        report_only: bool = False
                        ) -> None:
    """Highlight, delete highlights, or report occurrences for the
    given word in the PDF."""
    doc = fitz.open(input_pdf)
    total_counter = 0
    for page in doc:
        if report_only:
            total_counter += count_occurrences(page, word)
        elif delete_highlight:
            total_counter += delete_highlights(page, word)
        else:
            total_counter += add_highlights(page, word, color)

    if not report_only:
        temp_output_pdf = input_pdf + ".temp"
        doc.save(temp_output_pdf, incremental=False)
        os.replace(temp_output_pdf, input_pdf)

    action = ("reported" if report_only else
              "deleted highlights for" if delete_highlight else
              "highlighted")
    print(f"{action.capitalize()} {total_counter} instances of "
          f"'{word}' in {input_pdf}")


INPUT_FILE: str = sys.argv[1]
WORD_TO_PROCESS: str = sys.argv[2]
COLOR: tuple[float, float, float] = (1, 0, 0)  # Red color
if len(sys.argv) > 3 and sys.argv[3]:
    # "highlight", "delete_highlight", or "report"
    ACTION: str = sys.argv[3].lower()
else:
    ACTION = "highlight"

if ACTION == "delete_highlight":
    process_word_in_pdf(INPUT_FILE,
                        WORD_TO_PROCESS,
                        COLOR,
                        delete_highlight=True)
elif ACTION == "report":
    process_word_in_pdf(INPUT_FILE,
                        WORD_TO_PROCESS,
                        COLOR,
                        report_only=True)
else:
    process_word_in_pdf(INPUT_FILE,
                        WORD_TO_PROCESS,
                        COLOR)

import sys
import fitz  # PyMuPDF
import os

def process_word_in_pdf(input_pdf: str,
                        word: str,
                        color: tuple[float, float, float],
                        delete_highlight: bool = False
                        ):
    doc = fitz.open(input_pdf)
    counter = 0
    for page in doc:
        text_instances = page.search_for(word)
        for inst in text_instances:
            if delete_highlight:
                annots = page.annots()
                for annot in annots:
                    if annot.type[0] == 8:  # Highlight annotation type
                        annot_rect = annot.rect
                        if annot_rect.intersects(inst):
                            page.delete_annot(annot)
                            counter += 1
            else:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors(stroke=color)
                highlight.update()
                counter += 1
    temp_output_pdf = input_pdf + ".temp"
    doc.save(temp_output_pdf, incremental=False)
    os.replace(temp_output_pdf, input_pdf)

    action = "deleted highlights for" if delete_highlight else "highlighted"
    
    print(
        f"{action.capitalize()} {counter} instances of '{word}' in {input_pdf}"
        )

INPUT_FILE: str = sys.argv[1]
WORD_TO_PROCCESS: str = sys.argv[2]
ACTION: str = sys.argv[3].lower()  # "highlight" or "delete_highlight"
COLOR: tuple[float, float, float] = (1, 0, 0)  # Red color

if ACTION == "delete_highlight":
    process_word_in_pdf(INPUT_FILE,
                        WORD_TO_PROCCESS,
                        COLOR,
                        delete_highlight=True)
else:
    process_word_in_pdf(INPUT_FILE,
                        WORD_TO_PROCCESS,
                        COLOR)

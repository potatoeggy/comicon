import comicon


def test_cirtools() -> None:
    # comicon.create_cir("/home/eggy/kaguya.epub", "/home/eggy/kaguya-cir", "epub")
    # comicon.create_comic("/home/eggy/kaguya-cir", "/home/eggy/kaguya.pdf", "pdf")
    comicon.create_comic("/home/eggy/repos/mandown/City of Blank", "./City of Blank.cbz", "cbz")
    # comicon.create_cir("/home/eggy/kaguya.pdf", "/home/eggy/kaguya-cir", "pdf")
    # cirtools.validate_cir("/home/eggy/kaguya-cir")
    # comicon.convert("/home/eggy/kaguya-cir.epub", "/home/eggy/kaguya.cbz")

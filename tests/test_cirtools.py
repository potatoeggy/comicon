import comicon
from comicon import cirtools


def test_cirtools() -> None:
    # comicon.create_cir("/home/eggy/kaguya.epub", "/home/eggy/kaguya-cir", "epub")
    # comicon.create_comic("/home/eggy/kaguya-cir", "/home/eggy/kaguya.pdf", "pdf")
    comicon.create_cir("/home/eggy/kaguya.pdf", "/home/eggy/kaguya-cir", "pdf")
    cirtools.validate_cir("/home/eggy/kaguya-cir")

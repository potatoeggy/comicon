import comicon
from comicon import cirtools


def test_cirtools() -> None:
    # comicon.create_comic("/home/eggy/kaguya-cir", "/home/eggy/kaguya.epub", "epub")
    comicon.create_cir("/home/eggy/kaguya.epub", "/home/eggy/kaguya-cir", "epub")
    cirtools.validate_cir("/home/eggy/kaguya-cir")

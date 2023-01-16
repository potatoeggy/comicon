import comicon
from comicon import cirtools


def test_cirtools():
    comicon.create_comic(
        "/home/eggy/Kaguya-sama - Love Is War", "/home/eggy/kaguya.cbz", "cbz"
    )

    _ = comicon.create_cir("/home/eggy/kaguya.cbz", "/home/eggy/kaguya-cir", "cbz")
    cirtools.validate_cir("/home/eggy/kaguya-cir")

class InvalidCirError(RuntimeError):
    """Error for invalid CIR folders."""


class InvalidCirDataError(InvalidCirError):
    """Error for invalid CIR data."""


class NoChaptersError(InvalidCirError):
    """Error for no chapters in CIR."""


class EmptyChapterError(InvalidCirError):
    """Error for empty chapters in CIR."""


class NonImagesInChapterError(InvalidCirError):
    """Error for non-image files in chapter folders."""


class BadImageError(InvalidCirError):
    """Error for bad image files (e.g., wrong image format)."""


class UnusedChapterError(InvalidCirError):
    """Error for chapters declared in comicon.json but not found in the CIR folder."""

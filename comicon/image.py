ACCEPTED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".js2", ".png", ".gif"]
EXTENSION_MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".jp2": "image/jp2",
    ".png": "image/png",
    ".gif": "image/gif",
}

WITH_WEBP_ACCEPTED_IMAGE_EXTENSIONS = [*ACCEPTED_IMAGE_EXTENSIONS, ".webp"]
WITH_WEBP_EXTENSION_MIME_MAP = {
    **EXTENSION_MIME_MAP,
    ".webp": "image/webp",
}

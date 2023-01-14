from pathlib import Path


class BaseInput:
    def create_ir(self, path: Path | str) -> Path:
        raise NotImplementedError

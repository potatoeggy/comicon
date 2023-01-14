from pathlib import Path


class BaseOutput:
    def create_from_ir(self, path: Path | str) -> Path:
        """
        Create a comic of the given format from the IR folder path.
        """
        raise NotImplementedError

    # if ir metadata is improperly undefined, crash immediately

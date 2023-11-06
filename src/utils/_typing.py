from pathlib import Path
from typing import IO, Union

FilePath = Union[str, Path]
Buffer = IO
FilePathOrBuffer = Union[FilePath, Buffer]

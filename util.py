import io
import os

def chunks(file_to_read, chunk_size=io.DEFAULT_BUFFER_SIZE, *open_args, **open_kwargs):
    if isinstance(file_to_read, (str, bytes, os.PathLike)):
        file_to_read = open(file_to_read, *open_args, **open_kwargs)

    with file_to_read:
        # yield from each(lambda: file_to_read.read(chunk_size))
        for chunk in each(lambda: file_to_read.read(chunk_size)):
            yield chunk

def each(next):
    value = next()
    while value:
        yield value
        value = next()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

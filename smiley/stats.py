import base64
import marshal
import pstats
import tempfile


def stats_to_blob(stats):
    with tempfile.TemporaryFile(mode='r+') as f:
        marshal.dump(stats.stats, f)
        f.flush()
        f.seek(0)
        return f.read()


def blob_to_stats(data):
    # HACK: It really is too bad that pstats can't load data from a
    # string or StringIO.
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(base64.b64decode(data))
        f.flush()
        return pstats.Stats(f.name)

import marshal
import tempfile


def stats_to_blob(stats):
    with tempfile.TemporaryFile(mode='r+') as f:
        marshal.dump(stats.stats, f)
        f.flush()
        f.seek(0)
        return f.read()

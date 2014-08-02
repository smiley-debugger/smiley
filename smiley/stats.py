import base64
import marshal
import pstats
import tempfile

import six


def stats_to_blob(stats):
    marshalled = marshal.dumps(stats.stats)
    encoded = base64.b64encode(marshalled)
    return six.text_type(encoded, encoding='utf-8')


def blob_to_stats(data):
    # HACK: It really is too bad that pstats can't load data from a
    # string or StringIO.
    decoded = base64.b64decode(data)
    with tempfile.NamedTemporaryFile(mode='wb') as f:
        f.write(decoded)
        f.flush()
        return pstats.Stats(f.name)

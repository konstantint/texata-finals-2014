'''
Texata 2014 Finals Solution.
Some string hash functions.

Partially from:
http://stackoverflow.com/questions/2511058/persistent-hashing-of-strings-in-python
http://www.cse.yorku.ca/~oz/hash.html

Copyright: Konstantin Tretyakov
License: MIT
'''

from ctypes import c_ulong


def ulong(i):
    # XXX: ulong for some reason did not fit into SQLAlchemy's columns
    return c_ulong(i).value  # numpy would be better if available


def djb2(L):
    """
    h = 5381
    for c in L:
      h = ((h << 5) + h) + ord(c) # h * 33 + c
    return h
    """
    return reduce(lambda h, c: ord(c) + ((h << 5) + h), L, 5381)


def djb2_l(L):
    return reduce(lambda h, c: ulong(ord(c) + ((h << 5) + h)), L, 5381)


def sdbm(L):
    """
    h = 0
    for c in L:
      h = ord(c) + (h << 6) + (h << 16) - h
    return h
    """
    return reduce(lambda h, c: ord(c) + (h << 6) + (h << 16) - h, L, 0)


def sdbm_l(L):
    return reduce(lambda h, c: ulong(ord(c) + (h << 6) + (h << 16) - h), L, 0)

# This seems like the best option for basic string hashing
basic_string_hash = djb2_l


def rolling_word_hasher(seq, k):
    '''Given a sequence of *words*, yields a hash for each word subsequence of length k.
    That is, if len(seq) = m, yields (m-k+1) hashes. If len(seq) < k, yields nothing.

    Each hash is computed in a "rolling" (rabin-karp) fashion as:
         h_1 << (K-1) + h_2 << (K-2) + ... + h_(K-1) << 1 + h_K

    where each h_i is obtained as basic_string_hash(seq[i])

    >>> list(rolling_word_hasher(["a", "a", "a", "a"], 3))
    [1243690L, 1243690L]
    >>> list(rolling_word_hasher(["b", "a", "a", "a", "b", "a", "a", "a"], 3))
    [1243694L, 1243690L, 1243691L, 1243692L, 1243694L, 1243690L]

    '''
    if len(seq) < k:
        return
    h = map(basic_string_hash, seq)
    a = 0
    for i in range(k):
        a = ulong((a << 1) + h[i])
    yield a
    for i in range(k, len(seq)):
        toremove = ulong(h[i - k] << (k - 1))
        a = ulong(((a - toremove) << 1) + h[i])
        yield a


def winnowing_hasher(seq, k, w):
    '''
    Given a sequence, performs winnowing hashing with parameters k and w.
    Returns two sets - set of all fingerprints (obtained using rolling_word_hasher),
    and a set of "winnowing fingerprints".
    If seq is shorter than k, returns two empty lists.

    >>> winnowing_hasher(["a", "a", "a", "a"], 3, 3)
    (set([1243690L]), set([1243690L]))
    >>> assert winnowing_hasher(["b", "a", "a", "a", "b", "a", "a", "a"], 3, 3) == \
             (set([1243694L, 1243690L, 1243691L, 1243692L, 1243694L, 1243690L]), \
              set([1243690L, 1243691L]))

    '''

    if len(seq) < k:
        return ([], [])
    fps = list(rolling_word_hasher(seq, k))
    if len(fps) < w:
        wps = set([min(fps)])
    else:
        # TODO: This could be made theoretically faster with a pqueue,
        # but I have a feeling that with small w it is practically faster
        # this way. Didn't test.
        wps = set([min(fps[i:(i + w)]) for i in range(0, len(fps) - w + 1)])
    return (set(fps), wps)

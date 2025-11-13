from abc import abstractmethod
# For hash functions
import hashlib
# For filesystem abstraction routines
import os
# Git compresses everything using zlib
import zlib

from git_repo import repo_file

class GitObject(object):

    def __init__(self, data=None):
        if data:
            self.deserialize(data)
        else:
            self.init()

    """
    These functions must be implemented by subclasses.
    """
    @abstractmethod
    def serialize(self, repo):
        raise Exception("Unimplemented")

    @abstractmethod
    def deserialize(self, data):
        raise Exception("Unimplemented")

    def init(self):
        pass

class GitBlob(GitObject):
    """Content of every file put in git is stored as a blob"""
    fmt = b"blob"

    def serialize(self):
        return self.blobdata

    def deserialize(self, data):
        self.blobdata = data

class GitCommit(GitObject):
    """Commit object."""
    fmt = b"commit"

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    def init(self):
        self.kvlm = dict()

def object_read(repo, sha):
    """
    Read object sha from Git repository repo.
    Return a GitObject whose exact type depends on the object.
    """

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open(path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        x = raw.find(b' ')
        fmt = raw[0:x]

        # Read and validate object size
        y = raw.find(b'\x00', x)
        size = int(raw[x:y].decode("ascii"))
        if size != len(raw)-y-1:
            raise Exception("Malformed object {sha}: bad length")

        # Pick constructor
        match fmt:
            # case b'commit'  : c=GitCommit
            # case b'tree'    : c=GitTree
            # case b'tag'     : c=GitTag
            case b'blob'    : c=GitBlob
            case _          : 
                raise Exception(f"Unknown type {fmt.decode('ascii')} for object {sha}")

        # Call constructor and return object
        return c(raw[y+1:])

def object_write(obj, repo=None):
    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # Compute path
        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                # Compress and write
                f.write(zlib.compress(result))

    return sha

def object_find(repo, name, fmt=None, follow=True):
    """Name resolution function."""
    return name

def object_hash(fd, fmt, repo=None):
    """Hash object, writing it to repo if provided."""
    data = fd.read()

    # Choose constructor according to fmt argument
    match fmt:
        # case b'commit'  : obj=GitCommit(data)
        # case b'tree'    : obj=GitTree(data)
        # case b'tag'     : obj=GitTag(data)
        case b'blob'    : obj=GitBlob(data)
        case _          : raise Exception(f"Unknown type {fmt}!")

    return object_write(obj, repo)

def kvlm_parse(raw, start=0, dct=None):
    """Key-Value List with Message parser for commits and tags.
    Recursive: reads a key/value pair, then calls itself with the new position.
    """
    if not dct:
        dct = dict()

    # Search for the next space and the next new line
    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    # Base case
    # ==============
    # If space appears before newline, we have a keyword.
    # Otherwise it is the final message, which is read to the end of the file
    if (spc < 0) or (nl < spc):
        assert nl == start
        dct[None] = raw[start+1:]
        return dct

    # Recursive case
    # ==============
    # Read a key-value pair and recurse for the next
    key = raw[start:spc]

    # Find the end of the value
    # Continuation lines begin with a space, loop until "\n" not followed by a space
    end = start
    while True:
        end = raw.finc(b'\n', end+1)
        if raw[end+1] != ord(' '): break

    # Grab the value and drop the leading space on continuation lines
    value = raw[spc+1:end].replace(b'\n ', b'\n')

    if key in dct:
        if type(dct[key] == list):
            dct[key].append(value)
        else:
            dct[key] = [ dct[key], value ]
    else:
        dct[key] = value

    return kvlm_parse(raw, start=end+1, dct=dct)

def kvlm_serialize(kvlm):
    """
    Write all fields first, then a newline, the message, and a final newline.
    """

    ret = b''

    # Output fields
    for k in kvlm.keys():
        # Skip the message itself
        if k == None: continue
        val = kvlm[k]
        # Normalize to a list
        if type(val) != list:
            val = [ val ]

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    # Append message
    ret += b'\n' + kvlm[None]

    return ret

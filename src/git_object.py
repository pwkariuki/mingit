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

def object_read(repo, sha):
    """
    Read object sha from Git repository repo.
    Return a GitObject whose exact type depends on the object.
    """

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None
    
    with open(path, "rb") as f:
        raw = zlib.compress(f.read())

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
                raise Exception(f"Unknown type {fmt.decode("ascii")} for object {sha}")
        
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

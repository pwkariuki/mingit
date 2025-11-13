# For filesystem abstraction routines
import os
# To read configuration files
import configparser

class GitRepository (object):
    """A git repository"""

    worktree = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f'Not a git repository {path}')

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "reposirotyformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion: {vers}")

def repo_path(repo: GitRepository, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo: GitRepository, *path, mkdir=False):
    """
    Same as repo_path, but create dirname(*path) if absent.
    For example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will
        create .git/refs/remotes/origin.
    """

    if repo_dir(repo,  *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo: GitRepository, *path, mkdir=False):
    """Same as repo_path, but mkdir *path is absent if mkdir."""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None

def repo_default_config():
    ret = configparser.ConfigParser()

    ret.add_section("core")
    ret.set("core", "repositoryformatversion", "0") # gitdir format version
    ret.set("core", "filemode", "false") # disable tracking of file permissions
    ret.set("core", "bare", "false") # repository has a worktree

    return ret

def repo_create(path):
    """Create a new repository at path."""

    repo = GitRepository(path, True)

    # First ensure path either does not exist or is an empty dir.
    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"{path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"{path} is not empty!")
    else:
        os.makedirs(repo.worktree)

    assert repo_dir(repo, "branches", mkdir=True) # .git/branches/
    assert repo_dir(repo, "objects", mkdir=True) # .git/objects/
    assert repo_dir(repo, "refs", "tags", mkdir=True) # .git/refs/tags/
    assert repo_dir(repo, "refs", "heads", mkdir=True) # .git/refs/heads/

    # .git/description
    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository: edit this file 'description' to name the repository.\n")

    # .git/HEAD
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")

    # .git/config
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo

def repo_find(path=".", required=True):
    """Find the root of the current repository."""

    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".git")):
        return GitRepository(path)

    # If we have not returned, recurse on parent
    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        # Base case
        # os.path.join("/", "..") == "/"
        # If parent == path, then path is root.
        if required:
            raise Exception("Not git directory.")
        else:
            return None

    # Recursive case
    return repo_find(parent, required)

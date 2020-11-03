
import errno

try:
    import zlib
    del zlib
    _ZLIB_SUPPORTED = True
except ImportError:
    _ZLIB_SUPPORTED = False

try:
    import bz2
    del bz2
    _BZ2_SUPPORTED = True
except ImportError:
    _BZ2_SUPPORTED = False

try:
    import lzma
    del lzma
    _LZMA_SUPPORTED = True
except ImportError:
    _LZMA_SUPPORTED = False

try:
    from pwd import getpwnam
except ImportError:
    getpwnam = None

try:
    from grp import getgrnam
except ImportError:
    getgrnam = None

_WINDOWS = os.name == 'nt'
posix = nt = None
if os.name == 'posix':
    import posix
elif _WINDOWS:
    import nt

COPY_BUFSIZE = 1024 * 1024 if _WINDOWS else 64 * 1024
_USE_CP_SENDFILE = hasattr(os, "sendfile") and sys.platform.startswith("linux")
_HAS_FCOPYFILE = posix and hasattr(posix, "_fcopyfile")  # macOS
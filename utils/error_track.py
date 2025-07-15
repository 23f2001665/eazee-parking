import functools
import sys
import traceback

def with_error_location(func):
    """Decorator: print file‑name & line‑number whenever *func* raises."""
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:              # catch *everything* that isn’t a SystemExit/KeyboardInterrupt
            # Grab the most recent traceback frame that belongs to *func*
            tb_last = traceback.TracebackException.from_exception(exc).stack[-1]
            file_name = tb_last.filename
            line_no   = tb_last.lineno

            # Friendly message — swap `print` for `logging.error` if you prefer
            print(
                f"\n🚨  {func.__name__} crashed!\n"
                f"    File \"{file_name}\", line {line_no}\n"
                f"    → {exc.__class__.__name__}: {exc}"
            )

            # Re‑raise so normal exception flow (and debuggers/test suites) still work
            raise
    return _wrapper

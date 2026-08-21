from pathlib import Path
import importlib
import multiprocessing as mp
import sys
import traceback
import os

def is_empty_dir(path: str | Path) -> bool:
    path = Path(path)
    return path.is_dir() and not any(path.iterdir())

def _worker(conn, name, srcpath, outdir):
    outdir = Path(outdir).resolve()
    srcpath = Path(srcpath)
    filename = Path(outdir).joinpath(srcpath.stem+'.instr').resolve()
    assert not filename.exists(), f"file already found: {filename}"
    try:
        srcpath = Path(srcpath).resolve()
        package, parts = srcpath.parent, [srcpath.stem]
        assert (package / "__init__.py").is_file()
        parts.insert(0, package.name)
        package = package.parent
        assert not (package / "__init__.py").is_file(), "spurious __init__.py"
        assert len(parts)==2
        sys.path.insert(0, str(package))
        impname = ".".join(parts)
        print(f"Importing {impname}")
        mod = importlib.import_module(impname)
        print("   ... Calling .make()")
        instr = mod.make()
        if instr.name != filename.stem:
            raise ValueError(f'Instrument loaded from {srcpath} has '
                             f'unexpected name. Expected "{filename.stem}" '
                             f'but got "{instr.name}"')
        print("   ... Calling .write_full_instrument()")
        instr.write_full_instrument()
        ok = True
        for f in filename.parent.rglob('*'):
            if f.resolve() == filename:
                continue
            if is_empty_dir(f):
                print(f"   WARNING: Removing spurious empty directory {f.name}")
                f.rmdir()
            else:
                print(f"ERROR: Unexpected file generated: {f}")
                conn.send(("extrafiles", None))
                ok = False
        if not filename.exists():
            print(f"Did not find file:: {filename}")
            conn.send(("missingfile", None))
            ok = False
        if ok:
            conn.send(("ok", None))
    except BaseException:
        conn.send(("error", traceback.format_exc()))
    finally:
        conn.close()


def _genpy( name, srcpath, outdir, timeout = None):
    ctx = mp.get_context("spawn")
    parent, child = ctx.Pipe(duplex=False)
    process = ctx.Process(
        target=_worker,
        args=(child, str(name), str(srcpath), str(outdir) ),
    )
    process.start()
    child.close()
    try:
        if not parent.poll(timeout):
            process.terminate()
            process.join()
            raise TimeoutError(f"Process timed out for instrument: {srcpath}")
        try:
            status, message = parent.recv()
        except EOFError:
            status, message = "error", (
                f"Child exited without reporting success "
                f"(exit code {process.exitcode})"
            )
    finally:
        parent.close()
    process.join()
    if status != "ok":
        raise RuntimeError(message)

def P(p):
    return Path(p).resolve().absolute()

def _gen( name, srcpath, outdir):
    print(f"Copying {srcpath.name}")
    outdir.joinpath(srcpath.name).write_text( srcpath.read_text() )

def generate( info, outdir ):
    assert outdir.is_dir()
    genfct = _genpy if info['layout']=='instrpy' else _gen
    for k,v in info['setups'].items():
        d = outdir.joinpath(k)
        d.mkdir()
        os.chdir(d)
        genfct( k, P(v), d )

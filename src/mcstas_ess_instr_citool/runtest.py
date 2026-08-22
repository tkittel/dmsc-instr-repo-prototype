import subprocess
import shlex
import json

def runtest( info, outdir ):
    from .util import mcstas_info
    from .generate import generate
    do_mpi = False
    if do_mpi:
        from .util import get_nprocs
        nprocs = get_nprocs()
    mctest_cmd = mcstas_info()['cmd']['mctest']
    generate( info, outdir )
    testdir = outdir.joinpath('tests').absolute().resolve()
    cmd = ['--mpi', str(nprocs) ] if do_mpi else []
    cmd += [ '--local', str(outdir), '--testdir', str(testdir) ]
    #fixme: add --strict to cmd (and update minimum mcstas version in util.py):
    print(f"Launching: mctest {shlex.join(cmd)}")
    ec = subprocess.run( [ mctest_cmd ] + cmd,
                         check = False, capture_output = False )
    if not ec.returncode==0:
        raise RuntimeError('mctest command failed')
    json_files = list(testdir.glob('*/testresults_*.json'))
    if len(json_files)>1:
        raise RuntimeError('mctest command produced multiple testresults_*.json')
    if len(json_files) != 1:
        raise RuntimeError('mctest command produced no testresults_*.json')
    jsonfile = json_files[0]
    print(f"Loading json results from {jsonfile.name}")
    res = json.loads(jsonfile.read_text())
    #TODO: Use the json results for anything?
    return res

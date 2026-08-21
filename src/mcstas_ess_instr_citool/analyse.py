
from .enforce_layout import enforce_instr_layout
from pathlib import Path

def analyse_dir( project_dir ):
    info = enforce_instr_layout(project_dir)
    merged_modes = {'MAIN':info['main']['path']}
    merged_modes.update(dict(sorted( (m['mode'],m['path'])
                                     for m in info['modes'] )))
    info['setups'] = merged_modes
    if len(set(m.lower().strip() for m in merged_modes)) != len(merged_modes):
        raise ValueError('Clashing mode names detected')

    pypkgname = None
    if info['layout']=='instrpy':
        for k,v in merged_modes.items():
            ppn = Path(v).parent.name
            if pypkgname is None:
                pypkgname = ppn
            elif ppn != pypkgname:
                raise ValueError('Could not infer a consistent python pkg name')
    info['pypkgname'] = pypkgname
    return info

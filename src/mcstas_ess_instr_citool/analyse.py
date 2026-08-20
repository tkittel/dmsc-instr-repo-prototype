
from .enforce_layout import enforce_instr_layout
def analyse_dir( project_dir ):
    info = enforce_instr_layout(project_dir)
    return info

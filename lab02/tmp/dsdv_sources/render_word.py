"""Use Word's PDF as the conversion backend for the packaged PNG renderer.
The packaged runtime has no LibreOffice on Windows; Word export was generated
from the latest DOCX with ExportAsFixedFormat before this script is run.
"""
import importlib.util, os, tempfile
from pathlib import Path
base=Path.cwd()
tmp=base/'tmp'/'dsdv_sources'/'render_temp';tmp.mkdir(exist_ok=True)
tempfile.tempdir=str(tmp)
poppler=Path(r'C:\Users\ASUS\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin')
os.environ['PATH']=str(poppler)+os.pathsep+os.environ['PATH']
src=Path(r'C:\Users\ASUS\.codex\plugins\cache\openai-primary-runtime\documents\26.1020.11127\skills\documents\render_docx.py')
spec=importlib.util.spec_from_file_location('docx_renderer',src)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def from_word(*args,**kwargs):
    return str(base/'tmp'/'dsdv_sources'/'final_word.pdf'),'Word ExportAsFixedFormat backend'
mod.convert_to_pdf=from_word
images=mod.rasterize(str(base/'output'/'DSDV_on_tap'/'DSDV_On_tap_va_luyen_de.docx'),str(base/'tmp'/'dsdv_sources'/'final_render'),120,False,False)
print('Rendered latest Word output:',len(images),'pages')

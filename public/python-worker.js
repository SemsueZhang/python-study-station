/* The Python runtime is loaded only when a learner runs code. */
const runtimeURL = 'https://cdn.jsdelivr.net/pyodide/v0.29.3/full/';
let outputLength = 0;
function emitOutput(text, stream = 'stdout') {
  if (outputLength >= 50000) return;
  const remaining = 50000 - outputLength;
  const part = text.slice(0, remaining);
  outputLength += part.length;
  self.postMessage({type:'output', text:part, stream});
  if (outputLength >= 50000) self.postMessage({type:'output', text:'\n[输出已达到 50,000 字符上限]\n', stream:'stderr'});
}
self.onmessage = async ({data}) => {
  try {
    self.postMessage({type:'status', text:'正在加载 Python，首次使用需要下载运行环境…'});
    importScripts(runtimeURL + 'pyodide.js');
    const py = await loadPyodide({indexURL:runtimeURL});
    py.setStdout({batched: text=>emitOutput(text+'\n')});
    py.setStderr({batched: text=>emitOutput(text+'\n','stderr')});
    const lines = data.input === '' ? [] : data.input.replace(/\r\n/g,'\n').split('\n');
    let inputIndex = 0;
    py.setStdin({stdin:()=>inputIndex < lines.length ? lines[inputIndex++] : null});
    self.postMessage({type:'status',text:'正在准备本次示例…'});
    if (data.packages?.length) await py.loadPackage(data.packages);
    await py.loadPackagesFromImports(data.code);
    py.FS.mkdirTree('/study');
    py.FS.chdir('/study');
    for(const [name, content] of Object.entries(data.files || {})) py.FS.writeFile('/study/'+name,content);
    await py.runPythonAsync('import sys\nif "/study" not in sys.path: sys.path.insert(0, "/study")');
    const namespace = py.runPython('dict(__name__="__main__")');
    py.globals.set('_study_namespace', namespace);
    py.globals.set('_study_source', data.code);
    py.globals.set('_study_plot', src => self.postMessage({type:'image',src}));
    if(data.packages?.includes('matplotlib') || /(?:import matplotlib|from matplotlib)/.test(data.code)) {
      await py.runPythonAsync(`import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import io, base64

def _study_show(*args, **kwargs):
    for number in plt.get_fignums():
        buffer = io.BytesIO()
        plt.figure(number).savefig(buffer, format='png', dpi=120, bbox_inches='tight')
        _study_plot('data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode())
    plt.close('all')
plt.show = _study_show`);
    }
    self.postMessage({type:'running'});
    await py.runPythonAsync('exec(compile(_study_source, "学习代码.py", "exec"), _study_namespace)');
    if(py.globals.has('_study_show')) await py.runPythonAsync('_study_show()');
    namespace.destroy();
    self.postMessage({type:'done'});
  } catch(error) {
    self.postMessage({type:'error',text:String(error)});
  }
};

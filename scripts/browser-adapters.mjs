export const mockAI = `"""离线教学客户端。所有响应为预置文字，不发送网络请求。"""
from types import SimpleNamespace

class OpenAI:
    def __init__(self, **kwargs):
        self.models = SimpleNamespace(list=self.list_models)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
    def list_models(self):
        print("[模拟接口] models.list()")
        return SimpleNamespace(data=[SimpleNamespace(id="Qwen/Qwen2.5-7B-Instruct")])
    def create(self, *, model, messages, max_tokens):
        print("[模拟接口] chat.completions.create()", "model=", model, "max_tokens=", max_tokens)
        text = messages[-1]["content"]
        answer = ("[模拟响应] def square(x): return x * x\\n调用 square(3) 得到 9。"
                  if "example" in text.lower() else
                  "[模拟响应] 函数封装一组步骤。参数接收输入。return 将结果交回调用者。")
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=answer))])
    def close(self):
        print("[模拟接口] 客户端已关闭")
`;
export const sampleMarket = `"""固定的合成教学数据，不查询真实市场。"""
import pandas as pd

def set_token(token):
    pass

def pro_api():
    return SampleMarket()

class SampleMarket:
    def index_weight(self, **kwargs):
        print("[内置示例数据] 合成成分股 DEMO_A / DEMO_B / DEMO_C")
        return pd.DataFrame({"con_code": ["DEMO_A", "DEMO_B", "DEMO_C"],
                             "weight": [40.0, 35.0, 25.0],
                             "trade_date": ["20240105"] * 3})

def pro_bar(*, ts_code, adj, start_date, end_date):
    print("[内置示例数据]", ts_code, "固定价格序列，非真实行情")
    factor = {"DEMO_A": 1.0, "DEMO_B": 0.8, "DEMO_C": 1.2}.get(ts_code, 1.0)
    data = pd.DataFrame({"trade_date": ["20240102", "20240103", "20240104", "20240105", "20240108", "20240109"],
                         "close": [x * factor for x in [100, 103, 101, 106, 108, 105]]})
    return data.loc[(data.trade_date >= start_date) & (data.trade_date <= end_date)].copy()
`;
export function adaptedExample(index,codes){
 if(index>=10&&index<=14){
  const module=codes.slice(10,14).join('\n\n').replace('from openai import OpenAI','from mock_openai import OpenAI');
  const setup='import os\nos.environ["SILICONFLOW_API_KEY"] = "OFFLINE_DEMO_ONLY"\n';
  let code;
  if(index===14)code=setup+'\n'+codes[14];
  else {
   code=setup+'\n'+codes.slice(10,index+1).join('\n\n').replace('from openai import OpenAI','from mock_openai import OpenAI');
   code+='\n\n# 调用本段功能，观察参数与返回值\n'+[
    'print("[模拟配置]", MODEL_GROUPS)',
    'set_api_key()\nprint(_check_text("  Python  ", "question"))\nclient = _get_client()\nclient.close()',
    'print(get_models(task="chat"))',
    'print(call_silicon("解释 Python 函数"))'
   ][index-10];
  }
  return {code,files:{'mock_openai.py':mockAI,'Call_AI.py':module},packages:[],note:'离线模拟：保留原接口的参数检查、消息组织和客户端管理逻辑。mock_openai.py 返回预置响应，不连接 AI 服务。编辑器展示本次实际执行的代码，文件区展示补齐的模块。'};
 }
 if(index>=15&&index<=19){
  const module=codes.slice(15,19).join('\n\n').replace('import tushare as ts','import sample_market as ts');
  const setup='import os\nos.environ["TUSHARE_TOKEN"] = "OFFLINE_DEMO_ONLY"\n';
  let code;
  if(index===19)code=setup+'\n'+codes[19];
  else {
   code=setup+'\n'+codes.slice(15,index+1).join('\n\n').replace('import tushare as ts','import sample_market as ts');
   code+='\n\n# 使用固定教学数据调用本段功能\n'+[
    'components = get_index_components("DEMO_INDEX")\nprint(random_sample_stocks(components, 2, 42))',
    'prices = get_stock_adj_close("DEMO_A", "20240101", "20241231")\nprint(calc_daily_return(prices))',
    'print(batch_download_and_calc_return(["DEMO_A"], "20240101", "20241231", 0))',
    'results = batch_download_and_calc_return(["DEMO_A"], "20240101", "20241231", 0)\nplot_price_return_subplot(results)'
   ][index-15];
  }
  return {code,files:{'sample_market.py':sampleMarket,'stock_analysis.py':module},packages:['pandas','matplotlib'],note:'内置合成行情：sample_market.py 提供固定示例数据，替代真实行情接口。原函数在 Pyodide 中实际执行抽样、日期排序、收益率计算和绘图。数据与模块代码可在文件区查看。'};
 }
 return null;
}

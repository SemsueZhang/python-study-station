"""Validate static questions without regenerating or changing their answers."""
import ast
from collections import Counter
import contextlib
import io
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
course = json.loads((root / 'src/data/course.json').read_text())
bank = json.loads((root / 'src/data/question-bank.json').read_text())['questions']
old = [q for c in course['chapters'] for q in c['questions']]
chapters = {c['id']: c for c in course['chapters']}
assert len(bank) == 500
assert Counter(q['chapter'] for q in bank) == {1:50,2:65,3:85,4:90,5:90,6:65,7:55}
assert Counter(q['answer'] for q in bank) == dict.fromkeys('ABCD', 125)
normalize = lambda s: re.sub(r'\s+', '', s).replace('`', '').replace('，', ',').replace('？', '?')
ids = {q['id'] for q in old}
prompts = {normalize(q['prompt']) for q in old}
def signature(code):
    return ast.dump(ast.parse(code), include_attributes=False)
old_code = {signature(code) for q in old for code in re.findall(r'```python\n(.*?)\n```', q['prompt'], re.S)}
checked = 0
new_code = set()
for i, q in enumerate(bank):
    assert q['id'] == f'bank-{i+1:03}' and q['number'] == i+1
    assert q['id'] not in ids and normalize(q['prompt']) not in prompts, q['id']
    ids.add(q['id']); prompts.add(normalize(q['prompt']))
    assert q['pool'] == 'expansion' and q['context'] is None
    assert q['sourceSection'] in [s['id'] for s in chapters[q['chapter']]['sections']]
    assert q['explanation'].strip() and '；' not in q['explanation']
    assert [o['label'] for o in q['options']] == list('ABCD')
    assert len(set(o['markdown'] for o in q['options'])) == 4
    assert all(o['markdown'].strip() for o in q['options'])
    v = q['verification']
    if not v: continue
    sig = signature(v['code'])
    assert sig not in old_code and sig not in new_code, q['id'] + ': duplicate executable code'
    new_code.add(sig)
    stdout = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout):
            if v['kind'] == 'expression':
                actual = repr(eval(v['code'], {}))
            else:
                exec(v['code'], {})
                actual = stdout.getvalue().rstrip('\n')
    except Exception as error:
        actual = '!' + type(error).__name__
    assert actual == v['expected'], (q['id'], actual, v['expected'])
    if actual.startswith('!'):
        expected_option = f'`{actual[1:]}` 异常'
    elif v['kind'] == 'expression':
        expected_option = f'`{actual}`'
    else:
        expected_option = f'```text\n{actual}\n```' if actual else '（无输出）'
    assert next(o['markdown'] for o in q['options'] if o['label'] == q['answer']) == expected_option
    checked += 1
report = dict(totalNew=len(bank), original=len(old), chapters=dict(Counter(q['chapter'] for q in bank)),
              executableChecked=checked, conceptualQuestions=len(bank)-checked,
              duplicatePrompts=0, duplicateExecutableCode=0,
              answers=dict(Counter(q['answer'] for q in bank)), status='passed')
print(json.dumps(report, ensure_ascii=False, indent=2))
(root / 'qa/question-bank-validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

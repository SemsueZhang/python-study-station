import {useEffect, useRef, useState} from 'react';
import {ArrowRight, Bookmark, Check, ChevronLeft, ChevronRight, Clock3, Shuffle} from 'lucide-react';
import type {Question} from '../types';
import {createExam, EXAM_SIZE, EXAM_STORAGE_KEY, gradeExam, parseExam} from '../examState';
import type {ExamSession} from '../examState';
import {Markdown} from './Markdown';

export function Exam({bank, record}: {bank: Question[]; record: (session: ExamSession) => void}) {
  const [session, setSession] = useState<ExamSession | null>(() => {
    try { return parseExam(localStorage.getItem(EXAM_STORAGE_KEY), bank); } catch { return null; }
  });
  const [storageError, setStorageError] = useState(false);
  const [confirm, setConfirm] = useState<'submit' | 'restart' | null>(null);
  const [now, setNow] = useState(Date.now);
  const [review, setReview] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (!session) return;
    try { localStorage.setItem(EXAM_STORAGE_KEY, JSON.stringify(session)); setStorageError(false); }
    catch { setStorageError(true); }
  }, [session]);
  useEffect(() => {
    if (session?.submittedAt) record(session);
  }, [session?.id, session?.submittedAt]);
  useEffect(() => {
    if (!session || session.submittedAt) return;
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [session?.id, session?.submittedAt]);
  useEffect(() => { if (confirm) heading.current?.focus(); }, [confirm]);
  function start() { setSession(createExam(bank)); setNow(Date.now()); setConfirm(null); setReview(false); }
  const result = session ? gradeExam(session, bank) : null;
  const items = result?.items || [], q = session ? items[session.index] : null;
  const submitted = !!session?.submittedAt;
  const navigation = items.map((q, i) => ({q, i})).filter(({q}) => !submitted || !review || session!.answers[q.id] !== q.answer).map(({i}) => i);
  const previous = [...navigation].reverse().find(i => i < (session?.index || 0));
  const next = navigation.find(i => i > (session?.index || 0));
  const elapsed = session ? Math.max(0, Math.floor(((session.submittedAt || now) - session.startedAt) / 1000)) : 0;
  const time = `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, '0')}`;
  function go(index: number) { setSession(s => s && ({...s, index})); setConfirm(null); }
  return <section className="practice exam">
    <div className="eyebrow">CHECK WHAT YOU HAVE LEARNED</div>
    <h1>50 道题，检验七章所学。</h1>
    <p className="page-lead">从新增的 {bank.length} 题中随机抽取 {EXAM_SIZE} 道单选题，本场不重复。每题 2 分，满分 100 分。不限时，交卷后统一评分。</p>
    {storageError && <p className="notice" role="alert">本次考试暂时无法保存到浏览器。请保持页面打开，避免刷新丢失作答。</p>}
    {!session ? <div className="exam-intro question-card"><h2>准备好就开始</h2><ul><li>可以前后切题、修改选项，或标记稍后检查。</li><li>交卷前不显示答案与解析。</li><li>题序、选项和用时自动保存在当前浏览器，刷新或下次打开可继续；用时包含离开页面的时间。</li><li>交卷后可查看各章成绩，错题会进入错题本。</li></ul><button className="button primary" onClick={start}>开始考试<ArrowRight size={17}/></button><a className="button" href="#/practice/bank">先练习新题库</a></div> : <>
      <div className="quiz-summary exam-summary"><span><Clock3 size={16}/> {submitted ? '考试用时' : '已用时'} {time}</span><span>已作答 {result!.answered} / {EXAM_SIZE} 题</span><span>待检查 {session.flagged.length} 题</span><button className="button small" onClick={() => setConfirm('restart')}><Shuffle size={14}/>重新抽卷</button></div>
      {confirm && <div className="exam-confirm" role="region" aria-labelledby="exam-confirm-title"><h2 id="exam-confirm-title" ref={heading} tabIndex={-1}>{confirm === 'submit' ? '确认提交本场考试' : '重新抽取一套试卷'}</h2><p>{confirm === 'submit' ? `已作答 ${result!.answered} 题，还有 ${result!.unanswered} 题未答。未答题计 0 分，提交后本场答案锁定。` : '重新抽卷将替换当前试卷及作答，开始新一场考试。已经计入学习记录的结果会保留。'}</p><div className="exam-actions"><button className="button primary" onClick={() => {
        if (confirm === 'restart') { start(); return; }
        setSession(s => s && ({...s, submittedAt: Date.now()})); setConfirm(null); setReview(false);
      }}>{confirm === 'submit' ? '确认交卷' : '确认重新抽卷'}</button><button className="button" onClick={() => setConfirm(null)}>取消，返回试卷</button></div></div>}
      {submitted && <div className="exam-result question-card" role="status"><div><span className="eyebrow">本场成绩</span><h2><strong>{result!.score}</strong> / 100 分</h2><p>答对 {result!.correct} 题 · 答错 {result!.answered - result!.correct} 题 · 未答 {result!.unanswered} 题</p></div><div className="exam-chapters">{[1,2,3,4,5,6,7].map(ch => {
        const group = items.filter(q => q.chapter === ch), right = group.filter(q => session.answers[q.id] === q.answer).length;
        return <span key={ch}>第 {ch} 章 <b>{group.length ? `${right} / ${group.length}` : '本场未抽到'}</b></span>;
      })}</div><div className="exam-actions"><button className="button" onClick={() => { setReview(false); go(0); }}>逐题查看解析</button><button className={`button ${review ? 'primary' : ''}`} disabled={result!.correct === EXAM_SIZE} onClick={() => { setReview(true); const i = items.findIndex(q => session.answers[q.id] !== q.answer); if(i >= 0) go(i); }}>只看错题与未答题</button><a className="button" href="#/practice/wrong">去错题本重练</a></div></div>}
      <p className="exam-legend">{submitted ? '绿色：答对 · 橙色：答错或未答' : '紫色：已作答 · 小圆点：待检查'} · 点击题号可跳转</p>
      <div className="question-dots exam-dots" aria-label="考试题目导航">{items.map((item, i) => (!submitted || !review || session.answers[item.id] !== item.answer) && <button key={item.id} aria-current={session.index === i ? 'step' : undefined} aria-label={`第 ${i+1} 题，${submitted ? (session.answers[item.id] === item.answer ? '答对' : '答错或未答') : (session.answers[item.id] ? '已作答' : '未作答')}${session.flagged.includes(item.id) ? '，待检查' : ''}`} className={`${session.index === i ? 'current' : ''} ${submitted ? (session.answers[item.id] === item.answer ? 'correct' : 'incorrect') : (session.answers[item.id] ? 'answered' : '')} ${session.flagged.includes(item.id) ? 'flagged' : ''}`} onClick={() => go(i)}>{i+1}</button>)}</div>
      {q && <div className="question-card" key={q.id}><div className="question-caption"><span className="pill purple">第 {q.chapter} 章 · 新增第 {q.number} 题</span><span>{session.index + 1} / {EXAM_SIZE}</span></div><Markdown text={q.prompt}/><fieldset className="options" disabled={submitted}><legend className="sr-only">选择答案</legend>{q.options.map(o => <label className={`option ${session.answers[q.id] === o.label ? 'chosen' : ''} ${submitted && o.label === q.answer ? 'right' : ''} ${submitted && session.answers[q.id] === o.label && o.label !== q.answer ? 'wrong' : ''}`} key={o.label}><input type="radio" name={q.id} value={o.label} checked={session.answers[q.id] === o.label} onChange={() => setSession(s => s && ({...s, answers: {...s.answers, [q.id]: o.label}}))}/><b>{o.label}</b><Markdown text={o.markdown}/></label>)}</fieldset>
        {!submitted ? <div className="exam-actions"><button className="button" aria-pressed={session.flagged.includes(q.id)} onClick={() => setSession(s => s && ({...s, flagged: s.flagged.includes(q.id) ? s.flagged.filter(id => id !== q.id) : [...s.flagged, q.id]}))}><Bookmark size={16}/>{session.flagged.includes(q.id) ? '取消待检查' : '标记待检查'}</button><button className="button" disabled={!session.answers[q.id]} onClick={() => setSession(s => { if (!s) return s; const answers = {...s.answers}; delete answers[q.id]; return {...s, answers}; })}>清除本题选择</button><span className="subtle">选择即保存，交卷后判分</span></div> : <div className={`answer-explanation ${session.answers[q.id] === q.answer ? 'success' : 'retry'}`}><div className="answer-feedback"><h2>{session.answers[q.id] === q.answer ? '答对了' : session.answers[q.id] ? '本题答错' : '本题未作答'}</h2><p>你的答案 {session.answers[q.id] || '未作答'} · 正确答案 {q.answer}</p></div><details className="answer-details"><summary>答案解析</summary><Markdown text={q.explanation}/><a href={`#/chapter/${q.chapter}/${q.sourceSection || 'intro'}`}>回顾对应知识点 →</a></details></div>}
      </div>}
      <div className="page-turn"><button className="button" disabled={previous === undefined} onClick={() => previous !== undefined && go(previous)}><ChevronLeft size={16}/>上一题</button><button className="button" disabled={next === undefined} onClick={() => next !== undefined && go(next)}>下一题<ChevronRight size={16}/></button></div>
      {!submitted && <div className="exam-submit"><p>未答 {result!.unanswered} 题 · 已标记 {session.flagged.length} 题</p><button className="button primary" onClick={() => setConfirm('submit')}><Check size={17}/>提交试卷</button></div>}
    </>}
  </section>;
}

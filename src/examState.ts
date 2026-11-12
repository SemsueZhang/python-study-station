import type {Question} from './types';

export const EXAM_SIZE = 50;
export const EXAM_STORAGE_KEY = 'python-study-exam-v1';
export type ExamSession = {
  version: 1;
  id: string;
  questionIds: string[];
  answers: Record<string, string>;
  flagged: string[];
  index: number;
  startedAt: number;
  submittedAt: number | null;
};

export function drawQuestions(bank: Question[], count = EXAM_SIZE): string[] {
  if (new Set(bank.map(q => q.id)).size !== bank.length || bank.length < count) {
    throw new Error('题库不足或存在重复题号');
  }
  const ids = bank.map(q => q.id);
  for (let i = ids.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [ids[i], ids[j]] = [ids[j], ids[i]];
  }
  return ids.slice(0, count);
}

export function createExam(bank: Question[]): ExamSession {
  return {version: 1, id: crypto.randomUUID(), questionIds: drawQuestions(bank),
    answers: {}, flagged: [], index: 0, startedAt: Date.now(), submittedAt: null};
}

export function parseExam(raw: string | null, bank: Question[]): ExamSession | null {
  try {
    const s = JSON.parse(raw || 'null');
    const ids = new Set(bank.map(q => q.id));
    if (s?.version !== 1 || typeof s.id !== 'string' || !Array.isArray(s.questionIds)
      || s.questionIds.length !== EXAM_SIZE || new Set(s.questionIds).size !== EXAM_SIZE
      || !s.questionIds.every((id: unknown) => typeof id === 'string' && ids.has(id))
      || !s.answers || typeof s.answers !== 'object' || Array.isArray(s.answers)
      || !Object.entries(s.answers).every(([id, a]) => s.questionIds.includes(id) && typeof a === 'string' && /^[A-D]$/.test(a))
      || !Array.isArray(s.flagged) || !s.flagged.every((id: unknown) => s.questionIds.includes(id))
      || !Number.isInteger(s.index) || s.index < 0 || s.index >= EXAM_SIZE
      || !Number.isFinite(s.startedAt) || s.startedAt <= 0
      || !(s.submittedAt === null || (Number.isFinite(s.submittedAt) && s.submittedAt >= s.startedAt))) return null;
    return s as ExamSession;
  } catch { return null; }
}

export function gradeExam(session: ExamSession, bank: Question[]) {
  const map = new Map(bank.map(q => [q.id, q]));
  const items = session.questionIds.map(id => map.get(id)!);
  const correct = items.filter(q => session.answers[q.id] === q.answer).length;
  const answered = Object.keys(session.answers).length;
  return {items, correct, answered, unanswered: items.length - answered, score: correct * 2};
}

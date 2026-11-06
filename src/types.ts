export type Option = { label: string; markdown: string };
export type Question = { id: string; chapter: number; number: number; prompt: string; options: Option[]; answer: string; explanation: string; context: { number: number; prompt: string } | null };
export type Section = { id: string; title: string; markdown: string };
export type Chapter = { id: number; title: string; description: string; color: string; source: string; sections: Section[]; questions: Question[] };
export type Example = { id: string; chapter: number; section: string; title: string; original: string; code: string; input: string; files: Record<string,string>; expectedError: string; packages: string[]; note: string };
export type Progress = { version: 1; positions?: Record<string, number>; completed: string[]; lastRead: {chapter: number; section: string} | null; answers: Record<string, {selected: string; correct: boolean; attempts: number; correctAttempts: number}> };

import type { Chapter, Example, Section } from './types';

export type StudyTime = { min: number; max: number };

// Planning estimates for a first pass, not observed learner timings.
// Reading: 220–350 Chinese characters / English words per minute.
// Examples: allow time to read, run and change the code. Exercises: 2–4 min each.
export function estimateSection(section: Section, examples: Example[]): StudyTime {
  const prose = section.markdown.replace(/```[\s\S]*?```/g, '');
  const units = (prose.match(/\p{Script=Han}|[A-Za-z]+|\d+/gu) || []).length;
  const practice = examples.reduce((time, example) => {
    const lines = (example.original || example.code).split('\n').filter(line => line.trim()).length;
    return { min: time.min + 1 + lines / 18, max: time.max + 2 + lines / 10 };
  }, { min: 0, max: 0 });
  return {
    min: Math.max(2, Math.ceil(units / 350 + practice.min)),
    max: Math.max(3, Math.ceil(units / 220 + practice.max)),
  };
}

export function estimateChapter(chapter: Chapter, examples: Example[]): StudyTime {
  const time = chapter.sections.reduce((time, section) => {
    const part = estimateSection(section, examples.filter(e => e.chapter === chapter.id && e.section === section.id));
    return { min: time.min + part.min, max: time.max + part.max };
  }, { min: chapter.questions.length * 2, max: chapter.questions.length * 4 });
  // Keep chapter cards and the course total on the same half-hour scale.
  return { min: Math.floor(time.min / 30) * 30, max: Math.ceil(time.max / 30) * 30 };
}

export function formatStudyTime(time: StudyTime, unit: 'minutes' | 'hours' = 'hours'): string {
  const minutes = Math.round((time.min + time.max) / 2);
  if (unit === 'minutes') return `${minutes} 分钟`;
  const hours = Math.floor(minutes / 60);
  const remainder = minutes % 60;
  return remainder ? `${hours} 小时 ${remainder} 分钟` : `${hours} 小时`;
}

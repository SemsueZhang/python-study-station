import type { Root, RootContent, Blockquote, Paragraph } from 'mdast';

// Recognize only the notes' details/summary container. Other raw HTML stays inert.
// Keeping the body as Markdown nodes preserves links, lists, math, and code runners.
export function remarkTermCards() {
  return (tree: Root) => {
    const visit = (parent: { children: RootContent[] }) => {
      const nodes = parent.children;
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        if (node.type === 'html') {
          const opening = /^<details>\s*<summary>([^<>]+)<\/summary>\s*$/.exec(node.value);
          if (opening) {
            let depth = 1;
            let end = i + 1;
            for (; end < nodes.length; end++) {
              const candidate = nodes[end];
              if (candidate.type !== 'html') continue;
              if (/^<details>/.test(candidate.value)) depth++;
              if (/^<\/details>\s*$/.test(candidate.value) && --depth === 0) break;
            }
            if (end < nodes.length) {
              const summary: Paragraph = {
                type: 'paragraph',
                data: { hName: 'summary' },
                children: [{ type: 'text', value: opening[1].trim() }],
              };
              const card: Blockquote = {
                type: 'blockquote',
                data: { hName: 'details', hProperties: { className: ['term-card'] } },
                children: [summary, ...nodes.slice(i + 1, end)] as Blockquote['children'],
              };
              nodes.splice(i, end - i + 1, card);
            }
          }
        }
        const current = nodes[i];
        if ('children' in current) visit(current as { children: RootContent[] });
      }
    };
    visit(tree);
  };
}

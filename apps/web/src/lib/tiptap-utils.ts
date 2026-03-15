const BLOCK_TYPES = new Set(['paragraph', 'heading', 'blockquote', 'listItem', 'codeBlock']);

/** Extract plain text from TipTap JSON */
export function tiptapToPlainText(doc: Record<string, unknown>): string {
  const parts: string[] = [];
  function walk(node: unknown, isBlock = false) {
    if (node && typeof node === 'object') {
      const n = node as Record<string, unknown>;
      const block = BLOCK_TYPES.has((n.type as string) || '');
      if (block && parts.length > 0 && !parts[parts.length - 1]?.endsWith('\n')) parts.push('\n');
      if (n.type === 'hardBreak') parts.push('\n');
      if ('text' in n && typeof n.text === 'string') parts.push(n.text);
      if (Array.isArray(n.content)) n.content.forEach((c) => walk(c, block));
    }
  }
  const content = (doc as { content?: unknown[] }).content;
  if (Array.isArray(content)) content.forEach((c) => walk(c));
  return parts.join('').replace(/\n{3,}/g, '\n\n').trim();
}

/** Replace text in TipTap JSON recursively */
export function replaceInTiptapJson(
  node: Record<string, unknown>,
  find: string,
  replace: string,
  caseSensitive = false
): Record<string, unknown> {
  if (!find) return node;

  const flags = caseSensitive ? 'g' : 'gi';
  const regex = new RegExp(find.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), flags);

  if (node.type === 'text' && typeof node.text === 'string') {
    return { ...node, text: node.text.replace(regex, replace) };
  }

  if (Array.isArray(node.content)) {
    return {
      ...node,
      content: node.content.map((child) =>
        replaceInTiptapJson(child as Record<string, unknown>, find, replace, caseSensitive)
      ),
    };
  }

  return node;
}

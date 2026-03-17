/**
 * TipTap JSON ↔ plain text conversion for mobile editor.
 * Matches API export service format.
 */

export function plainTextToTiptap(text: string): Record<string, unknown> {
  if (!text || !text.trim()) {
    return { type: "doc", content: [{ type: "paragraph" }] };
  }
  const blocks: Record<string, unknown>[] = [];
  for (const para of text.split("\n\n")) {
    const p = para.trim();
    if (!p) continue;
    const lines = p.split("\n");
    const content: Record<string, unknown>[] = [];
    for (let i = 0; i < lines.length; i++) {
      if (i > 0) content.push({ type: "hardBreak" });
      content.push({ type: "text", text: lines[i] });
    }
    blocks.push({ type: "paragraph", content });
  }
  if (blocks.length === 0) {
    return { type: "doc", content: [{ type: "paragraph" }] };
  }
  return { type: "doc", content: blocks };
}

export function tiptapToPlainText(content: Record<string, unknown> | null): string {
  if (!content || typeof content !== "object") return "";
  const parts: string[] = [];

  function extractParagraph(node: unknown): string {
    const buf: string[] = [];
    function walk(n: unknown): void {
      if (n && typeof n === "object" && "text" in n) {
        buf.push(String((n as { text?: string }).text ?? ""));
      } else if (n && typeof n === "object" && "content" in n) {
        const arr = (n as { content?: unknown[] }).content;
        if (Array.isArray(arr)) {
          for (const c of arr) {
            if (c && typeof c === "object" && (c as { type?: string }).type === "hardBreak") {
              buf.push("\n");
            } else {
              walk(c);
            }
          }
        }
      }
    }
    walk(node);
    return buf.join("");
  }

  const c = (content as { content?: unknown[] }).content;
  if (Array.isArray(c)) {
    for (let i = 0; i < c.length; i++) {
      const node = c[i];
      if (node && typeof node === "object" && (node as { type?: string }).type === "paragraph") {
        parts.push(extractParagraph(node));
      }
    }
  }
  return parts.join("\n\n").replace(/\n\n\n+/g, "\n\n").trim();
}

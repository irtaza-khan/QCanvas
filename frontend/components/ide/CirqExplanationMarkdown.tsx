"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

const mdComponents = {
  h1: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h1
      className="text-base font-semibold text-white mt-4 mb-2 first:mt-0"
      {...props}
    />
  ),
  h2: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h2 className="text-sm font-semibold text-quantum-blue-light mt-3 mb-1.5" {...props} />
  ),
  h3: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className="text-sm font-medium text-editor-text mt-2 mb-1" {...props} />
  ),
  p: (props: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className="text-editor-text/90 leading-relaxed mb-2 last:mb-0" {...props} />
  ),
  ul: (props: React.HTMLAttributes<HTMLUListElement>) => (
    <ul className="list-disc pl-4 mb-2 space-y-1 text-editor-text/90" {...props} />
  ),
  ol: (props: React.HTMLAttributes<HTMLOListElement>) => (
    <ol className="list-decimal pl-4 mb-2 space-y-1 text-editor-text/90" {...props} />
  ),
  li: (props: React.HTMLAttributes<HTMLLIElement>) => (
    <li className="leading-relaxed" {...props} />
  ),
  code: ({
    inline,
    ...props
  }: React.HTMLAttributes<HTMLElement> & { inline?: boolean }) =>
    inline ? (
      <code
        className="px-1 py-0.5 rounded bg-editor-border text-quantum-blue-light text-xs font-mono"
        {...props}
      />
    ) : (
      <code
        className="block p-2 rounded bg-editor-bg border border-editor-border text-xs font-mono overflow-x-auto my-2"
        {...props}
      />
    ),
  pre: (props: React.HTMLAttributes<HTMLPreElement>) => (
    <pre className="overflow-x-auto my-2" {...props} />
  ),
  a: (props: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a
      className="text-quantum-blue-light underline hover:text-white"
      target="_blank"
      rel="noopener noreferrer"
      {...props}
    />
  ),
  blockquote: (props: React.HTMLAttributes<HTMLQuoteElement>) => (
    <blockquote
      className="border-l-2 border-quantum-blue-light/50 pl-3 my-2 text-editor-text/80 italic"
      {...props}
    />
  ),
};

export default function CirqExplanationMarkdown({
  markdown,
  useMath = true,
}: {
  markdown: string;
  /** Enable KaTeX when explanations may include LaTeX (e.g. very_high depth). */
  useMath?: boolean;
}) {
  return (
    <div className="cirq-explanation-markdown text-sm [&_.katex]:text-editor-text">
      <ReactMarkdown
        remarkPlugins={useMath ? [remarkGfm, remarkMath] : [remarkGfm]}
        rehypePlugins={useMath ? [rehypeKatex] : []}
        components={mdComponents}
      >
        {markdown}
      </ReactMarkdown>
    </div>
  );
}

"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import rehypeRaw from "rehype-raw";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import "katex/dist/katex.min.css";
import "github-markdown-css/github-markdown-dark.css";

const mdComponents = {
  // Keep GitHub-like alignment/spacing by letting `github-markdown-css`
  // style the structure. Only override link behavior (open in new tab).
  a: (props: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a target="_blank" rel="noopener noreferrer" {...props} />
  ),
};

export default function MarkdownPreview({
  markdown,
  useMath = true,
}: Readonly<{
  markdown: string;
  useMath?: boolean;
}>) {
  const schema = {
    ...defaultSchema,
    attributes: {
      ...defaultSchema.attributes,
      div: [
        ...(defaultSchema.attributes?.div ?? []),
        ["align"],
      ],
      img: [
        ...(defaultSchema.attributes?.img ?? []),
        ["src"],
        ["alt"],
        ["title"],
        ["width"],
        ["height"],
      ],
      a: [
        ...(defaultSchema.attributes?.a ?? []),
        ["href"],
        ["title"],
      ],
    },
  };

  return (
    <div className="h-full overflow-y-auto bg-editor-bg py-6">
      <div className="w-full flex justify-center px-6">
        <div className="w-full max-w-3xl markdown-body !bg-transparent">
        <ReactMarkdown
          remarkPlugins={useMath ? [remarkGfm, remarkMath] : [remarkGfm]}
          rehypePlugins={
            useMath
              ? [rehypeRaw, [rehypeSanitize, schema], rehypeKatex]
              : [rehypeRaw, [rehypeSanitize, schema]]
          }
          components={mdComponents}
        >
          {markdown}
        </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}


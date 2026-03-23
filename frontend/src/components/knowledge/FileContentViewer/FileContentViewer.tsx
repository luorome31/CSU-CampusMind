import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { Badge } from '../../ui';
import './FileContentViewer.css';

// Warm Paper themed syntax highlighting style (matches MessageBubble)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const warmPaperStyle: any = {
  'code[class*="language-"]': {
    color: '#3B3D3F',
    background: 'none',
    fontFamily: 'ui-monospace, "SF Mono", Monaco, Consolas, monospace',
    fontSize: '0.875rem',
    textAlign: 'left',
    whiteSpace: 'pre',
    wordSpacing: 'normal',
    wordBreak: 'normal',
    wordWrap: 'normal',
    lineHeight: '1.6',
    tabSize: '2',
    hyphens: 'none',
  },
  'pre[class*="language-"]': {
    color: '#3B3D3F',
    background: '#FAF5E9',
    fontFamily: 'ui-monospace, "SF Mono", Monaco, Consolas, monospace',
    fontSize: '0.875rem',
    textAlign: 'left',
    whiteSpace: 'pre',
    wordSpacing: 'normal',
    wordBreak: 'normal',
    wordWrap: 'normal',
    lineHeight: '1.6',
    tabSize: '2',
    hyphens: 'none',
    padding: '1em',
    margin: '1em 0',
    overflow: 'auto',
    borderRadius: '2px',
    border: '1px solid rgba(83, 125, 150, 0.15)',
    boxShadow: '0 1px 2px rgba(59, 61, 63, 0.06)',
  },
  comment: { color: '#8E9196', fontStyle: 'italic' },
  prolog: { color: '#8E9196' },
  doctype: { color: '#8E9196' },
  cdata: { color: '#8E9196' },
  punctuation: { color: '#6B6F73' },
  property: { color: '#537D96' },
  tag: { color: '#537D96' },
  boolean: { color: '#C4846C' },
  number: { color: '#C4846C' },
  constant: { color: '#C4846C' },
  symbol: { color: '#C4846C' },
  deleted: { color: '#cf222e' },
  selector: { color: '#7BAE7F' },
  'attr-name': { color: '#7BAE7F' },
  string: { color: '#7BAE7F' },
  char: { color: '#7BAE7F' },
  builtin: { color: '#7BAE7F' },
  inserted: { color: '#7BAE7F' },
  operator: { color: '#6B6F73' },
  entity: { color: '#537D96', cursor: 'help' },
  url: { color: '#537D96' },
  'atrule': { color: '#537D96' },
  'attr-value': { color: '#7BAE7F' },
  keyword: { color: '#537D96', fontWeight: 'normal' },
  function: { color: '#456A80' },
  'class-name': { color: '#456A80' },
  regex: { color: '#C4846C' },
  important: { color: '#C4846C', fontWeight: 'bold' },
  variable: { color: '#C4846C' },
  bold: { fontWeight: 'bold' },
  italic: { fontStyle: 'italic' },
};

export interface FileContentViewerProps {
  content: string;
  fileName?: string;
}

export function FileContentViewer({ content, fileName }: FileContentViewerProps) {
  if (!content) {
    return <div className="file-content-empty">暂无内容</div>;
  }

  return (
    <div className="file-content-viewer">
      <div className="file-content-header">
        {fileName && <span className="file-content-name">{fileName}</span>}
        <Badge variant="accent" size="sm">只读</Badge>
      </div>
      <div className="file-content-body">
        <ReactMarkdown
          components={{
            code({ node, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              const inline = !match;
              return !inline ? (
                <SyntaxHighlighter
                  language={match[1]}
                  style={warmPaperStyle}
                  PreTag="div"
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
}

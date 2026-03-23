import ReactMarkdown from 'react-markdown';
import SyntaxHighlighter from 'react-syntax-highlighter/dist/esm/prism-light';
import { Badge } from '../../ui';
import './FileContentViewer.css';

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
                  PreTag="div"
                  customStyle={{
                    margin: '1em 0',
                    borderRadius: 'var(--radius-md, 8px)',
                    fontSize: 'var(--text-sm, 0.875rem)',
                  }}
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

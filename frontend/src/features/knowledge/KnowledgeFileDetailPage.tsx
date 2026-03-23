import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui';
import { FileContentViewer } from '../../components/knowledge/FileContentViewer/FileContentViewer';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeFileDetailPage.css';

function Spinner() {
  return <div className="spinner" aria-label="加载中" />;
}

export function KnowledgeFileDetailPage() {
  const { kbId, fileId } = useParams<{ kbId: string; fileId: string }>();
  const navigate = useNavigate();
  const { currentFile, currentFileContent, isLoadingContent, error, fetchFileContent } = knowledgeListStore();

  useEffect(() => {
    if (fileId) {
      fetchFileContent(fileId);
    }
  }, [fileId, fetchFileContent]);

  if (isLoadingContent) {
    return (
      <div className="knowledge-file-detail-page">
        <div className="knowledge-file-detail-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-file-detail-page">
      <header className="knowledge-file-detail-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/knowledge/${kbId}`)}
          className="knowledge-file-detail-back"
        >
          ← 返回
        </Button>
        <h1 className="knowledge-file-detail-title">{currentFile?.file_name || '文件'}</h1>
      </header>

      {error && (
        <div className="knowledge-file-detail-error">
          <p>{error}</p>
        </div>
      )}

      <div className="knowledge-file-detail-content">
        <FileContentViewer content={currentFileContent} fileName={currentFile?.file_name} />
      </div>
    </div>
  );
}

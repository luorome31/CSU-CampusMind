import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui';
import { FileTable } from '../../components/knowledge/FileTable/FileTable';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeFileListPage.css';

function Spinner() {
  return <div className="spinner" aria-label="加载中" />;
}

export function KnowledgeFileListPage() {
  const { kbId } = useParams<{ kbId: string }>();
  const navigate = useNavigate();
  const { currentKB, files, isLoadingFiles, error, fetchFiles, knowledgeBases } = knowledgeListStore();

  useEffect(() => {
    if (kbId) {
      const kb = knowledgeBases.find(k => k.id === kbId);
      if (kb) {
        knowledgeListStore.getState().setCurrentKB(kb);
      }
      fetchFiles(kbId);
    }
  }, [kbId, fetchFiles, knowledgeBases]);

  const handleFileClick = (file: { id: string }) => {
    navigate(`/knowledge/${kbId}/files/${file.id}`);
  };

  if (isLoadingFiles) {
    return (
      <div className="knowledge-file-list-page">
        <div className="knowledge-file-list-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-file-list-page">
      <header className="knowledge-file-list-header">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/knowledge')}
          className="knowledge-file-list-back"
        >
          ← 返回
        </Button>
        <h1 className="knowledge-file-list-title">{currentKB?.name || '知识库'}</h1>
      </header>

      {error && (
        <div className="knowledge-file-list-error">
          <p>{error}</p>
        </div>
      )}

      <div className="knowledge-file-list-content">
        <FileTable files={files} onFileClick={handleFileClick} />
      </div>
    </div>
  );
}

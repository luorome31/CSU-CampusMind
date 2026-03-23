import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgeCard } from '../../components/knowledge/KnowledgeCard/KnowledgeCard';
import { Button } from '../../components/ui/Button';
import { CreateKnowledgeDialog } from './CreateKnowledgeDialog';
import { knowledgeListStore } from './knowledgeListStore';
import { chatStore } from '../chat/chatStore';
import './KnowledgeListPage.css';

function Spinner() {
  return <div className="spinner" aria-label="加载中" />;
}

export function KnowledgeListPage() {
  const navigate = useNavigate();
  const { knowledgeBases, isLoadingKBs, error, fetchKnowledgeBases } = knowledgeListStore();
  const enableRag = chatStore((s) => s.enableRag);
  const toggleRag = chatStore((s) => s.toggleRag);
  const currentKnowledgeIds = chatStore((s) => s.currentKnowledgeIds);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  useEffect(() => {
    fetchKnowledgeBases();
  }, [fetchKnowledgeBases]);

  const handleKBClick = (kbId: string) => {
    navigate(`/knowledge/${kbId}`);
  };

  const handleCreateClick = () => {
    setIsCreateDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsCreateDialogOpen(false);
  };

  if (isLoadingKBs) {
    return (
      <div className="knowledge-list-page">
        <div className="knowledge-list-loading">
          <Spinner />
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-list-page">
      <header className="knowledge-list-header">
        <div className="knowledge-list-header-left">
          <h1 className="knowledge-list-title">知识库</h1>
          {enableRag && currentKnowledgeIds.length > 0 && (
            <span className="knowledge-list-selected">
              已选择 {currentKnowledgeIds.length} 个知识库
            </span>
          )}
        </div>
        <div className="knowledge-list-header-right">
          <label className="knowledge-list-rag-toggle">
            <input
              type="checkbox"
              checked={enableRag}
              onChange={toggleRag}
            />
            <span className="knowledge-list-rag-toggle-switch" />
            <span>RAG 检索</span>
          </label>
          <Button variant="ghost" onClick={handleCreateClick}>+ 新建</Button>
        </div>
      </header>

      {error && (
        <div className="knowledge-list-error">
          <p>{error}</p>
          <button onClick={fetchKnowledgeBases}>重试</button>
        </div>
      )}

      {knowledgeBases.length === 0 && !error ? (
        <div className="knowledge-list-empty">
          <p>暂无知识库</p>
        </div>
      ) : (
        <div className="knowledge-list-grid">
          {knowledgeBases.map((kb) => (
            <KnowledgeCard
              key={kb.id}
              knowledge={kb}
              fileCount={kb.file_count}
              onClick={() => handleKBClick(kb.id)}
            />
          ))}
        </div>
      )}
      <CreateKnowledgeDialog isOpen={isCreateDialogOpen} onClose={handleCloseDialog} />
    </div>
  );
}

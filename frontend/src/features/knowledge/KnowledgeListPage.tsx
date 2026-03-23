import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { KnowledgeCard } from '../../components/knowledge/KnowledgeCard/KnowledgeCard';
import { Button } from '../../components/ui/Button';
import { CreateKnowledgeDialog } from './CreateKnowledgeDialog';
import { knowledgeListStore } from './knowledgeListStore';
import './KnowledgeListPage.css';

function Spinner() {
  return <div className="spinner" aria-label="加载中" />;
}

export function KnowledgeListPage() {
  const navigate = useNavigate();
  const { knowledgeBases, isLoadingKBs, error, fetchKnowledgeBases } = knowledgeListStore();
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
        <h1 className="knowledge-list-title">知识库</h1>
        <Button variant="ghost" onClick={handleCreateClick}>+ 新建</Button>
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
              fileCount={0}
              onClick={() => handleKBClick(kb.id)}
            />
          ))}
        </div>
      )}
      <CreateKnowledgeDialog isOpen={isCreateDialogOpen} onClose={handleCloseDialog} />
    </div>
  );
}

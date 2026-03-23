import React, { useState, useCallback } from 'react';
import { Modal } from '../../components/ui/Modal';
import { Input } from '../../components/ui/Input';
import { Button } from '../../components/ui/Button';
import { knowledgeListStore } from './knowledgeListStore';
import './CreateKnowledgeDialog.css';

interface CreateKnowledgeDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CreateKnowledgeDialog: React.FC<CreateKnowledgeDialogProps> = ({
  isOpen,
  onClose,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [nameError, setNameError] = useState('');

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      // Validate
      if (!name.trim()) {
        setNameError('请输入知识库名称');
        return;
      }

      setIsSubmitting(true);
      setNameError('');

      try {
        await knowledgeListStore.getState().createKnowledgeBase(
          name.trim(),
          description.trim() || undefined
        );

        // Check if there was an error
        const { error } = knowledgeListStore.getState();
        if (error) {
          setNameError(error);
          setIsSubmitting(false);
          return;
        }

        // Success - close dialog and reset form
        setName('');
        setDescription('');
        onClose();
      } catch {
        setNameError('创建知识库失败');
        setIsSubmitting(false);
      }
    },
    [name, description, onClose]
  );

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      setName('');
      setDescription('');
      setNameError('');
      onClose();
    }
  }, [isSubmitting, onClose]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="创建知识库"
      className="create-knowledge-dialog"
    >
      <form onSubmit={handleSubmit} className="create-knowledge-form">
        <Input
          label="知识库名称"
          placeholder="请输入知识库名称"
          value={name}
          onChange={(e) => setName(e.target.value)}
          error={nameError}
          disabled={isSubmitting}
          required
        />

        <div className="create-knowledge-description">
          <label htmlFor="description" className="input-label">
            描述
          </label>
          <textarea
            id="description"
            className="create-knowledge-textarea"
            placeholder="请输入描述（可选）"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={isSubmitting}
            rows={3}
          />
        </div>

        <div className="create-knowledge-actions">
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            取消
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSubmitting}
            disabled={isSubmitting}
          >
            {isSubmitting ? '创建中...' : '创建'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateKnowledgeDialog;

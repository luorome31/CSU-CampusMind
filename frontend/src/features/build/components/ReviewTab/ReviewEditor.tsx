import React, { useState, useCallback, useEffect } from 'react';
import { Save, Play, Eye, Edit3, Bold, Italic, List, ListOrdered, Heading } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import { useToast } from './Toast';
import styles from './ReviewEditor.module.css';

export const ReviewEditor: React.FC = () => {
  const selectedFile = buildStore((s) => s.selectedFile);
  const fileContent = buildStore((s) => s.fileContent);
  const isSaving = buildStore((s) => s.isSaving);
  const isIndexing = buildStore((s) => s.isIndexing);
  const updateFileContent = buildStore((s) => s.updateFileContent);
  const triggerIndex = buildStore((s) => s.triggerIndex);

  const [editedContent, setEditedContent] = useState(fileContent);
  const [isPreview, setIsPreview] = useState(false);
  const { toasts, addToast, dismissToast } = useToast();

  // Sync edited content when file changes
  useEffect(() => {
    setEditedContent(fileContent);
  }, [fileContent]);

  const handleSave = useCallback(async () => {
    if (!selectedFile) return;
    try {
      await updateFileContent(selectedFile.id, editedContent);
      addToast('success', '保存成功');
    } catch {
      addToast('error', '保存失败，请重试');
    }
  }, [selectedFile, updateFileContent, editedContent, addToast]);

  const handleIndex = useCallback(async () => {
    if (!selectedFile) return;
    try {
      await triggerIndex(selectedFile.id);
      addToast('success', '索引创建成功');
    } catch {
      addToast('error', '索引创建失败，请重试');
    }
  }, [selectedFile, triggerIndex, addToast]);

  // Insert markdown formatting at cursor
  const insertFormatting = useCallback((prefix: string, suffix: string = prefix) => {
    const textarea = document.querySelector(`.${styles.editor}`) as HTMLTextAreaElement;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = editedContent.substring(start, end);
    const newText =
      editedContent.substring(0, start) +
      prefix + selectedText + suffix +
      editedContent.substring(end);

    setEditedContent(newText);

    // Restore cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + prefix.length, end + prefix.length);
    }, 0);
  }, [editedContent]);

  if (!selectedFile) {
    return (
      <div className={styles.container}>
        <div className={styles.empty}>
          <p>请从左侧选择文件进行审核</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.fileName}>{selectedFile.file_name}</span>
        <div className={styles.actions}>
          <div className={styles.modeToggle}>
            <button
              className={`${styles.modeBtn} ${!isPreview ? styles.active : ''}`}
              onClick={() => setIsPreview(false)}
              title="编辑模式"
            >
              <Edit3 size={16} />
            </button>
            <button
              className={`${styles.modeBtn} ${isPreview ? styles.active : ''}`}
              onClick={() => setIsPreview(true)}
              title="预览模式"
            >
              <Eye size={16} />
            </button>
          </div>
          <Button
            variant="secondary"
            onClick={handleSave}
            disabled={isSaving || editedContent === fileContent}
            isLoading={isSaving}
          >
            <Save size={16} />
            保存
          </Button>
          <Button
            variant="primary"
            onClick={handleIndex}
            disabled={isIndexing}
            isLoading={isIndexing}
          >
            <Play size={16} />
            确认索引
          </Button>
        </div>
      </div>

      {!isPreview && (
        <div className={styles.toolbar}>
          <button
            className={styles.toolbarBtn}
            onClick={() => insertFormatting('**')}
            title="粗体"
          >
            <Bold size={16} />
          </button>
          <button
            className={styles.toolbarBtn}
            onClick={() => insertFormatting('*')}
            title="斜体"
          >
            <Italic size={16} />
          </button>
          <button
            className={styles.toolbarBtn}
            onClick={() => insertFormatting('# ', '')}
            title="标题"
          >
            <Heading size={16} />
          </button>
          <button
            className={styles.toolbarBtn}
            onClick={() => insertFormatting('- ', '')}
            title="无序列表"
          >
            <List size={16} />
          </button>
          <button
            className={styles.toolbarBtn}
            onClick={() => insertFormatting('1. ', '')}
            title="有序列表"
          >
            <ListOrdered size={16} />
          </button>
        </div>
      )}

      <div className={styles.editorWrapper}>
        {isPreview ? (
          <div className={styles.preview}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{editedContent}</ReactMarkdown>
          </div>
        ) : (
          <textarea
            className={styles.editor}
            value={editedContent}
            onChange={(e) => setEditedContent(e.target.value)}
            placeholder="加载中..."
          />
        )}
      </div>

      {/* Toast container */}
      {toasts.length > 0 && (
        <div className={styles.toastContainer}>
          {toasts.map((toast) => (
            <div
              key={toast.id}
              className={`${styles.toast} ${styles[toast.type]}`}
              onClick={() => dismissToast(toast.id)}
            >
              {toast.type === 'success' ? (
                <span className={styles.toastIcon}>✓</span>
              ) : (
                <span className={styles.toastIcon}>✕</span>
              )}
              <span>{toast.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

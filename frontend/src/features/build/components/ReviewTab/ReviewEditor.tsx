import React, { useState, useCallback, useEffect } from 'react';
import { Save, Play } from 'lucide-react';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import styles from './ReviewEditor.module.css';

export const ReviewEditor: React.FC = () => {
  const selectedFile = buildStore((s) => s.selectedFile);
  const fileContent = buildStore((s) => s.fileContent);
  const isSaving = buildStore((s) => s.isSaving);
  const isIndexing = buildStore((s) => s.isIndexing);
  const updateFileContent = buildStore((s) => s.updateFileContent);
  const triggerIndex = buildStore((s) => s.triggerIndex);

  const [editedContent, setEditedContent] = useState(fileContent);

  // Sync edited content when file changes
  useEffect(() => {
    setEditedContent(fileContent);
  }, [fileContent]);

  const handleSave = useCallback(async () => {
    if (!selectedFile) return;
    await updateFileContent(selectedFile.id, editedContent);
  }, [selectedFile, updateFileContent, editedContent]);

  const handleIndex = useCallback(async () => {
    if (!selectedFile) return;
    await triggerIndex(selectedFile.id);
  }, [selectedFile, triggerIndex]);

  if (!selectedFile) {
    return (
      <div className={styles.empty}>
        <p>请从左侧选择文件进行审核</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.fileName}>{selectedFile.file_name}</span>
        <div className={styles.actions}>
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
      <div className={styles.editorWrapper}>
        <textarea
          className={styles.editor}
          value={editedContent}
          onChange={(e) => setEditedContent(e.target.value)}
          placeholder="加载中..."
        />
      </div>
    </div>
  );
};

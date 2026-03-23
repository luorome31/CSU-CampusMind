import React, { useEffect } from 'react';
import { FileText } from 'lucide-react';
import { buildStore } from '../../buildStore';
import styles from './ReviewInbox.module.css';

export const ReviewInbox: React.FC = () => {
  const pendingFiles = buildStore((s) => s.pendingFiles);
  const selectedFile = buildStore((s) => s.selectedFile);
  const fetchPendingFiles = buildStore((s) => s.fetchPendingFiles);
  const fetchFileContent = buildStore((s) => s.fetchFileContent);

  // Fetch pending files on mount
  useEffect(() => {
    fetchPendingFiles();
  }, [fetchPendingFiles]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
    });
  };

  const handleFileClick = (fileId: string) => {
    fetchFileContent(fileId);
  };

  if (pendingFiles.length === 0) {
    return (
      <div className={styles.empty}>
        <FileText size={48} className={styles.emptyIcon} />
        <p>暂无待审核文件</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span>共 {pendingFiles.length} 个文件</span>
      </div>
      <ul className={styles.list}>
        {pendingFiles.map((file) => (
          <li
            key={file.id}
            className={`${styles.item} ${selectedFile?.id === file.id ? styles.selected : ''}`}
            onClick={() => handleFileClick(file.id)}
          >
            <FileText size={18} className={styles.fileIcon} />
            <span className={styles.fileName}>{file.file_name}</span>
            <span className={styles.date}>{formatDate(file.create_time)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

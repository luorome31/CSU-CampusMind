import React, { useCallback, useRef, useState } from 'react';
import { Upload, X, FileText, Check } from 'lucide-react';
import { Modal } from '../../../../components/ui/Modal';
import { Button } from '../../../../components/ui/Button';
import { buildStore } from '../../buildStore';
import styles from './UrlImportModal.module.css';

const MAX_FILE_SIZE = 1024 * 1024; // 1MB
const MAX_URLS = 100;

export const UrlImportModal: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isOpen = buildStore((s) => s.isImportModalOpen);
  const previewUrls = buildStore((s) => s.previewUrls);
  const closeModal = buildStore((s) => s.closeImportModal);
  const setPreviewUrls = buildStore((s) => s.setPreviewUrls);
  const setCrawlUrls = buildStore((s) => s.setCrawlUrls);

  const parseFile = useCallback((file: File) => {
    setError(null);

    if (!file.name.match(/\.(txt|csv)$/i)) {
      setError('仅支持 .txt 或 .csv 文件');
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError('文件大小不能超过 1MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      let urls: string[] = [];

      if (file.name.endsWith('.csv')) {
        // Parse CSV - take first column
        const lines = content.split('\n');
        urls = lines
          .map((line) => {
            const parts = line.split(',');
            return parts[0]?.trim();
          })
          .filter((url) => url && (url.startsWith('http://') || url.startsWith('https://')));
      } else {
        // Parse txt - one URL per line
        urls = content
          .split('\n')
          .map((line) => line.trim())
          .filter((url) => url.startsWith('http://') || url.startsWith('https://'));
      }

      if (urls.length > MAX_URLS) {
        setError(`URL 数量不能超过 ${MAX_URLS} 个`);
        return;
      }

      if (urls.length === 0) {
        setError('未找到有效的 URL');
        return;
      }

      setPreviewUrls(urls);
    };

    reader.readAsText(file);
  }, [setPreviewUrls]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      parseFile(file);
    }
  }, [parseFile]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      parseFile(file);
    }
  }, [parseFile]);

  const handleConfirm = useCallback(() => {
    if (previewUrls.length > 0) {
      setCrawlUrls(previewUrls.join('\n'));
      closeModal();
    }
  }, [previewUrls, setCrawlUrls, closeModal]);

  const handleRemoveUrl = useCallback((index: number) => {
    setPreviewUrls(previewUrls.filter((_, i) => i !== index));
  }, [previewUrls, setPreviewUrls]);

  return (
    <Modal isOpen={isOpen} onClose={closeModal} title="批量导入URL">
      <div className={styles.container}>
        {previewUrls.length === 0 ? (
          <div
            className={`${styles.dropzone} ${dragActive ? styles.active : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={48} className={styles.uploadIcon} />
            <p className={styles.dropzoneText}>点击上传文件</p>
            <p className={styles.dropzoneHint}>支持 .txt（每行一个URL）或 .csv（第一列）</p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".txt,.csv"
              onChange={handleFileSelect}
              className={styles.fileInput}
            />
          </div>
        ) : (
          <div className={styles.preview}>
            <div className={styles.previewHeader}>
              <FileText size={20} />
              <span>已解析 {previewUrls.length} 个 URL</span>
              <button
                className={styles.clearBtn}
                onClick={() => setPreviewUrls([])}
              >
                清空
              </button>
            </div>
            <ul className={styles.urlList}>
              {previewUrls.slice(0, 20).map((url, index) => (
                <li key={index} className={styles.urlItem}>
                  <span className={styles.urlText}>{url}</span>
                  <button
                    className={styles.removeBtn}
                    onClick={() => handleRemoveUrl(index)}
                  >
                    <X size={14} />
                  </button>
                </li>
              ))}
              {previewUrls.length > 20 && (
                <li className={styles.moreUrls}>
                  还有 {previewUrls.length - 20} 个 URL...
                </li>
              )}
            </ul>
          </div>
        )}

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <div className={styles.actions}>
          <Button variant="ghost" onClick={closeModal}>
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={previewUrls.length === 0}
          >
            <Check size={16} />
            确认导入
          </Button>
        </div>
      </div>
    </Modal>
  );
};

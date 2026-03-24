import React, { useEffect, useMemo, useCallback } from 'react';
import { Play, Upload, Trash2 } from 'lucide-react';
import { Button } from '../../ui/Button';
import { Select } from '../../ui/Select';
import { buildStore } from '../../../features/build/buildStore';
import { knowledgeListStore } from '../../../features/knowledge/knowledgeListStore';
import styles from './CrawlPanel.module.css';

export const CrawlPanel: React.FC = () => {
  const selectedKnowledgeId = buildStore((s) => s.selectedKnowledgeId);
  const crawlUrls = buildStore((s) => s.crawlUrls);
  const setSelectedKnowledgeId = buildStore((s) => s.setSelectedKnowledgeId);
  const setCrawlUrls = buildStore((s) => s.setCrawlUrls);
  const openImportModal = buildStore((s) => s.openImportModal);
  const submitBatchCrawl = buildStore((s) => s.submitBatchCrawl);
  const fetchTasks = buildStore((s) => s.fetchTasks);

  // Fetch knowledge bases on mount
  useEffect(() => {
    knowledgeListStore.getState().fetchKnowledgeBases();
  }, []);

  const knowledgeBases = knowledgeListStore((s) => s.knowledgeBases);

  const urls = useMemo(() => {
    return crawlUrls
      .split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);
  }, [crawlUrls]);

  const isValid = selectedKnowledgeId && urls.length > 0;

  const handleSubmit = useCallback(async () => {
    if (!isValid) return;
    await submitBatchCrawl(urls);
  }, [isValid, submitBatchCrawl, urls]);

  const handleClear = useCallback(() => {
    setCrawlUrls('');
  }, [setCrawlUrls]);

  const handleKnowledgeChange = useCallback((value: string) => {
    setSelectedKnowledgeId(value || null);
  }, [setSelectedKnowledgeId]);

  const handleUrlsChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setCrawlUrls(e.target.value);
  }, [setCrawlUrls]);

  // Refresh tasks on mount
  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return (
    <div className={styles.panel}>
      <div className={styles.form}>
        <div className={styles.field}>
          <label className={styles.label}>选择知识库</label>
          <Select
            value={selectedKnowledgeId || ''}
            options={knowledgeBases.map((kb) => ({
              value: kb.id,
              label: kb.name,
              description: `${kb.file_count} 个文件`,
            }))}
            onChange={handleKnowledgeChange}
            placeholder="请选择知识库"
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>URL列表</label>
          <textarea
            className={styles.textarea}
            placeholder="输入URL，每行一个"
            value={crawlUrls}
            onChange={handleUrlsChange}
            rows={6}
          />
        </div>

        <div className={styles.actions}>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!isValid}
          >
            <Play size={16} />
            开始爬取
          </Button>
          <Button variant="secondary" onClick={openImportModal}>
            <Upload size={16} />
            批量导入
          </Button>
          <Button variant="ghost" onClick={handleClear}>
            <Trash2 size={16} />
            清空
          </Button>
        </div>
      </div>
    </div>
  );
};

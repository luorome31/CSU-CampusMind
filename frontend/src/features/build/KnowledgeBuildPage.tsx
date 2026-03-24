import { useEffect } from 'react';
import { FileSearch, Download } from 'lucide-react';
import { buildStore } from './buildStore';
import { CrawlPanel } from './components/CrawlTab/CrawlPanel';
import { TaskList } from './components/CrawlTab/TaskList';
import { UrlImportModal } from './components/CrawlTab/UrlImportModal';
import { ReviewInbox } from './components/ReviewTab/ReviewInbox';
import { ReviewEditor } from './components/ReviewTab/ReviewEditor';
import styles from './KnowledgeBuildPage.module.css';

export function KnowledgeBuildPage() {
  const activeTab = buildStore((s) => s.activeTab);
  const setActiveTab = buildStore((s) => s.setActiveTab);
  const pendingReviewCount = buildStore((s) => s.pendingReviewCount);
  const fetchPendingFiles = buildStore((s) => s.fetchPendingFiles);
  const tasks = buildStore((s) => s.tasks);
  const removeTask = buildStore((s) => s.removeTask);
  const retryFailedUrls = buildStore((s) => s.retryFailedUrls);
  const clearCompletedTasks = buildStore((s) => s.clearCompletedTasks);

  // Fetch initial data
  useEffect(() => {
    fetchPendingFiles();
  }, [fetchPendingFiles]);

  const handleTabChange = (tab: 'crawl' | 'review') => {
    setActiveTab(tab);
    if (tab === 'review') {
      fetchPendingFiles();
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>知识库构建</h1>
      </div>

      <div className={styles.tabs} role="tablist">
        <button
          role="tab"
          aria-selected={activeTab === 'crawl'}
          className={`${styles.tab} ${activeTab === 'crawl' ? styles.active : ''}`}
          onClick={() => handleTabChange('crawl')}
        >
          <Download size={18} />
          爬取任务
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'review'}
          className={`${styles.tab} ${activeTab === 'review' ? styles.active : ''}`}
          onClick={() => handleTabChange('review')}
        >
          <FileSearch size={18} />
          审核队列
          {pendingReviewCount > 0 && (
            <span className={styles.badge}>{pendingReviewCount}</span>
          )}
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'crawl' ? (
          <div className={styles.crawlContent}>
            <CrawlPanel />
            <TaskList
              tasks={tasks}
              onDelete={removeTask}
              onRetry={retryFailedUrls}
              onClearCompleted={clearCompletedTasks}
            />
          </div>
        ) : (
          <div className={styles.reviewLayout}>
            <div className={styles.reviewSidebar}>
              <ReviewInbox />
            </div>
            <div className={styles.reviewMain}>
              <ReviewEditor />
            </div>
          </div>
        )}
      </div>

      <UrlImportModal />
    </div>
  );
}

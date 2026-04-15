// mobile/src/screens/BuildScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Pressable } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { SegmentedControl } from '../components/build/SegmentedControl';
import { CrawlPanel } from '../components/build/CrawlTab/CrawlPanel';
import { TaskList } from '../components/build/CrawlTab/TaskList';
import { UrlImportModal } from '../components/build/CrawlTab/UrlImportModal';
import { ReviewInbox } from '../components/build/ReviewTab/ReviewInbox';
import { ReviewEditor } from '../components/build/ReviewTab/ReviewEditor';
import { FileSelectModal } from '../components/build/ReviewTab/FileSelectModal';
import { useBuildStore } from '../features/build/buildStore';
import { colors, spacing } from '../styles';
import type { KnowledgeBuildScreenProps } from '../navigation/types';

const MOCK_KB_LIST = [
  { id: 'kb-1', name: '教务处', file_count: 12 },
  { id: 'kb-2', name: '图书馆', file_count: 8 },
  { id: 'kb-3', name: '就业中心', file_count: 5 },
];

const TABS = [
  { value: 'crawl', label: '爬取任务' },
  { value: 'review', label: '审核队列' },
];

export function BuildScreen({ navigation }: KnowledgeBuildScreenProps) {
  const activeTab = useBuildStore((s) => s.activeTab);
  const setActiveTab = useBuildStore((s) => s.setActiveTab);
  const selectedKnowledgeId = useBuildStore((s) => s.selectedKnowledgeId);
  const setSelectedKnowledgeId = useBuildStore((s) => s.setSelectedKnowledgeId);
  const fetchTasks = useBuildStore((s) => s.fetchTasks);
  const fetchPendingFiles = useBuildStore((s) => s.fetchPendingFiles);
  const fetchFileContent = useBuildStore((s) => s.fetchFileContent);
  const pendingFiles = useBuildStore((s) => s.pendingFiles);
  const pendingReviewCount = useBuildStore((s) => s.pendingReviewCount);

  const [isFileSelectModalVisible, setIsFileSelectModalVisible] = useState(false);

  useEffect(() => {
    fetchTasks();
    fetchPendingFiles();
  }, [fetchTasks, fetchPendingFiles]);

  useEffect(() => {
    if (activeTab === 'review' && pendingFiles.length > 0) {
      fetchFileContent(pendingFiles[0].id);
    }
  }, [activeTab, pendingFiles, fetchFileContent]);

  const handleBack = () => {
    navigation.goBack();
  };

  const handleTabChange = (value: string) => {
    setActiveTab(value as 'crawl' | 'review');
  };

  const handleSelectKnowledge = (id: string) => {
    setSelectedKnowledgeId(id);
  };

  const handleOpenImportModal = () => {
    useBuildStore.getState().openImportModal();
  };

  const handleOpenFileSelect = () => {
    setIsFileSelectModalVisible(true);
  };

  const handleCloseFileSelect = () => {
    setIsFileSelectModalVisible(false);
  };

  const handleSelectFile = (file: (typeof pendingFiles)[0]) => {
    fetchFileContent(file.id);
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backButton}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <View style={styles.segmentedControlWrapper}>
          <SegmentedControl
            options={TABS}
            value={activeTab}
            onChange={handleTabChange}
          />
        </View>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {activeTab === 'crawl' ? (
          <>
            <CrawlPanel
              knowledgeBases={MOCK_KB_LIST}
              onSelectKnowledge={handleSelectKnowledge}
              selectedKnowledgeId={selectedKnowledgeId}
              onOpenImportModal={handleOpenImportModal}
            />
            <TaskList />
          </>
        ) : (
          <>
            <View style={styles.reviewInboxWrapper}>
              <ReviewInbox
                count={pendingReviewCount}
                onPress={handleOpenFileSelect}
              />
            </View>
            <ReviewEditor />
          </>
        )}
      </View>

      {/* Modals */}
      <UrlImportModal />
      <FileSelectModal
        visible={isFileSelectModalVisible}
        files={pendingFiles}
        onSelect={handleSelectFile}
        onClose={handleCloseFileSelect}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
  },
  backButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  segmentedControlWrapper: {
    flex: 1,
    alignItems: 'center',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
  },
  reviewInboxWrapper: {
    paddingHorizontal: spacing[4],
    paddingTop: spacing[2],
    paddingBottom: spacing[3],
  },
});

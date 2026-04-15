import React, { useEffect, useCallback, useState } from 'react';
import { View, StyleSheet, ScrollView, Text, Pressable, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Plus } from 'lucide-react-native';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { useChatStore } from '../features/chat/chatStore';
import { KnowledgeCard } from '../components/knowledge/KnowledgeCard';
import { RAGSwitch } from '../components/knowledge/RAGSwitch';
import { colors, typography, spacing, elevation } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';
import type { KnowledgeBase } from '../api/knowledge';

type NavigationProp = NativeStackNavigationProp<KnowledgeStackParamList>;

export function KnowledgeScreen() {
  const navigation = useNavigation<NavigationProp>();
  const [refreshing, setRefreshing] = useState(false);

  const { knowledgeBases, isLoadingKBs, error, fetchKnowledgeBases, clearError } = useKnowledgeStore();
  const enableRag = useChatStore((s) => s.enableRag);
  const toggleRag = useChatStore((s) => s.toggleRag);
  const currentKnowledgeIds = useChatStore((s) => s.currentKnowledgeIds);
  const setCurrentKnowledgeIds = useChatStore((s) => s.setCurrentKnowledgeIds);

  useEffect(() => {
    fetchKnowledgeBases();
  }, [fetchKnowledgeBases]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    clearError();
    await fetchKnowledgeBases();
    setRefreshing(false);
  }, [fetchKnowledgeBases, clearError]);

  const handleToggleRag = () => {
    toggleRag();
  };

  const handleSelectKB = (kbId: string) => {
    const isSelected = currentKnowledgeIds.includes(kbId);
    if (isSelected) {
      setCurrentKnowledgeIds(currentKnowledgeIds.filter(id => id !== kbId));
    } else {
      setCurrentKnowledgeIds([...currentKnowledgeIds, kbId]);
    }
  };

  const handleKBClick = (kb: KnowledgeBase) => {
    navigation.navigate('KnowledgeDetail', { kbId: kb.id });
  };

  const handleBuildPress = () => {
    // 跳转到 HomeTab 的 KnowledgeBuild
    navigation.getParent()?.navigate('HomeTab', {
      screen: 'KnowledgeBuild',
    });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>知识库</Text>
        <Pressable style={styles.buildButton} onPress={handleBuildPress}>
          <Plus size={20} color={colors.accent} />
          <Text style={styles.buildButtonText}>构建</Text>
        </Pressable>
      </View>

      <ScrollView
        style={styles.content}
        contentContainerStyle={styles.contentContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.accent}
          />
        }
      >
        {/* Error Message */}
        {error && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable onPress={onRefresh}>
              <Text style={styles.retryText}>点击重试</Text>
            </Pressable>
          </View>
        )}

        {/* RAG Switch */}
        <RAGSwitch
          enabled={enableRag}
          selectedIds={currentKnowledgeIds}
          knowledgeBases={knowledgeBases}
          onToggle={handleToggleRag}
          onSelect={handleSelectKB}
        />

        {/* KB List */}
        {isLoadingKBs ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : knowledgeBases.length === 0 ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>暂无知识库</Text>
            <Text style={styles.emptySubtext}>点击右上角「构建」创建知识库</Text>
          </View>
        ) : (
          <View style={styles.kbList}>
            {knowledgeBases.map((kb) => (
              <KnowledgeCard
                key={kb.id}
                knowledge={kb}
                fileCount={kb.file_count}
                onClick={() => handleKBClick(kb)}
              />
            ))}
          </View>
        )}
      </ScrollView>
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
  title: {
    fontSize: typography.textXl,
    fontWeight: typography.fontBold,
    color: colors.text,
  },
  buildButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusMd,
  },
  buildButtonText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
    marginLeft: spacing[1],
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: spacing[4],
  },
  errorContainer: {
    backgroundColor: colors.errorBg,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
    marginBottom: spacing[4],
  },
  errorText: {
    color: colors.error,
    fontSize: typography.textSm,
  },
  retryText: {
    color: colors.accent,
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    marginTop: spacing[2],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing[8],
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: spacing[8],
  },
  emptyText: {
    fontSize: typography.textBase,
    color: colors.textLight,
    marginBottom: spacing[2],
  },
  emptySubtext: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  kbList: {
    gap: spacing[3],
  },
});

export default KnowledgeScreen;

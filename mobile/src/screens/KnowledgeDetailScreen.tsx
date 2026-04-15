import React, { useEffect, useCallback } from 'react';
import { View, StyleSheet, Text, Pressable, ActivityIndicator, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { FileTable } from '../components/knowledge/FileTable';
import { colors, typography, spacing, elevation } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';
import type { KnowledgeFile } from '../api/knowledge';

type Props = NativeStackScreenProps<KnowledgeStackParamList, 'KnowledgeDetail'>;

export function KnowledgeDetailScreen({ navigation, route }: Props) {
  const { kbId } = route.params;
  const { knowledgeBases, files, currentKB, isLoadingFiles, error, fetchFiles, setCurrentKB, clearError } = useKnowledgeStore();

  const handleRetry = useCallback(() => {
    clearError();
    fetchFiles(kbId);
  }, [clearError, fetchFiles, kbId]);

  useEffect(() => {
    const kb = knowledgeBases.find(k => k.id === kbId);
    if (kb) {
      setCurrentKB(kb);
    }
    fetchFiles(kbId);
  }, [kbId, setCurrentKB, fetchFiles]);

  const handleBack = () => {
    navigation.goBack();
  };

  const handleFileClick = (file: KnowledgeFile) => {
    navigation.navigate('FileDetail', { fileId: file.id });
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backButton}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {currentKB?.name || '知识库'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {error ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{error}</Text>
            <Pressable onPress={handleRetry}>
              <Text style={styles.retryText}>点击重试</Text>
            </Pressable>
          </View>
        ) : isLoadingFiles ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <ScrollView>
            <FileTable files={files} onFileClick={handleFileClick} />
          </ScrollView>
        )}
      </View>
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
    padding: spacing[2],
  },
  title: {
    flex: 1,
    fontSize: typography.textBase,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    textAlign: 'center',
  },
  placeholder: {
    width: 40,
  },
  content: {
    flex: 1,
    padding: spacing[4],
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    backgroundColor: colors.errorBg,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
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
});

export default KnowledgeDetailScreen;

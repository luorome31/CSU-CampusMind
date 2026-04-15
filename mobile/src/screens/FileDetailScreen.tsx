import React, { useEffect } from 'react';
import { View, StyleSheet, Text, Pressable, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ChevronLeft } from 'lucide-react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import { useKnowledgeStore } from '../features/knowledge/knowledgeStore';
import { FileContentViewer } from '../components/knowledge/FileContentViewer';
import { colors, typography, spacing } from '../styles';
import type { KnowledgeStackParamList } from '../navigation/types';

type Props = NativeStackScreenProps<KnowledgeStackParamList, 'FileDetail'>;

export function FileDetailScreen({ navigation, route }: Props) {
  const { fileId } = route.params;
  const { currentFile, currentFileContent, isLoadingContent, fetchFileContent } = useKnowledgeStore();

  useEffect(() => {
    fetchFileContent(fileId);
  }, [fileId, fetchFileContent]);

  const handleBack = () => {
    navigation.goBack();
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Pressable onPress={handleBack} style={styles.backButton}>
          <ChevronLeft size={24} color={colors.text} />
        </Pressable>
        <Text style={styles.title} numberOfLines={1}>
          {currentFile?.file_name || '文件详情'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      {/* Content */}
      <View style={styles.content}>
        {isLoadingContent ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={colors.accent} />
          </View>
        ) : (
          <FileContentViewer content={currentFileContent} fileName={currentFile?.file_name} />
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
});

export default FileDetailScreen;

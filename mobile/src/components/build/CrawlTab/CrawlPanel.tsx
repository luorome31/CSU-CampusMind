import React, { useMemo, useCallback } from 'react';
import { View, Text, TextInput, ScrollView, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { Play, Upload, Trash2 } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

interface CrawlPanelProps {
  knowledgeBases: Array<{ id: string; name: string; file_count: number }>;
  onSelectKnowledge: (id: string) => void;
  selectedKnowledgeId: string | null;
  onOpenImportModal: () => void;
}

export function CrawlPanel({
  knowledgeBases,
  onSelectKnowledge,
  selectedKnowledgeId,
  onOpenImportModal,
}: CrawlPanelProps) {
  const crawlUrls = useBuildStore((s) => s.crawlUrls);
  const setCrawlUrls = useBuildStore((s) => s.setCrawlUrls);
  const submitBatchCrawl = useBuildStore((s) => s.submitBatchCrawl);
  const isPolling = useBuildStore((s) => s.isPolling);

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

  const selectedKB = knowledgeBases.find((kb) => kb.id === selectedKnowledgeId);

  return (
    <View style={styles.panel}>
      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.label}>知识库选择</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.kbList}>
            {knowledgeBases.map((kb) => (
              <Pressable
                key={kb.id}
                style={[
                  styles.kbChip,
                  selectedKnowledgeId === kb.id && styles.kbChipSelected,
                ]}
                onPress={() => onSelectKnowledge(kb.id)}
              >
                <Text style={[
                  styles.kbChipText,
                  selectedKnowledgeId === kb.id && styles.kbChipTextSelected,
                ]}>
                  {kb.name}
                </Text>
              </Pressable>
            ))}
          </ScrollView>
          {selectedKB && (
            <Text style={styles.kbInfo}>{selectedKB.file_count} 个文件</Text>
          )}
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>URL列表</Text>
          <TextInput
            style={styles.textarea}
            placeholder="输入URL，每行一个"
            placeholderTextColor={colors.textMuted}
            value={crawlUrls}
            onChangeText={setCrawlUrls}
            multiline
            numberOfLines={6}
            textAlignVertical="top"
          />
        </View>

        <View style={styles.actions}>
          <Pressable
            style={[styles.btn, styles.btnPrimary, !isValid && styles.btnDisabled]}
            onPress={handleSubmit}
            disabled={!isValid || isPolling}
          >
            {isPolling ? (
              <ActivityIndicator size="small" color={colors.background} />
            ) : (
              <>
                <Play size={16} color={colors.background} />
                <Text style={styles.btnPrimaryText}>开始爬取</Text>
              </>
            )}
          </Pressable>
          <Pressable style={[styles.btn, styles.btnSecondary]} onPress={onOpenImportModal}>
            <Upload size={16} color={colors.accent} />
            <Text style={styles.btnSecondaryText}>批量导入</Text>
          </Pressable>
          <Pressable style={[styles.btn, styles.btnGhost]} onPress={handleClear}>
            <Trash2 size={16} color={colors.textMuted} />
            <Text style={styles.btnGhostText}>清空</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    padding: spacing[4],
  },
  form: {
    gap: spacing[4],
  },
  field: {
    gap: spacing[2],
  },
  label: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  kbList: {
    flexDirection: 'row',
    gap: spacing[2],
  },
  kbChip: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    backgroundColor: colors.backgroundGlass,
    borderRadius: elevation.radiusFull,
    borderWidth: 1,
    borderColor: colors.border,
  },
  kbChipSelected: {
    backgroundColor: colors.accent,
    borderColor: colors.accent,
  },
  kbChipText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  kbChipTextSelected: {
    color: colors.background,
  },
  kbInfo: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  textarea: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[3],
    fontSize: typography.textSm,
    color: colors.text,
    minHeight: 120,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    flexWrap: 'wrap',
  },
  btn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[1],
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderRadius: elevation.radiusMd,
    minHeight: spacing.buttonHeightMd,
  },
  btnPrimary: {
    backgroundColor: colors.accent,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnPrimaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.background,
  },
  btnSecondary: {
    backgroundColor: colors.accentLight,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
  },
  btnGhost: {
    backgroundColor: 'transparent',
  },
  btnGhostText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
});

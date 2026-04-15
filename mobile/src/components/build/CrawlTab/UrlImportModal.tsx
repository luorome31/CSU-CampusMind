// mobile/src/components/build/CrawlTab/UrlImportModal.tsx
import React, { useState } from 'react';
import { View, Text, TextInput, Modal, Pressable, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { X } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

export function UrlImportModal() {
  const isOpen = useBuildStore((s) => s.isImportModalOpen);
  const previewUrls = useBuildStore((s) => s.previewUrls);
  const setPreviewUrls = useBuildStore((s) => s.setPreviewUrls);
  const closeModal = useBuildStore((s) => s.closeImportModal);
  const submitBatchCrawl = useBuildStore((s) => s.submitBatchCrawl);
  const selectedKnowledgeId = useBuildStore((s) => s.selectedKnowledgeId);

  const [inputText, setInputText] = useState('');

  const handleImport = () => {
    const urls = inputText
      .split('\n')
      .map((url) => url.trim())
      .filter((url) => url.length > 0);
    setPreviewUrls(urls);
  };

  const handleConfirm = async () => {
    if (previewUrls.length > 0 && selectedKnowledgeId) {
      await submitBatchCrawl(previewUrls);
      closeModal();
      setInputText('');
      setPreviewUrls([]);
    }
  };

  const handleClose = () => {
    closeModal();
    setInputText('');
    setPreviewUrls([]);
  };

  return (
    <Modal visible={isOpen} animationType="slide" transparent>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.overlay}
      >
        <Pressable style={styles.backdrop} onPress={handleClose} />
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>批量导入URL</Text>
            <Pressable onPress={handleClose} style={styles.closeBtn}>
              <X size={20} color={colors.text} />
            </Pressable>
          </View>

          <TextInput
            style={styles.textarea}
            placeholder="输入URL，每行一个"
            placeholderTextColor={colors.textMuted}
            value={inputText}
            onChangeText={setInputText}
            multiline
            numberOfLines={8}
            textAlignVertical="top"
          />

          <View style={styles.actions}>
            <Pressable style={styles.btnSecondary} onPress={handleImport}>
              <Text style={styles.btnSecondaryText}>预览</Text>
            </Pressable>
            <Pressable
              style={[styles.btnPrimary, previewUrls.length === 0 && styles.btnDisabled]}
              onPress={handleConfirm}
              disabled={previewUrls.length === 0}
            >
              <Text style={styles.btnPrimaryText}>导入 ({previewUrls.length})</Text>
            </Pressable>
          </View>

          {previewUrls.length > 0 && (
            <View style={styles.preview}>
              <Text style={styles.previewTitle}>预览 ({previewUrls.length})</Text>
              {previewUrls.slice(0, 5).map((url, idx) => (
                <Text key={idx} style={styles.previewUrl} numberOfLines={1}>
                  {url}
                </Text>
              ))}
              {previewUrls.length > 5 && (
                <Text style={styles.previewMore}>...还有 {previewUrls.length - 5} 个</Text>
              )}
            </View>
          )}
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {
    backgroundColor: colors.backgroundCard,
    borderTopLeftRadius: elevation.radiusXl,
    borderTopRightRadius: elevation.radiusXl,
    padding: spacing[4],
    maxHeight: '80%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  title: {
    fontSize: typography.textBase,
    fontWeight: typography.fontSemibold,
    color: colors.text,
  },
  closeBtn: {
    padding: spacing[1],
  },
  textarea: {
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[3],
    fontSize: typography.textSm,
    color: colors.text,
    minHeight: 160,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    marginTop: spacing[4],
  },
  btnPrimary: {
    flex: 1,
    backgroundColor: colors.accent,
    paddingVertical: spacing[3],
    borderRadius: elevation.radiusMd,
    alignItems: 'center',
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
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
  preview: {
    marginTop: spacing[4],
    padding: spacing[3],
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
  },
  previewTitle: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginBottom: spacing[2],
  },
  previewUrl: {
    fontSize: typography.textXs,
    color: colors.text,
    fontFamily: 'monospace',
    paddingVertical: 2,
  },
  previewMore: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginTop: spacing[1],
  },
});

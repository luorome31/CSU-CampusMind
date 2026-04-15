// mobile/src/components/build/ReviewTab/ReviewEditor.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Pressable, StyleSheet, ActivityIndicator } from 'react-native';
import { Eye, Edit3 } from 'lucide-react-native';
import { useBuildStore } from '../../../features/build/buildStore';
import { colors, typography, spacing, elevation } from '../../../styles';

export function ReviewEditor() {
  const selectedFile = useBuildStore((s) => s.selectedFile);
  const fileContent = useBuildStore((s) => s.fileContent);
  const isLoadingContent = useBuildStore((s) => s.isLoadingContent);
  const isSaving = useBuildStore((s) => s.isSaving);
  const isIndexing = useBuildStore((s) => s.isIndexing);
  const isPreview = useBuildStore((s) => s.isPreview);
  const updateFileContent = useBuildStore((s) => s.updateFileContent);
  const triggerIndex = useBuildStore((s) => s.triggerIndex);
  const setIsPreview = useBuildStore((s) => s.setIsPreview);

  const [editedContent, setEditedContent] = useState(fileContent);

  // Sync local state when fileContent changes from store
  useEffect(() => {
    setEditedContent(fileContent);
  }, [fileContent]);

  const isContentChanged = editedContent !== fileContent;
  const canSave = isContentChanged && !isSaving;
  const canIndex = !isIndexing && selectedFile !== null;

  const handleSave = async () => {
    if (!selectedFile || !canSave) return;
    await updateFileContent(selectedFile.id, editedContent);
  };

  const handleIndex = async () => {
    if (!selectedFile || !canIndex) return;
    await triggerIndex(selectedFile.id);
  };

  if (!selectedFile) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={styles.emptyText}>请从上方选择文件进行审核</Text>
      </View>
    );
  }

  if (isLoadingContent) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Toggle */}
      <View style={styles.toggleContainer}>
        <View style={styles.toggle}>
          <Pressable
            style={[styles.toggleBtn, !isPreview && styles.toggleBtnActive]}
            onPress={() => setIsPreview(false)}
          >
            <Edit3 size={16} color={!isPreview ? colors.accent : colors.textMuted} />
            <Text style={[styles.toggleText, !isPreview && styles.toggleTextActive]}>编辑</Text>
          </Pressable>
          <Pressable
            style={[styles.toggleBtn, isPreview && styles.toggleBtnActive]}
            onPress={() => setIsPreview(true)}
          >
            <Eye size={16} color={isPreview ? colors.accent : colors.textMuted} />
            <Text style={[styles.toggleText, isPreview && styles.toggleTextActive]}>预览</Text>
          </Pressable>
        </View>
      </View>

      {/* Content Area */}
      <View style={styles.contentContainer}>
        {isPreview ? (
          <Text style={styles.previewContent}>{fileContent}</Text>
        ) : (
          <TextInput
            style={styles.editor}
            value={editedContent}
            onChangeText={setEditedContent}
            multiline
            textAlignVertical="top"
            placeholder="文件内容"
            placeholderTextColor={colors.textMuted}
          />
        )}
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        <Pressable
          style={[styles.btn, styles.btnPrimary, !canSave && styles.btnDisabled]}
          onPress={handleSave}
          disabled={!canSave}
        >
          {isSaving ? (
            <ActivityIndicator size="small" color={colors.background} />
          ) : (
            <Text style={styles.btnPrimaryText}>保存</Text>
          )}
        </Pressable>
        <Pressable
          style={[styles.btn, styles.btnSecondary, !canIndex && styles.btnDisabled]}
          onPress={handleIndex}
          disabled={!canIndex}
        >
          {isIndexing ? (
            <ActivityIndicator size="small" color={colors.accent} />
          ) : (
            <Text style={styles.btnSecondaryText}>确认索引</Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  emptyContainer: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing[4],
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusMd,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  toggleContainer: {
    flexDirection: 'row',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  toggle: {
    flexDirection: 'row',
    paddingHorizontal: spacing[2],
  },
  toggleBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing[1],
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[3],
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  toggleBtnActive: {
    borderBottomColor: colors.accent,
  },
  toggleText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  toggleTextActive: {
    color: colors.accent,
    fontWeight: typography.fontSemibold,
  },
  contentContainer: {
    flex: 1,
    minHeight: 200,
  },
  editor: {
    flex: 1,
    padding: spacing[4],
    fontSize: typography.textSm,
    color: colors.text,
    fontFamily: typography.fontMono,
    lineHeight: typography.textSm * typography.leadingNormal,
  },
  previewContent: {
    flex: 1,
    padding: spacing[4],
    fontSize: typography.textSm,
    color: colors.text,
    fontFamily: typography.fontMono,
    lineHeight: typography.textSm * typography.leadingNormal,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing[2],
    padding: spacing[4],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  btn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing[3],
    borderRadius: elevation.radiusMd,
    minHeight: spacing.buttonHeightMd,
  },
  btnPrimary: {
    backgroundColor: colors.accent,
  },
  btnSecondary: {
    backgroundColor: colors.accentLight,
  },
  btnDisabled: {
    opacity: 0.5,
  },
  btnPrimaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.background,
  },
  btnSecondaryText: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.accent,
  },
});

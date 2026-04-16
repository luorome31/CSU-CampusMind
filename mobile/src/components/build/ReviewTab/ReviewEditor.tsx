// mobile/src/components/build/ReviewTab/ReviewEditor.tsx
import React, { useState, useEffect } from 'react';
import { View, Pressable, StyleSheet, ActivityIndicator, ScrollView } from 'react-native';
import { Text, TextInput } from '@/components/ui/StyledText';
import Markdown, {
  // @ts-expect-error - FitImage is exported in JS but missing in type definitions
  FitImage
} from 'react-native-markdown-display';

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

  const markdownRules = {
    image: (node: any, children: any, parent: any, styles: any, allowedImageHandlers: any, defaultImageHandler: any) => {
      const { src, alt } = node.attributes;

      const show = allowedImageHandlers.filter((value: string) => {
        return src.toLowerCase().startsWith(value.toLowerCase());
      }).length > 0;

      if (show === false && defaultImageHandler === null) {
        return null;
      }

      const uri = show === true ? src : `${defaultImageHandler}${src}`;

      return (
        <FitImage
          key={node.key}
          // Set indicator to false to avoid stuck spinner issue in some RN versions
          indicator={false}
          style={styles._VIEW_SAFE_image}
          source={{ uri }}
          accessible={!!alt}
          accessibilityLabel={alt}
        />

      );
    },
  };


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
          <ScrollView style={{ flex: 1 }}>
            <Markdown style={markdownStyles} rules={markdownRules as any}>{fileContent}</Markdown>

          </ScrollView>
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
          style={[styles.btn, styles.btnSecondary, !canSave && styles.btnDisabled]}
          onPress={handleSave}
          disabled={!canSave}
          accessibilityLabel="保存"
        >
          {isSaving ? (
            <ActivityIndicator size="small" color={colors.background} />
          ) : (
            <Text style={styles.btnSecondaryText}>保存</Text>
          )}
        </Pressable>
        <Pressable
          style={[styles.btn, styles.btnPrimary, !canIndex && styles.btnDisabled]}
          onPress={handleIndex}
          disabled={!canIndex}
          accessibilityLabel="确认索引"
        >
          {isIndexing ? (
            <ActivityIndicator size="small" color={colors.accent} />
          ) : (
            <Text style={styles.btnPrimaryText}>确认索引</Text>
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
    lineHeight: 22,
  },
  previewContent: {
    padding: spacing[4],
    fontSize: typography.textSm,
    color: colors.text,
    fontFamily: typography.fontMono,
    lineHeight: 22,
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

const markdownStyles = StyleSheet.create({
  body: {
    fontSize: typography.textSm,
    color: colors.text,
    fontFamily: typography.fontMono,
    lineHeight: 22,
  },
  heading1: {
    fontSize: typography.textXl,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  heading2: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  heading3: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[1],
  },
  paragraph: {
    fontSize: typography.textSm,
    color: colors.text,
    marginBottom: spacing[2],
  },
  code_inline: {
    fontFamily: typography.fontMono,
    fontSize: typography.textXs,
    backgroundColor: colors.backgroundGlass,
    paddingHorizontal: spacing[1],
    borderRadius: elevation.radiusSm,
    color: colors.accent,
  },
  code_block: {
    fontFamily: typography.fontMono,
    fontSize: typography.textXs,
    backgroundColor: colors.backgroundCard,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
    marginVertical: spacing[2],
  },
  fence: {
    fontFamily: typography.fontMono,
    fontSize: typography.textXs,
    backgroundColor: colors.backgroundCard,
    padding: spacing[3],
    borderRadius: elevation.radiusMd,
    marginVertical: spacing[2],
  },
  list_item: {
    fontSize: typography.textSm,
    color: colors.text,
    marginBottom: spacing[1],
  },
  blockquote: {
    backgroundColor: colors.backgroundGlass,
    borderLeftWidth: 3,
    borderLeftColor: colors.accent,
    paddingLeft: spacing[3],
    paddingVertical: spacing[1],
  },
  link: {
    color: colors.accent,
  },
  strong: {
    fontWeight: typography.fontBold,
  },
  em: {
    fontStyle: 'italic',
  },
  hr: {
    backgroundColor: colors.border,
    height: 1,
    marginVertical: spacing[3],
  },
});

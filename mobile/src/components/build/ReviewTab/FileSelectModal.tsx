// mobile/src/components/build/ReviewTab/FileSelectModal.tsx
import React from 'react';
import { View, Modal, Pressable, FlatList, StyleSheet } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { X, FileText } from 'lucide-react-native';
import { KnowledgeFile } from '../../../api/knowledge';
import { colors, typography, spacing, elevation } from '../../../styles';

interface FileSelectModalProps {
  visible: boolean;
  files: KnowledgeFile[];
  onSelect: (file: KnowledgeFile) => void;
  onClose: () => void;
}

export function FileSelectModal({ visible, files, onSelect, onClose }: FileSelectModalProps) {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
    });
  };

  const renderItem = ({ item }: { item: KnowledgeFile }) => (
    <Pressable
      style={styles.fileItem}
      onPress={() => {
        onSelect(item);
        onClose();
      }}
    >
      <FileText size={18} color={colors.accent} />
      <Text style={styles.fileName} numberOfLines={1}>
        {item.file_name}
      </Text>
      <Text style={styles.fileDate}>{formatDate(item.create_time)}</Text>
    </Pressable>
  );

  return (
    <Modal visible={visible} animationType="slide" transparent>
      <View style={styles.overlay}>
        <Pressable style={styles.backdrop} onPress={onClose} />
        <View style={styles.container}>
          <View style={styles.header}>
            <Text style={styles.title}>选择文件</Text>
            <Pressable onPress={onClose} style={styles.closeBtn}>
              <X size={20} color={colors.text} />
            </Pressable>
          </View>

          <FlatList
            data={files}
            keyExtractor={(item) => item.id}
            renderItem={renderItem}
            ItemSeparatorComponent={() => <View style={styles.separator} />}
            ListEmptyComponent={
              <View style={styles.empty}>
                <Text style={styles.emptyText}>暂无待审核文件</Text>
              </View>
            }
          />

          <View style={styles.footer}>
            <Pressable style={styles.cancelBtn} onPress={onClose}>
              <Text style={styles.cancelText}>取消</Text>
            </Pressable>
          </View>
        </View>
      </View>
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
    maxHeight: '70%',
    paddingBottom: spacing[4],
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: typography.textBase,
    fontWeight: typography.fontSemibold,
    color: colors.text,
  },
  closeBtn: {
    padding: spacing[1],
  },
  fileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    gap: spacing[3],
  },
  fileName: {
    flex: 1,
    fontSize: typography.textSm,
    color: colors.text,
  },
  fileDate: {
    fontSize: typography.textXs,
    color: colors.textMuted,
  },
  separator: {
    height: StyleSheet.hairlineWidth,
    backgroundColor: colors.border,
    marginLeft: spacing[4] + 18 + spacing[3],
  },
  empty: {
    padding: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  footer: {
    padding: spacing[4],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  cancelBtn: {
    padding: spacing[3],
    alignItems: 'center',
    borderRadius: elevation.radiusMd,
    backgroundColor: colors.background,
  },
  cancelText: {
    fontSize: typography.textSm,
    color: colors.text,
  },
});

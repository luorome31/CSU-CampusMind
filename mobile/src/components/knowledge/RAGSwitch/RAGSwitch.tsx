import React from 'react';
import { View, StyleSheet, Pressable, ScrollView } from 'react-native';
import { Text } from '@/components/ui/StyledText';
import { ChevronDown, ChevronUp, Check } from 'lucide-react-native';
import { Card } from '../../ui';
import { colors, typography, spacing, elevation } from '../../../styles';
import type { KnowledgeBase } from '../../../api/knowledge';

export interface RAGSwitchProps {
  enabled: boolean;
  selectedIds: string[];
  knowledgeBases: KnowledgeBase[];
  onToggle: () => void;
  onSelect: (id: string) => void;
}

export const RAGSwitch: React.FC<RAGSwitchProps> = ({
  enabled,
  selectedIds,
  knowledgeBases,
  onToggle,
  onSelect,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <Card variant="default" padding="sm" style={styles.container}>
      <View style={styles.header}>
        <Pressable
          style={styles.toggleRow}
          onPress={onToggle}
          accessibilityRole="switch"
          accessibilityLabel="RAG 检索开关"
          accessibilityState={{ checked: enabled }}
        >
          <View style={[styles.switch, enabled && styles.switchEnabled]}>
            <View style={[styles.switchThumb, enabled && styles.switchThumbEnabled]} />
          </View>
          <Text style={styles.toggleLabel}>RAG 检索</Text>
        </Pressable>
        <Pressable
          style={styles.expandButton}
          onPress={() => setIsExpanded(!isExpanded)}
          accessibilityRole="button"
          accessibilityLabel={isExpanded ? '收起知识库列表' : '展开知识库列表'}
        >
          {isExpanded ? (
            <ChevronUp size={20} color={colors.textLight} />
          ) : (
            <ChevronDown size={20} color={colors.textLight} />
          )}
        </Pressable>
      </View>

      {isExpanded && (
        <ScrollView style={styles.kbList}>
          {knowledgeBases.length === 0 ? (
            <Text style={styles.emptyText}>暂无可用知识库</Text>
          ) : (
            knowledgeBases.map((kb) => {
              const isSelected = selectedIds.includes(kb.id);
              return (
                <Pressable
                  key={kb.id}
                  style={[styles.kbItem, isSelected && styles.kbItemSelected]}
                  onPress={() => onSelect(kb.id)}
                  accessibilityRole="checkbox"
                  accessibilityState={{ checked: isSelected }}
                >
                  <View style={styles.kbInfo}>
                    <Text style={styles.kbName} numberOfLines={1}>
                      {kb.name}
                    </Text>
                    <Text style={styles.kbFileCount}>{kb.file_count} 个文件</Text>
                  </View>
                  {isSelected && (
                    <Check size={18} color={colors.accent} />
                  )}
                </Pressable>
              );
            })
          )}
        </ScrollView>
      )}

      {selectedIds.length > 0 && (
        <Text style={styles.selectedText}>
          已选择 {selectedIds.length} 个知识库
        </Text>
      )}
    </Card>
  );
};

const styles = StyleSheet.create({
  container: {
    marginBottom: spacing[4],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  switch: {
    width: 44,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.textMuted,
    padding: 2,
    marginRight: spacing[3],
  },
  switchEnabled: {
    backgroundColor: colors.accent,
  },
  switchThumb: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.backgroundCard,
  },
  switchThumbEnabled: {
    transform: [{ translateX: 20 }],
  },
  toggleLabel: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  expandButton: {
    padding: spacing[2],
  },
  kbList: {
    marginTop: spacing[3],
    maxHeight: 200,
  },
  kbItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[2],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  kbItemSelected: {
    backgroundColor: colors.accentLight,
    borderRadius: elevation.radiusMd,
  },
  kbInfo: {
    flex: 1,
  },
  kbName: {
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
    color: colors.text,
  },
  kbFileCount: {
    fontSize: typography.textXs,
    color: colors.textMuted,
    marginTop: 2,
  },
  emptyText: {
    fontSize: typography.textSm,
    color: colors.textMuted,
    textAlign: 'center',
    padding: spacing[4],
  },
  selectedText: {
    fontSize: typography.textXs,
    color: colors.accent,
    marginTop: spacing[2],
  },
});

export default RAGSwitch;
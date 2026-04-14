// mobile/src/components/home/HistoryList.tsx
import React from 'react';
import { View, Text, StyleSheet, FlatList, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MessageSquare } from 'lucide-react-native';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList } from '../../navigation/types';
import type { Dialog } from '../../api/dialog';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

interface HistoryListProps {
  dialogs: Dialog[];
}

function HistoryItem({ dialog }: { dialog: Dialog }) {
  const navigation = useNavigation<NavigationProp>();
  const title = dialog.title || '新对话';
  const updatedDate = new Date(dialog.updated_at);
  const isValidDate = !isNaN(updatedDate.getTime());
  const time = isValidDate
    ? formatDistanceToNow(updatedDate, { addSuffix: true, locale: zhCN })
    : '未知时间';
  // console.log(`[HistoryList] dialog:`, dialog);
  return (
    <Pressable
      style={({ pressed }) => [styles.item, pressed && styles.itemPressed]}
      onPress={() =>
        navigation.navigate('ChatsTab', {
          screen: 'ChatDetail',
          params: { dialogId: dialog.id },
        } as any)
      }
    >
      <MessageSquare size={16} color={colors.accent} strokeWidth={2} />
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle} numberOfLines={1}>
          {title}
        </Text>
        <Text style={styles.itemTime}>{time}</Text>
      </View>
    </Pressable>
  );
}

export function HistoryList({ dialogs }: HistoryListProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>最近对话</Text>
      {dialogs.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>暂无对话记录</Text>
        </View>
      ) : (
        <FlatList
          data={dialogs}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => <HistoryItem dialog={item} />}
          scrollEnabled={false}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[6],
    paddingHorizontal: spacing[4],
  },
  sectionTitle: {
    fontSize: typography.textLg,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[3],
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing[3],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
    gap: spacing[3],
  },
  itemPressed: {
    opacity: 0.7,
  },
  itemContent: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  itemTitle: {
    fontSize: typography.textBase,
    color: colors.text,
    flex: 1,
    marginRight: spacing[2],
  },
  itemTime: {
    fontSize: typography.textSm,
    color: colors.textMuted,
  },
  empty: {
    paddingVertical: spacing[8],
    alignItems: 'center',
  },
  emptyText: {
    fontSize: typography.textBase,
    color: colors.textMuted,
  },
});

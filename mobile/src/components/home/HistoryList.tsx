import React from 'react';
import { View, Text, StyleSheet, FlatList, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { MessageSquare, ArrowRight } from 'lucide-react-native';
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
      <View style={styles.iconContainer}>
        <MessageSquare size={16} color={colors.textLight} strokeWidth={2} />
      </View>
      <View style={styles.itemContent}>
        <Text style={styles.itemTitle} numberOfLines={1}>
          {title}
        </Text>
      </View>
      <ArrowRight size={18} color={colors.textLight} />
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
          contentContainerStyle={styles.listContainer}
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
    fontSize: 20,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[4],
  },
  listContainer: {
    paddingBottom: spacing[4],
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 16,
    backgroundColor: '#FCFAF5',
    marginBottom: spacing[3],
  },
  itemPressed: {
    opacity: 0.7,
  },
  iconContainer: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.04)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing[3],
  },
  itemContent: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemTitle: {
    fontSize: typography.textBase,
    color: colors.text,
    flex: 1,
    marginRight: spacing[2],
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

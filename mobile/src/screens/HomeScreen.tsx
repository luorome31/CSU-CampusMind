import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator, View, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { HeroBanner, FeatureGrid, HistoryList } from '../components/home';
import { listDialogs } from '../api/dialog';
import { colors, spacing, typography } from '../styles';
import type { Dialog } from '../api/dialog';

export function HomeScreen() {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDialogs()
      .then(setDialogs)
      .catch(() => setDialogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>首页</Text>
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <HeroBanner />
        <FeatureGrid />
        {loading ? (
          <View style={styles.loading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : (
          <HistoryList dialogs={dialogs} />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[3],
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: typography.fontBold,
    color: colors.text,
  },
  scroll: {
    flex: 1,
  },
  content: {
    paddingBottom: spacing[8],
  },
  loading: {
    marginTop: spacing[8],
    alignItems: 'center',
  },
});

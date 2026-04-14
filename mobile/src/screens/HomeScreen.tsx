// mobile/src/screens/HomeScreen.tsx
import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, ActivityIndicator, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { HeroBanner, FeatureGrid, HistoryList } from '../components/home';
import { listDialogs } from '../api/dialog';
import { colors, spacing } from '../styles';
import type { Dialog } from '../api/dialog';

export function HomeScreen() {
  const [dialogs, setDialogs] = useState<Dialog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listDialogs(10)
      .then(setDialogs)
      .catch(() => setDialogs([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
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

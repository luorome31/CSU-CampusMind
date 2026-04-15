import React, { useEffect } from 'react';
import {
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  View,
  Text,
  Pressable,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Info, FileText, LogOut } from 'lucide-react-native';
import { ProfileCard, StatsGrid, SessionList } from '../features/profile/components';
import { useProfileStore } from '../features/profile/profileStore';
import { useAuthStore } from '../features/auth/authStore';
import { colors, typography, spacing } from '../styles';

export function ProfileScreen() {
  const { user, isLoading, loadProfile, loadStats, loadSessions } = useProfileStore();
  const { logout } = useAuthStore();

  useEffect(() => {
    loadProfile();
    loadStats();
    loadSessions();
  }, []);

  const handleLogout = () => {
    Alert.alert('退出登录', '确定要退出登录吗？', [
      { text: '取消', style: 'cancel' },
      {
        text: '确定',
        style: 'destructive',
        onPress: () => logout(),
      },
    ]);
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>个人中心</Text>
      </View>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {isLoading && !user ? (
          <View style={styles.loading}>
            <ActivityIndicator size="small" color={colors.accent} />
          </View>
        ) : (
          <>
            <ProfileCard />
            <StatsGrid />
            <SessionList />

            <View style={styles.section}>
              <Pressable style={styles.aboutItem}>
                <Info size={20} color={colors.textLight} />
                <Text style={styles.aboutText}>关于我们</Text>
              </Pressable>
              <Pressable style={styles.aboutItem}>
                <FileText size={20} color={colors.textLight} />
                <Text style={styles.aboutText}>版本信息</Text>
                <Text style={styles.versionText}>v1.0.0</Text>
              </Pressable>
            </View>

            <Pressable style={styles.logoutButton} onPress={handleLogout}>
              <LogOut size={20} color="#fff" />
              <Text style={styles.logoutText}>退出登录</Text>
            </Pressable>
          </>
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
  section: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
    overflow: 'hidden',
  },
  aboutItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing[4],
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  aboutText: {
    flex: 1,
    fontSize: typography.textBase,
    color: colors.text,
    marginLeft: spacing[3],
  },
  versionText: {
    fontSize: typography.textBase,
    color: colors.textMuted,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: spacing[4],
    marginTop: spacing[6],
    height: 48,
    backgroundColor: colors.coral,
    borderRadius: 12,
  },
  logoutText: {
    fontSize: typography.textBase,
    fontWeight: typography.fontMedium,
    color: '#fff',
    marginLeft: spacing[2],
  },
});

export default ProfileScreen;

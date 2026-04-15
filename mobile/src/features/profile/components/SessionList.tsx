import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Monitor, Smartphone } from 'lucide-react-native';
import { Card } from '../../../components/ui/Card';
import { Badge } from '../../../components/ui/Badge';
import { colors, typography, spacing, elevation } from '../../../styles';
import { useProfileStore } from '../profileStore';

const getDeviceIcon = (device?: string) => {
  if (!device) return Monitor;
  const d = device.toLowerCase();
  if (
    d.includes('mobile') ||
    d.includes('iphone') ||
    d.includes('android') ||
    d.includes('ipad')
  ) {
    return Smartphone;
  }
  return Monitor;
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return date.toLocaleDateString('zh-CN');
};

export function SessionList() {
  const { sessions } = useProfileStore();

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <Text style={styles.title}>活跃会话</Text>
      <View style={styles.list}>
        {sessions.length === 0 ? (
          <Text style={styles.empty}>暂无活跃会话</Text>
        ) : (
          sessions.map((session) => {
            const DeviceIcon = getDeviceIcon(session.device);
            return (
              <View key={session.session_id} style={styles.item}>
                <View style={styles.deviceIcon}>
                  <DeviceIcon size={20} color={colors.accent} />
                </View>
                <View style={styles.info}>
                  <Text style={styles.deviceName}>{session.device || '未知设备'}</Text>
                  <Text style={styles.meta}>
                    {session.location || '未知位置'} • {formatTime(session.created_at)}
                  </Text>
                </View>
                {session.is_current && (
                  <Badge variant="info" style={styles.badge}>当前</Badge>
                )}
              </View>
            );
          })
        )}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  title: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[4],
  },
  list: {
    gap: spacing[3],
  },
  empty: {
    fontSize: typography.textBase,
    color: colors.textMuted,
    textAlign: 'center',
    paddingVertical: spacing[4],
  },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: elevation.radiusMd,
    padding: spacing[3],
  },
  deviceIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentLight,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing[3],
  },
  info: {
    flex: 1,
  },
  deviceName: {
    fontSize: typography.textBase,
    fontWeight: typography.fontMedium,
    color: colors.text,
    marginBottom: spacing[1],
  },
  meta: {
    fontSize: typography.textSm,
    color: colors.textLight,
  },
  badge: {
    marginLeft: spacing[2],
  },
});

export default SessionList;

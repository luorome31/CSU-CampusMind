import React from 'react';
import { View, Text, StyleSheet, Pressable, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { Card } from '../ui/Card';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList } from '../../navigation/types';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

export function HeroBanner() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <Card style={styles.card}>
      <View style={styles.content}>
        <Text style={styles.title}>CampusMind</Text>
        <Text style={styles.subtitle}>基于 RAG 与 Tool-calling 的智能校园助手。连接校园知识，赋能学习生活。✨</Text>
        <Pressable
          style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
          onPress={() =>
            navigation.navigate('ChatsTab', {
              screen: 'Chats',
              params: { dialogId: undefined },
            } as any)
          }
        >
          <Text style={styles.buttonText}>新建对话</Text>
        </Pressable>
      </View>
      <Image
        source={require('../../assets/csu-xiaotuanzi-dashboard.png')}
        style={styles.image}
        resizeMode="contain"
      />
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
    padding: spacing[5],
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    overflow: 'hidden',
  },
  content: {
    width: '62%',
    zIndex: 2,
  },
  title: {
    fontSize: 22,
    fontWeight: typography.fontBold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.textSm,
    color: colors.textLight,
    lineHeight: 20,
    marginBottom: spacing[4],
  },
  button: {
    backgroundColor: '#5A7F93',
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[4],
    borderRadius: 20,
    alignSelf: 'flex-start',
  },
  buttonPressed: {
    opacity: 0.8,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: typography.textSm,
    fontWeight: typography.fontMedium,
  },
  image: {
    width: 140,
    height: 140,
    position: 'absolute',
    right: 0,
    bottom: -10,
    zIndex: 1,
  },
});

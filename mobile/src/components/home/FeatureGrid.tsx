import React from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { BottomTabNavigationProp } from '@react-navigation/bottom-tabs';
import { BookOpen, FilePlus } from 'lucide-react-native';
import { colors, typography, spacing } from '../../styles';
import type { RootTabParamList } from '../../navigation/types';

type NavigationProp = BottomTabNavigationProp<RootTabParamList>;

export function FeatureGrid() {
  const navigation = useNavigation<NavigationProp>();

  return (
    <View style={styles.container}>
      <View style={styles.grid}>
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
          onPress={() => navigation.navigate('KnowledgeTab' as any)}
        >
          <View style={styles.iconContainer}>
            <BookOpen size={20} color={colors.accent} strokeWidth={2} />
          </View>
          <Text style={styles.cardText}>知识库</Text>
        </Pressable>
        
        <Pressable
          style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
          onPress={() => {
            navigation.getParent()?.navigate('HomeTab', {
              screen: 'KnowledgeBuild',
            });
          }}
        >
          <View style={styles.iconContainer}>
            <FilePlus size={20} color={colors.accent} strokeWidth={2} />
          </View>
          <Text style={styles.cardText}>知识构建</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginTop: spacing[6],
    paddingHorizontal: spacing[4],
  },
  grid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: spacing[3],
  },
  card: {
    flex: 1,
    backgroundColor: '#EAE5DB', 
    borderRadius: 16,
    padding: spacing[4],
    minHeight: 120,
    justifyContent: 'center',
  },
  cardPressed: {
    opacity: 0.8,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(83, 125, 150, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: spacing[3],
  },
  cardText: {
    fontSize: typography.textBase,
    color: colors.text,
    fontWeight: typography.fontMedium,
    marginTop: spacing[2],
  },
});

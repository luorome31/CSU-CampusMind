/**
 * Modal Component
 * A customizable modal dialog following the design system tokens
 */

import React from 'react';
import {
  Modal as RNModal,
  View,
  Text,
  Pressable,
  StyleSheet,
  ScrollView,
  SafeAreaView,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { colors, typography, spacing, elevation } from '../../../styles';

export interface ModalProps {
  /** Display state */
  visible: boolean;
  /** Close callback */
  onClose: () => void;
  /** Title text */
  title: string;
  /** Content */
  children: React.ReactNode;
  /** Additional modal container style */
  style?: ViewStyle;
}

/**
 * Modal Component
 */
export const Modal: React.FC<ModalProps> = ({
  visible,
  onClose,
  title,
  children,
  style,
}) => {
  return (
    <RNModal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Pressable style={styles.backdrop} onPress={onClose} testID="modal-backdrop">
        <SafeAreaView style={styles.safeArea}>
          <Pressable
            style={[styles.modalContainer, style]}
            onPress={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <View style={styles.header}>
              <Text style={styles.title}>{title}</Text>
              <Pressable
                style={styles.closeButton}
                onPress={onClose}
                accessibilityRole="button"
                accessibilityLabel="close"
              >
                <Text style={styles.closeIcon}>✕</Text>
              </Pressable>
            </View>

            {/* Content */}
            <ScrollView
              style={styles.content}
              contentContainerStyle={styles.contentContainer}
              showsVerticalScrollIndicator={false}
            >
              {children}
            </ScrollView>
          </Pressable>
        </SafeAreaView>
      </Pressable>
    </RNModal>
  );
};

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  safeArea: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  modalContainer: {
    backgroundColor: colors.backgroundCard,
    borderRadius: elevation.radiusLg,
    padding: spacing[4],
    width: '90%',
    maxWidth: 440,
    maxHeight: '80%',
  } as ViewStyle,
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing[4],
  } as ViewStyle,
  title: {
    fontSize: typography.textLg,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    flex: 1,
  } as TextStyle,
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.accentLight,
  } as ViewStyle,
  closeIcon: {
    fontSize: 16,
    color: colors.text,
    fontWeight: typography.fontMedium,
  } as TextStyle,
  content: {
    maxHeight: 400,
  } as ViewStyle,
  contentContainer: {
    paddingBottom: spacing[2],
  } as ViewStyle,
});

export default Modal;

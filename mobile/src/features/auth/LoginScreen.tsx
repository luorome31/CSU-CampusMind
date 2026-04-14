/**
 * LoginScreen - 登录页面
 * 参考 Web 端 LoginPage.tsx 实现
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useAuthStore } from './authStore';
import { colors, typography, spacing } from '../../styles';

export function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const login = useAuthStore((s) => s.login);
  const isLoading = useAuthStore((s) => s.isLoading);

  const handleSubmit = async () => {
    setError('');
    try {
      await login(username, password);
      // Navigation will be handled by RootNavigator state change
    } catch (e: any) {
      console.error('[LoginScreen] 登录遇到未捕获异常:', e?.message || e);
      setError('登录失败，请检查学号和密码');
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Decorative leaves */}
        <View style={styles.leavesContainer}>
          <Text style={styles.leaf1}>🍃</Text>
          <Text style={styles.leaf2}>🍃</Text>
          <Text style={styles.leaf3}>🍂</Text>
          <Text style={styles.leaf4}>🍃</Text>
        </View>

        <Text style={styles.compassDecoration}>🧭</Text>

        {/* Login Card */}
        <View style={styles.card}>
          {/* Header */}
          <View style={styles.header}>
            <View style={styles.logoContainer}>
              <Text style={styles.logoEmoji}>🎓</Text>
            </View>
            <Text style={styles.title}>CampusMind</Text>
            <Text style={styles.subtitle}>
              欢迎回来{'\n'}请使用中南大学统一身份认证登录
            </Text>
          </View>

          {/* Form */}
          <View style={styles.form}>
            {/* Username */}
            <View style={styles.inputField}>
              <Text style={styles.label}>学号</Text>
              <View style={styles.inputWithIcon}>
                <Text style={styles.inputIcon}>👤</Text>
                <TextInput
                  style={styles.input}
                  value={username}
                  onChangeText={setUsername}
                  placeholder="请输入学号"
                  placeholderTextColor={colors.textMuted}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
              </View>
            </View>

            {/* Password */}
            <View style={styles.inputField}>
              <Text style={styles.label}>密码</Text>
              <View style={styles.inputWithIcon}>
                <Text style={styles.inputIcon}>🔒</Text>
                <TextInput
                  style={styles.input}
                  value={password}
                  onChangeText={setPassword}
                  placeholder="请输入密码"
                  placeholderTextColor={colors.textMuted}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                />
                <TouchableOpacity
                  style={styles.passwordToggle}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Text>{showPassword ? '👁️' : '👁️‍🗨️'}</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* Error */}
            {error ? <Text style={styles.error}>{error}</Text> : null}

            {/* Submit */}
            <TouchableOpacity
              style={[styles.button, isLoading && styles.buttonDisabled]}
              onPress={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.buttonText}>登录</Text>
              )}
            </TouchableOpacity>
          </View>

          {/* Footer */}
          <View style={styles.footer}>
            <Text style={styles.footerText}>
              © 2026 CampusMind · 中南大学智能校园助手
            </Text>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing[4],
  },
  leavesContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 0,
  },
  leaf1: { position: 'absolute', top: '10%', left: '10%', fontSize: 24, opacity: 0.6 },
  leaf2: { position: 'absolute', top: '20%', right: '15%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '45deg' }] },
  leaf3: { position: 'absolute', bottom: '15%', left: '15%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '-30deg' }] },
  leaf4: { position: 'absolute', bottom: '25%', right: '10%', fontSize: 24, opacity: 0.6, transform: [{ rotate: '15deg' }] },
  compassDecoration: {
    position: 'absolute',
    bottom: '10%',
    left: '5%',
    fontSize: 40,
    opacity: 0.3,
    transform: [{ rotate: '-15deg' }],
  },
  card: {
    width: '100%',
    maxWidth: 440,
    backgroundColor: colors.backgroundCard,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing[5],
    zIndex: 1,
    shadowColor: colors.shadow,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing[6],
  },
  logoContainer: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 20,
    marginBottom: spacing[3],
  },
  logoEmoji: { fontSize: 42 },
  title: {
    fontSize: 24,
    fontWeight: typography.fontSemibold,
    color: colors.text,
    marginBottom: spacing[2],
  },
  subtitle: {
    fontSize: typography.textSm,
    color: colors.textLight,
    textAlign: 'center',
    lineHeight: typography.textSm * typography.leadingRelaxed,
  },
  form: {
    gap: spacing[5],
  },
  inputField: {
    gap: spacing[2],
  },
  label: {
    fontSize: 13,
    fontWeight: typography.fontMedium,
    color: colors.textLight,
  },
  inputWithIcon: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderWidth: 1.5,
    borderColor: colors.border,
    borderRadius: 10,
    paddingHorizontal: spacing[3],
  },
  inputIcon: {
    fontSize: 18,
    marginRight: spacing[2],
  },
  input: {
    flex: 1,
    height: 44,
    fontSize: 15,
    color: colors.text,
  },
  passwordToggle: {
    padding: spacing[1],
  },
  error: {
    color: colors.coral,
    fontSize: 13,
    textAlign: 'center',
  },
  button: {
    backgroundColor: colors.accent,
    height: 48,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: spacing[2],
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: typography.textBase,
    fontWeight: typography.fontMedium,
  },
  footer: {
    marginTop: spacing[8],
    paddingTop: spacing[4],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 11,
    color: colors.textMuted,
  },
});

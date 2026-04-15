// mobile/src/features/profile/components/ProfileCard.tsx
import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable, TextInput } from 'react-native';
import { Camera, Check, X } from 'lucide-react-native';
import { Card } from '../../../components/ui/Card';
import { colors, typography, spacing, elevation } from '../../../styles';
import { useProfileStore } from '../profileStore';

export function ProfileCard() {
  const { user, updateProfile, isLoading } = useProfileStore();
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState('');

  if (!user) return null;

  const handleStartEdit = (field: string, value: string) => {
    setEditingField(field);
    setEditValue(value || '');
  };

  const handleSave = async () => {
    if (!editingField) return;
    await updateProfile({ [editingField]: editValue });
    setEditingField(null);
  };

  const handleCancel = () => {
    setEditingField(null);
    setEditValue('');
  };

  const renderField = (
    label: string,
    field: string,
    value: string | null | undefined,
    editable: boolean = true
  ) => (
    <View style={styles.field}>
      <Text style={styles.fieldLabel}>{label}</Text>
      {editingField === field ? (
        <View style={styles.fieldEdit}>
          <TextInput
            style={styles.input}
            value={editValue}
            onChangeText={setEditValue}
            autoFocus
          />
          <Pressable onPress={handleSave} disabled={isLoading} style={styles.iconButton}>
            <Check size={18} color={colors.success} />
          </Pressable>
          <Pressable onPress={handleCancel} style={styles.iconButton}>
            <X size={18} color={colors.error} />
          </Pressable>
        </View>
      ) : (
        <Pressable
          style={styles.fieldDisplay}
          onPress={() => editable && handleStartEdit(field, value || '')}
          disabled={!editable}
        >
          <Text style={[styles.fieldValue, !editable && styles.fieldReadonly]}>
            {value || '未设置'}
          </Text>
          {editable && <Text style={styles.editHint}>点击编辑</Text>}
        </Pressable>
      )}
    </View>
  );

  return (
    <Card variant="elevated" padding="md" style={styles.card}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <View style={styles.avatarPlaceholder}>
            <Text style={styles.avatarText}>
              {(user.display_name || user.username || 'U').charAt(0).toUpperCase()}
            </Text>
          </View>
          <Pressable style={styles.avatarUpload}>
            <Camera size={14} color="#fff" />
          </Pressable>
        </View>
        <View style={styles.nameSection}>
          {renderField('显示名称', 'display_name', user.display_name)}
          {renderField('用户名', 'username', user.username, false)}
        </View>
      </View>
      <View style={styles.fields}>
        {renderField('邮箱', 'email', user.email)}
        {renderField('手机号', 'phone', user.phone)}
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing[4],
    marginTop: spacing[4],
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[4],
  },
  avatar: {
    width: 64,
    height: 64,
    marginRight: spacing[4],
  },
  avatarPlaceholder: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
  },
  avatarText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: typography.fontBold,
  },
  avatarUpload: {
    position: 'absolute',
    right: 0,
    bottom: 0,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  nameSection: {
    flex: 1,
  },
  fields: {
    gap: spacing[3],
  },
  field: {
    marginBottom: spacing[2],
  },
  fieldLabel: {
    fontSize: typography.textSm,
    color: colors.textLight,
    marginBottom: spacing[1],
  },
  fieldDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  fieldValue: {
    fontSize: typography.textBase,
    color: colors.text,
  },
  fieldReadonly: {
    color: colors.textMuted,
  },
  editHint: {
    fontSize: typography.textSm,
    color: colors.accent,
    marginLeft: spacing[2],
  },
  fieldEdit: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    height: 40,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: elevation.radiusMd,
    paddingHorizontal: spacing[3],
    fontSize: typography.textBase,
    color: colors.text,
    backgroundColor: colors.background,
  },
  iconButton: {
    padding: spacing[2],
    marginLeft: spacing[1],
  },
});

export default ProfileCard;

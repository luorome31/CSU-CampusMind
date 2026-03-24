import { useState } from 'react';
import { Camera, Check, X } from 'lucide-react';
import { profileStore } from '../profileStore';
import './ProfileCard.css';

export function ProfileCard() {
  const { user, updateProfile, isLoading } = profileStore();
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

  return (
    <div className="profile-card">
      <div className="profile-avatar-section">
        <div className="profile-avatar">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt={user.display_name || user.username} />
          ) : (
            <div className="profile-avatar-placeholder">
              {(user.display_name || user.username).charAt(0).toUpperCase()}
            </div>
          )}
          <button className="profile-avatar-upload" aria-label="上传头像">
            <Camera size={16} />
          </button>
        </div>
      </div>

      <div className="profile-info">
        <div className="profile-field">
          <label>显示名称</label>
          {editingField === 'display_name' ? (
            <div className="profile-field-edit">
              <input
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading} aria-label="保存">
                <Check size={16} />
              </button>
              <button onClick={handleCancel} aria-label="取消">
                <X size={16} />
              </button>
            </div>
          ) : (
            <div
              className="profile-field-display"
              onClick={() => handleStartEdit('display_name', user.display_name || '')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleStartEdit('display_name', user.display_name || '')}
            >
              {user.display_name || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>

        <div className="profile-field">
          <label>用户名</label>
          <div className="profile-field-display readonly">{user.username}</div>
        </div>

        <div className="profile-field">
          <label>邮箱</label>
          {editingField === 'email' ? (
            <div className="profile-field-edit">
              <input
                type="email"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading} aria-label="保存">
                <Check size={16} />
              </button>
              <button onClick={handleCancel} aria-label="取消">
                <X size={16} />
              </button>
            </div>
          ) : (
            <div
              className="profile-field-display"
              onClick={() => handleStartEdit('email', user.email || '')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleStartEdit('email', user.email || '')}
            >
              {user.email || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>

        <div className="profile-field">
          <label>手机号</label>
          {editingField === 'phone' ? (
            <div className="profile-field-edit">
              <input
                type="tel"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
              />
              <button onClick={handleSave} disabled={isLoading} aria-label="保存">
                <Check size={16} />
              </button>
              <button onClick={handleCancel} aria-label="取消">
                <X size={16} />
              </button>
            </div>
          ) : (
            <div
              className="profile-field-display"
              onClick={() => handleStartEdit('phone', user.phone || '')}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleStartEdit('phone', user.phone || '')}
            >
              {user.phone || '未设置'} <span className="edit-hint">点击编辑</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

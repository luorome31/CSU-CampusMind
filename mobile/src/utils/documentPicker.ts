/**
 * 文档选择工具
 * 使用 react-native-document-picker 调起系统文件管理器选择文档
 */

import { pick, types } from 'react-native-document-picker';

export interface DocumentPickResult {
  uri: string;
  name: string;
  size: number;
}

/**
 * 调起文件管理器选择文档
 * @returns 返回包含 uri, name, size 的对象；用户取消时返回 null
 */
export async function pickDocument(): Promise<DocumentPickResult | null> {
  try {
    const result = await pick({
      allowMultiSelection: false,
      type: [types.allFiles],
    });

    if (!result || result.length === 0) {
      return null;
    }

    const file = result[0];

    return {
      uri: file.uri,
      name: file.name ?? 'unknown',
      size: file.size ?? 0,
    };
  } catch (error: unknown) {
    // 用户取消时抛出 CancelError
    if (error instanceof Error && error.name === 'CancelError') {
      return null;
    }
    throw error;
  }
}

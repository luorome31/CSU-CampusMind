/**
 * 图片选择工具函数
 * 封装 react-native-image-picker，提供统一调用方式
 */

import { launchImageLibrary, launchCamera, ImagePickerResponse, Asset } from 'react-native-image-picker';

export interface ImagePickerResult {
  uri: string;
  width: number;
  height: number;
}

/**
 * 从相册选择图片
 * @returns 返回包含 uri, width, height 的对象，或用户取消时返回 null
 */
export const pickImage = async (): Promise<ImagePickerResult | null> => {
  return new Promise((resolve) => {
    launchImageLibrary(
      {
        mediaType: 'photo',
        selectionLimit: 1,
        includeBase64: false,
        quality: 1,
      },
      (response: ImagePickerResponse) => {
        if (response.didCancel) {
          resolve(null);
          return;
        }

        if (response.errorCode) {
          console.error('Image picker error:', response.errorMessage);
          resolve(null);
          return;
        }

        const asset: Asset | undefined = response.assets?.[0];
        if (asset && asset.uri && asset.width && asset.height) {
          resolve({
            uri: asset.uri,
            width: asset.width,
            height: asset.height,
          });
        } else {
          resolve(null);
        }
      }
    );
  });
};

/**
 * 调起相机拍照
 * @returns 返回包含 uri, width, height 的对象，或用户取消时返回 null
 */
export const takePhoto = async (): Promise<ImagePickerResult | null> => {
  return new Promise((resolve) => {
    launchCamera(
      {
        mediaType: 'photo',
        saveToPhotos: false,
        includeBase64: false,
        quality: 1,
      },
      (response: ImagePickerResponse) => {
        if (response.didCancel) {
          resolve(null);
          return;
        }

        if (response.errorCode) {
          console.error('Camera error:', response.errorMessage);
          resolve(null);
          return;
        }

        const asset: Asset | undefined = response.assets?.[0];
        if (asset && asset.uri && asset.width && asset.height) {
          resolve({
            uri: asset.uri,
            width: asset.width,
            height: asset.height,
          });
        } else {
          resolve(null);
        }
      }
    );
  });
};

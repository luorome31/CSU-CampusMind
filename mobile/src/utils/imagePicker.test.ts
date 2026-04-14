/**
 * imagePicker 工具函数测试
 */

import { describe, it, expect, jest, beforeEach } from '@jest/globals';

// Mock response types
interface MockAsset {
  uri?: string;
  width?: number;
  height?: number;
  type?: string;
  fileName?: string;
}

interface MockImagePickerResponse {
  didCancel?: boolean;
  errorCode?: string;
  errorMessage?: string;
  assets?: MockAsset[];
}

// Store mock implementations
let mockLaunchImageLibrary: ReturnType<typeof jest.fn>;
let mockLaunchCamera: ReturnType<typeof jest.fn>;

describe('imagePicker', () => {
  beforeEach(() => {
    jest.resetModules();

    mockLaunchImageLibrary = jest.fn();
    mockLaunchCamera = jest.fn();

    jest.doMock('react-native-image-picker', () => ({
      launchImageLibrary: mockLaunchImageLibrary,
      launchCamera: mockLaunchCamera,
      ImagePickerResponse: {},
    }));
  });

  describe('pickImage', () => {
    it('should return image data when image is selected', async () => {
      const { pickImage } = require('./imagePicker');

      const mockAsset: MockAsset = {
        uri: 'file:///test/image.jpg',
        width: 1920,
        height: 1080,
        type: 'image/jpeg',
        fileName: 'image.jpg',
      };

      (mockLaunchImageLibrary as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ assets: [mockAsset] });
      });

      const result = await pickImage();

      expect(result).toEqual({
        uri: 'file:///test/image.jpg',
        width: 1920,
        height: 1080,
      });
    });

    it('should return null when user cancels selection', async () => {
      const { pickImage } = require('./imagePicker');

      (mockLaunchImageLibrary as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ didCancel: true });
      });

      const result = await pickImage();

      expect(result).toBeNull();
    });

    it('should return null when there is an error', async () => {
      const { pickImage } = require('./imagePicker');

      (mockLaunchImageLibrary as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ errorCode: 'ERROR', errorMessage: 'Test error' });
      });

      const result = await pickImage();

      expect(result).toBeNull();
    });

    it('should return null when no asset is returned', async () => {
      const { pickImage } = require('./imagePicker');

      (mockLaunchImageLibrary as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ assets: [] });
      });

      const result = await pickImage();

      expect(result).toBeNull();
    });

    it('should return null when asset is missing required fields', async () => {
      const { pickImage } = require('./imagePicker');

      const mockAsset: MockAsset = {
        uri: 'file:///test/image.jpg',
        // missing width and height
      };

      (mockLaunchImageLibrary as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ assets: [mockAsset] });
      });

      const result = await pickImage();

      expect(result).toBeNull();
    });
  });

  describe('takePhoto', () => {
    it('should return image data when photo is taken', async () => {
      const { takePhoto } = require('./imagePicker');

      const mockAsset: MockAsset = {
        uri: 'file:///test/photo.jpg',
        width: 4032,
        height: 3024,
        type: 'image/jpeg',
        fileName: 'photo.jpg',
      };

      (mockLaunchCamera as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ assets: [mockAsset] });
      });

      const result = await takePhoto();

      expect(result).toEqual({
        uri: 'file:///test/photo.jpg',
        width: 4032,
        height: 3024,
      });
    });

    it('should return null when user cancels camera', async () => {
      const { takePhoto } = require('./imagePicker');

      (mockLaunchCamera as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ didCancel: true });
      });

      const result = await takePhoto();

      expect(result).toBeNull();
    });

    it('should return null when there is a camera error', async () => {
      const { takePhoto } = require('./imagePicker');

      (mockLaunchCamera as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ errorCode: 'CAMERA_ERROR', errorMessage: 'Camera not available' });
      });

      const result = await takePhoto();

      expect(result).toBeNull();
    });

    it('should return null when no asset is returned from camera', async () => {
      const { takePhoto } = require('./imagePicker');

      (mockLaunchCamera as any).mockImplementation((_options: any, callback: (response: MockImagePickerResponse) => void) => {
        callback({ assets: undefined });
      });

      const result = await takePhoto();

      expect(result).toBeNull();
    });
  });
});

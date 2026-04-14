import { pickDocument } from '../documentPicker';
import { pick, types } from 'react-native-document-picker';

jest.mock('react-native-document-picker', () => ({
  pick: jest.fn(),
  types: {
    allFiles: 'allFiles',
    images: 'images',
    videos: 'videos',
    audio: 'audio',
  },
}));

describe('pickDocument', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should return document info when user selects a file', async () => {
    const mockResult = {
      uri: 'file:///path/to/document.pdf',
      name: 'document.pdf',
      displayName: 'document.pdf',
      size: 1024,
      type: 'application/pdf',
    };

    (pick as jest.Mock).mockResolvedValueOnce([mockResult]);

    const result = await pickDocument();

    expect(result).toEqual({
      uri: mockResult.uri,
      name: mockResult.displayName,
      size: mockResult.size,
    });
    expect(pick).toHaveBeenCalledWith({
      allowMultiSelection: false,
      type: [types.allFiles],
    });
  });

  it('should return null when user cancels the picker', async () => {
    const error = new Error('User canceled');
    error.name = 'CancelError';
    (pick as jest.Mock).mockRejectedValueOnce(error);

    const result = await pickDocument();

    expect(result).toBeNull();
  });

  it('should return null for CancelError with different message', async () => {
    const error = new Error('The user cancelled the operation');
    error.name = 'CancelError';
    (pick as jest.Mock).mockRejectedValueOnce(error);

    const result = await pickDocument();

    expect(result).toBeNull();
  });

  it('should propagate non-cancel errors', async () => {
    const error = new Error('Permission denied');
    (pick as jest.Mock).mockRejectedValueOnce(error);

    await expect(pickDocument()).rejects.toThrow('Permission denied');
  });

  it('should handle documents without size property', async () => {
    const mockResult = {
      uri: 'file:///path/to/document.pdf',
      name: 'document.pdf',
      displayName: 'document.pdf',
      type: 'application/pdf',
    };

    (pick as jest.Mock).mockResolvedValueOnce([mockResult]);

    const result = await pickDocument();

    expect(result).toEqual({
      uri: mockResult.uri,
      name: mockResult.displayName,
      size: 0,
    });
  });
});

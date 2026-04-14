// mobile/src/api/__tests__/dialog.test.ts
import { listDialogs, deleteDialog } from '../dialog';

describe('dialog API', () => {
  it('should be defined', () => {
    expect(listDialogs).toBeDefined();
    expect(deleteDialog).toBeDefined();
  });
});

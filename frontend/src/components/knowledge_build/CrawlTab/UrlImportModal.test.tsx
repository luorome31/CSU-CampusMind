import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UrlImportModal } from './UrlImportModal';
import { buildStore } from '../../../features/build/buildStore';

describe('UrlImportModal', () => {
  beforeEach(() => {
    buildStore.setState({ isImportModalOpen: false, previewUrls: [] });
  });

  it('should not render when closed', () => {
    render(<UrlImportModal />);
    expect(screen.queryByText(/批量导入URL/)).not.toBeInTheDocument();
  });

  it('should render when opened', () => {
    buildStore.setState({ isImportModalOpen: true });
    render(<UrlImportModal />);
    expect(screen.getByText(/批量导入URL/)).toBeInTheDocument();
  });

  it('should show drag and drop zone', () => {
    buildStore.setState({ isImportModalOpen: true });
    render(<UrlImportModal />);
    expect(screen.getByText(/点击上传文件/)).toBeInTheDocument();
  });
});

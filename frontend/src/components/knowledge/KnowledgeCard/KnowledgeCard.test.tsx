import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { KnowledgeCard } from './KnowledgeCard';

describe('KnowledgeCard', () => {
  const mockKB = {
    id: 'kb1',
    name: 'Test Knowledge Base',
    description: 'This is a test knowledge base',
  };

  it('renders KB name and description', () => {
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={() => {}} />);
    expect(screen.getByText('Test Knowledge Base')).toBeInTheDocument();
    expect(screen.getByText('This is a test knowledge base')).toBeInTheDocument();
  });

  it('renders file count badge', () => {
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={() => {}} />);
    expect(screen.getByText('5 个文件')).toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    const handleClick = vi.fn();
    render(<KnowledgeCard knowledge={mockKB} fileCount={5} onClick={handleClick} />);
    screen.getByText('Test Knowledge Base').click();
    expect(handleClick).toHaveBeenCalled();
  });
});

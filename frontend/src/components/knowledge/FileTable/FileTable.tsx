import { Badge } from '../../ui';
import type { KnowledgeFile } from '../../../api/knowledge';
import './FileTable.css';

export interface FileTableProps {
  files: KnowledgeFile[];
  onFileClick: (file: KnowledgeFile) => void;
}

const STATUS_LABELS: Record<KnowledgeFile['status'], string> = {
  process: '处理中',
  indexing: '索引中',
  success: '成功',
  verified: '已验证',
  indexed: '已索引',
  fail: '失败',
  pending_verify: '待验证',
};

const STATUS_VARIANT: Record<KnowledgeFile['status'], 'accent' | 'warm' | 'success' | 'error'> = {
  process: 'accent',
  indexing: 'accent',
  success: 'success',
  verified: 'success',
  indexed: 'success',
  fail: 'error',
  pending_verify: 'warm',
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateStr: string): string {
  return dateStr.split('T')[0];
}

export function FileTable({ files, onFileClick }: FileTableProps) {
  if (files.length === 0) {
    return <div className="file-table-empty">暂无文件</div>;
  }

  return (
    <div className="file-table-wrapper">
      <table className="file-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>状态</th>
            <th>大小</th>
            <th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr
              key={file.id}
              className="file-table-row"
              onClick={() => onFileClick(file)}
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onFileClick(file)}
            >
              <td className="file-table-name">{file.file_name}</td>
              <td className="file-table-status">
                <Badge variant={STATUS_VARIANT[file.status]} size="sm">
                  {STATUS_LABELS[file.status]}
                </Badge>
              </td>
              <td className="file-table-size">{formatFileSize(file.file_size)}</td>
              <td className="file-table-date">{formatDate(file.update_time)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

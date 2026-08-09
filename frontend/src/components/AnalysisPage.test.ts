import { describe, expect, it } from 'vitest';
import { latestPublishedWorkflows } from './AnalysisPage';
import type { WorkflowRecord } from '../types';

function workflow(id: string, name: string, version: number): WorkflowRecord {
  return {
    id,
    version,
    published_version_id: `${id}-published`,
    definition: { name, description: '', nodes: [], edges: [] },
  };
}

describe('latestPublishedWorkflows', () => {
  it('shows only the newest published version for a repeated workflow name', () => {
    const result = latestPublishedWorkflows([
      workflow('old', 'Complete stock decision workflow', 1),
      workflow('new', 'Complete stock decision workflow', 2),
      workflow('other', 'Research workflow', 1),
    ]);

    expect(result).toHaveLength(2);
    expect(result.find(item => item.definition.name.startsWith('Complete'))?.id).toBe('new');
  });
});

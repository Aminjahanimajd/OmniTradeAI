import { describe, expect, it } from 'vitest';
import { optionControlMode, providerRoles } from './AnalysisPage';
import { activeWorkflow } from '../workflows';
import type { WorkflowRecord } from '../types';

function workflow(id: string, name: string, version: number): WorkflowRecord {
  return {
    id,
    version,
    published_version_id: `${id}-published`,
    definition: { name, description: '', nodes: [], edges: [] },
  };
}

describe('activeWorkflow', () => {
  it('uses the latest published Workflow Lab record', () => {
    const result = activeWorkflow([
      workflow('old', 'Complete stock decision workflow', 1),
      workflow('new', 'Complete stock decision workflow', 2),
      workflow('other', 'Research workflow', 1),
    ]);
    expect(result?.id).toBe('new');
  });

  it('keeps the newest draft active until it is published', () => {
    const draft = workflow('draft', 'Complete stock decision workflow', 3);
    delete draft.published_version_id;
    expect(activeWorkflow([workflow('published', 'Complete stock decision workflow', 2), draft])?.id).toBe('draft');
  });
});

describe('optionControlMode', () => {
  it('never renders a useless one-option selector', () => {
    expect(optionControlMode([])).toBe('empty');
    expect(optionControlMode(['only'])).toBe('fixed');
    expect(optionControlMode(['first', 'second'])).toBe('select');
  });

  it('maps every verified provider only to its supported data roles', () => {
    const roles = providerRoles({
      tickers: [], quick_models: [], deep_models: [], languages: [], currencies: [], data_modes: [],
      model_providers: [], provider_models: {}, data_providers: ['fred', 'polymarket', 'yfinance'],
      data_provider_labels: { fred: 'FRED', polymarket: 'Polymarket', yfinance: 'Yahoo Finance' },
      data_provider_capabilities: { fred: ['macro'], polymarket: ['macro', 'prediction_markets'], yfinance: ['market', 'fundamentals', 'news', 'sentiment'] },
    });
    expect(roles.find(item => item.name === 'fred')?.capabilities).toEqual(['macro']);
    expect(roles.find(item => item.name === 'polymarket')?.capabilities).toContain('macro');
    expect(roles.find(item => item.name === 'yfinance')?.capabilities).not.toContain('macro');
  });
});

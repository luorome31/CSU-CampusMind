import { describe, it, expect } from 'vitest';
import { parseSSELines } from './parseSSELines';

describe('parseSSELines', () => {
  it('yields events from valid SSE data lines', () => {
    const input = 'data: {"type":"event","data":{"status":"START","title":"Test"}}\n';
    const events = [...parseSSELines(input)];

    expect(events).toHaveLength(1);
    expect(events[0]).toEqual({
      type: 'event',
      data: { status: 'START', title: 'Test' },
      timestamp: undefined,
    });
  });

  it('yields multiple events from multiple data lines', () => {
    const input = [
      'data: {"type":"event","data":{"status":"START","title":"Query"}}',
      'data: {"type":"response_chunk","data":{"chunk":"Hello"}}',
    ].join('\n');

    const events = [...parseSSELines(input)];
    expect(events).toHaveLength(2);
    expect(events[0].type).toBe('event');
    expect(events[1].type).toBe('response_chunk');
  });

  it('extracts timestamp when present', () => {
    const input = 'data: {"type":"event","data":{},"timestamp":1234567890}';
    const events = [...parseSSELines(input)];

    expect(events[0].timestamp).toBe(1234567890);
  });

  it('skips empty lines', () => {
    const input = [
      'data: {"type":"event","data":{}}',
      '',
      'data: {"type":"event","data":{}}',
    ].join('\n');

    const events = [...parseSSELines(input)];
    expect(events).toHaveLength(2);
  });

  it('skips lines without data: prefix', () => {
    const input = [
      'data: {"type":"event","data":{}}',
      'event: custom',
      'data: {"type":"event","data":{}}',
    ].join('\n');

    const events = [...parseSSELines(input)];
    expect(events).toHaveLength(2);
  });

  it('skips malformed JSON', () => {
    const input = [
      'data: {"type":"event","data":{}}',
      'data: not valid json',
      'data: {"type":"event","data":{}}',
    ].join('\n');

    const events = [...parseSSELines(input)];
    expect(events).toHaveLength(2);
  });

  it('handles mixed whitespace', () => {
    const input = '  data: {"type":"event","data":{}}  \n';
    const events = [...parseSSELines(input)];
    expect(events).toHaveLength(1);
  });

  it('handles empty input', () => {
    const events = [...parseSSELines('')];
    expect(events).toHaveLength(0);
  });

  it('parses complex nested data', () => {
    const input = 'data: {"type":"response_chunk","data":{"chunk":"Hello","accumulated":"Hello World"}}';
    const events = [...parseSSELines(input)];

    expect(events[0]).toEqual({
      type: 'response_chunk',
      data: { chunk: 'Hello', accumulated: 'Hello World' },
      timestamp: undefined,
    });
  });
});

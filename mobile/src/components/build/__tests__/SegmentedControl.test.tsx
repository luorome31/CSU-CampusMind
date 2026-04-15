import React from 'react';
import { render, fireEvent } from '@testing-library/react-native';
import { SegmentedControl } from '../SegmentedControl';

describe('SegmentedControl', () => {
  it('should render two tabs', () => {
    const { getByText } = render(
      <SegmentedControl
        options={[
          { value: 'crawl', label: '爬取任务' },
          { value: 'review', label: '审核队列' },
        ]}
        value="crawl"
        onChange={() => {}}
      />
    );

    expect(getByText('爬取任务')).toBeTruthy();
    expect(getByText('审核队列')).toBeTruthy();
  });

  it('should call onChange with correct value when tab clicked', () => {
    const onChange = jest.fn();
    const { getByText } = render(
      <SegmentedControl
        options={[
          { value: 'crawl', label: '爬取任务' },
          { value: 'review', label: '审核队列' },
        ]}
        value="crawl"
        onChange={onChange}
      />
    );

    fireEvent.press(getByText('审核队列'));
    expect(onChange).toHaveBeenCalledWith('review');
  });
});

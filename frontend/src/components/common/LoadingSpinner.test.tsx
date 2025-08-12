import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByLabelText('Loading');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with custom size', () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('h-12', 'w-12');
  });

  it('renders with custom color', () => {
    const { container } = render(<LoadingSpinner color="gray" />);
    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('text-gray-600');
  });

  it('renders with text', () => {
    render(<LoadingSpinner text="Loading chapters..." />);
    expect(screen.getByText('Loading chapters...')).toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const sizes = ['sm', 'md', 'lg', 'xl'] as const;
    const expectedClasses = ['h-4 w-4', 'h-8 w-8', 'h-12 w-12', 'h-16 w-16'];
    
    sizes.forEach((size, index) => {
      const { container } = render(<LoadingSpinner size={size} />);
      const svg = container.querySelector('svg');
      const classes = expectedClasses[index].split(' ');
      classes.forEach(cls => {
        expect(svg).toHaveClass(cls);
      });
    });
  });
});
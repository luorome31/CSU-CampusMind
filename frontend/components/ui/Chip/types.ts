import { LucideIcon } from 'lucide-react';

export type ChipVariant = 'default' | 'active' | 'disabled';
export type ChipSize = 'sm' | 'md';

export interface ChipProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ChipVariant;
  size?: ChipSize;
  icon?: LucideIcon;
  children: React.ReactNode;
}

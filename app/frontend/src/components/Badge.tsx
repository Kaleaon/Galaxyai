import type { PropsWithChildren } from 'react';

type BadgeTone = 'neutral' | 'success' | 'warn' | 'danger' | 'info';

const toneClass: Record<BadgeTone, string> = {
  neutral: 'badge badge-neutral',
  success: 'badge badge-success',
  warn: 'badge badge-warn',
  danger: 'badge badge-danger',
  info: 'badge badge-info',
};

interface BadgeProps {
  tone?: BadgeTone;
}

export function Badge({ tone = 'neutral', children }: PropsWithChildren<BadgeProps>) {
  return <span className={toneClass[tone]}>{children}</span>;
}

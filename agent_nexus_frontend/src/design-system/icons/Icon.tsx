import * as React from 'react';
import { Icons, Icon } from '../icons';
import { cn } from '@/lib/utils';
import { LucideProps } from 'lucide-react';

interface IconComponentProps extends LucideProps {
  name: keyof typeof Icons;
  className?: string;
}

export const IconComponent: React.FC<IconComponentProps> = ({ 
  name, 
  className, 
  ...props 
}) => {
  const IconToRender = Icons[name] as Icon;
  
  if (!IconToRender) {
    // Fallback to a warning icon if the specified name is invalid
    return <Icons.warning className={cn('text-status-error', className)} {...props} />;
  }

  return (
    <IconToRender 
      className={cn('shrink-0', className)} 
      aria-hidden="true" 
      {...props} 
    />
  );
};
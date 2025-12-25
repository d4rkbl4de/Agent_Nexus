import * as React from 'react';
import * as ReactDOM from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import { assertExists } from '../../utils/assert';
import Button from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  isCloseable?: boolean;
}

const sizeMap: Record<Required<ModalProps>['size'], string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
};

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  isCloseable = true,
}) => {
  const modalRef = React.useRef<HTMLDivElement>(null);
  const portalRoot = React.useMemo(() => document.body, []);
  
  // Trap focus within the modal when open
  const handleKeyDown = React.useCallback((event: KeyboardEvent) => {
    if (!isOpen || !modalRef.current) return;

    if (event.key === 'Escape' && isCloseable) {
      onClose();
      return;
    }

    if (event.key === 'Tab') {
      const focusableElements = modalRef.current.querySelectorAll(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      );
      
      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement.focus();
          event.preventDefault();
        }
      } else {
        if (document.activeElement === lastElement) {
          firstElement.focus();
          event.preventDefault();
        }
      }
    }
  }, [isOpen, onClose, isCloseable]);

  // Handle focus and body scroll lock
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
      
      // Focus the modal content for screen readers
      const focusTimeout = setTimeout(() => {
        if (modalRef.current) {
          modalRef.current.focus();
        }
      }, 0);

      return () => {
        clearTimeout(focusTimeout);
        document.body.style.overflow = '';
        window.removeEventListener('keydown', handleKeyDown);
      };
    } else {
      document.body.style.overflow = '';
      window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  const modalContent = (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[1000] flex items-center justify-center">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm"
            onClick={isCloseable ? onClose : undefined}
            aria-hidden="true"
          />

          {/* Modal Content */}
          <motion.div
            ref={modalRef}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby={`${title.toLowerCase().replace(/\s/g, '-')}-title`}
            tabIndex={-1} // Makes the modal container focusable
            className={`bg-white rounded-xl shadow-2xl relative z-10 mx-4 w-full ${sizeMap[size]}`}
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 id={`${title.toLowerCase().replace(/\s/g, '-')}-title`} className="text-xl font-semibold text-gray-900 truncate">
                {title}
              </h2>
              {isCloseable && (
                <Button
                  onClick={onClose}
                  variant="ghost"
                  size="icon"
                  aria-label="Close modal"
                >
                  <X className="w-5 h-5" />
                </Button>
              )}
            </div>

            {/* Body */}
            <div className="p-6 overflow-y-auto max-h-[70vh]">
              {children}
            </div>
            
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );

  assertExists(portalRoot, 'Document body must exist for portal creation.');
  return ReactDOM.createPortal(modalContent, portalRoot);
};

export default Modal;
export class NexusAssertionError extends Error {
  constructor(message: string) {
    super(`Nexus Assertion Failed: ${message}`);
    this.name = 'NexusAssertionError';
    
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, NexusAssertionError);
    }
  }
}

export function assert(
  condition: unknown,
  message: string = 'Condition must be truthy.'
): asserts condition {
  if (process.env.NODE_ENV !== 'production') {
    if (!condition) {
      throw new NexusAssertionError(message);
    }
  }
}

export function assertExists<T>(
  value: T,
  message: string = 'Value must exist (non-null and non-undefined).'
): asserts value is NonNullable<T> {
  if (process.env.NODE_ENV !== 'production') {
    if (value === null || value === undefined) {
      throw new NexusAssertionError(message);
    }
  }
}

export function assertUnreachable(
  x: never,
  message: string = 'Reached unexpected code path.'
): never {
  if (process.env.NODE_ENV !== 'production') {
    throw new NexusAssertionError(`${message} Value: ${x}`);
  }
  throw new Error('Unreachable path reached');
}
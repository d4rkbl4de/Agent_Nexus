export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  SILENT = 4,
}

interface LogOptions {
  level?: LogLevel;
  context?: string;
  timestamp?: Date;
  data?: unknown;
}

const DEFAULT_LOG_LEVEL =
  process.env.NODE_ENV === 'production' ? LogLevel.WARN : LogLevel.DEBUG;

const CurrentLogLevel = Number(
  process.env.NEXT_PUBLIC_LOG_LEVEL || DEFAULT_LOG_LEVEL
);

export class Logger {
  private context: string;

  constructor(context: string = 'App') {
    this.context = context;
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= CurrentLogLevel;
  }

  private formatMessage(
    level: LogLevel,
    message: string,
    options: LogOptions = {}
  ) {
    const timestamp = options.timestamp || new Date();
    const context = options.context || this.context;
    const levelName = LogLevel[level].padEnd(5, ' ');
    const logPrefix = `[${timestamp.toISOString()}] [${context}] [${levelName}]`;

    if (options.data !== undefined) {
      return [`${logPrefix} ${message}`, options.data];
    }
    return [`${logPrefix} ${message}`];
  }

  public log(level: LogLevel, message: string, options?: LogOptions): void {
    if (!this.shouldLog(level)) {
      return;
    }

    const output = this.formatMessage(level, message, options);

    switch (level) {
      case LogLevel.DEBUG:
        console.debug(...output);
        break;
      case LogLevel.INFO:
        console.info(...output);
        break;
      case LogLevel.WARN:
        console.warn(...output);
        break;
      case LogLevel.ERROR:
        console.error(...output);
        break;
      default:
        console.log(...output);
    }
  }

  public debug(message: string, data?: unknown): void {
    this.log(LogLevel.DEBUG, message, { data });
  }

  public info(message: string, data?: unknown): void {
    this.log(LogLevel.INFO, message, { data });
  }

  public warn(message: string, data?: unknown): void {
    this.log(LogLevel.WARN, message, { data });
  }

  public error(message: string, error?: Error | unknown, data?: unknown): void {
    let errorMessage = message;
    let logData = data;

    if (error instanceof Error) {
      errorMessage = `${message}: ${error.message}`;
      logData = { ...logData, stack: error.stack, error };
    } else if (error !== undefined) {
      logData = { ...logData, error };
    }
    
    this.log(LogLevel.ERROR, errorMessage, { data: logData });
  }
}

export const globalLogger = new Logger('Global');

export const createLogger = (context: string): Logger => new Logger(context);
/**
 * Combine all MSW handlers.
 */
import { authHandlers } from './auth';
import { lobbyHandlers } from './lobby';
import { gameHandlers } from './game';

export const handlers = [
  ...authHandlers,
  ...lobbyHandlers,
  ...gameHandlers,
];

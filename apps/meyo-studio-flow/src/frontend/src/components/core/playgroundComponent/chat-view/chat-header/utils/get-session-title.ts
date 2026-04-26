export function getSessionTitle(
  currentSessionId?: string,
  currentFlowId?: string,
  defaultSessionName = "Default Session",
): string {
  if (!currentSessionId || currentSessionId === currentFlowId) {
    return defaultSessionName;
  }
  return currentSessionId;
}

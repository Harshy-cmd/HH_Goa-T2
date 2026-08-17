/* ===== STATE MACHINE — Voice RAG 2026 ===== */

/**
 * Valid states:
 * IDLE, LISTENING, TRANSCRIBING, RETRIEVING, GENERATING,
 * GROUNDED, NO_CONTEXT, REFUSED, ERROR
 */
const STATES = {
  IDLE: 'idle',
  LISTENING: 'listening',
  TRANSCRIBING: 'transcribing',
  RETRIEVING: 'retrieving',
  GENERATING: 'generating',
  GROUNDED: 'grounded',
  NO_CONTEXT: 'no_context',
  REFUSED: 'refused',
  ERROR: 'error'
};

// Valid transitions map — state: [allowed next states]
const TRANSITIONS = {
  [STATES.IDLE]:         [STATES.LISTENING, STATES.TRANSCRIBING, STATES.RETRIEVING, STATES.ERROR],
  [STATES.LISTENING]:    [STATES.TRANSCRIBING, STATES.IDLE, STATES.ERROR],
  [STATES.TRANSCRIBING]: [STATES.RETRIEVING, STATES.IDLE, STATES.ERROR],
  [STATES.RETRIEVING]:   [STATES.GENERATING, STATES.NO_CONTEXT, STATES.REFUSED, STATES.ERROR, STATES.IDLE],
  [STATES.GENERATING]:   [STATES.GROUNDED, STATES.NO_CONTEXT, STATES.REFUSED, STATES.ERROR, STATES.IDLE],
  [STATES.GROUNDED]:     [STATES.IDLE, STATES.LISTENING, STATES.RETRIEVING, STATES.ERROR],
  [STATES.NO_CONTEXT]:   [STATES.IDLE, STATES.LISTENING, STATES.RETRIEVING, STATES.ERROR],
  [STATES.REFUSED]:      [STATES.IDLE, STATES.LISTENING, STATES.RETRIEVING, STATES.ERROR],
  [STATES.ERROR]:        [STATES.IDLE, STATES.LISTENING, STATES.RETRIEVING]
};

class StateMachine {
  constructor() {
    this._state = STATES.IDLE;
    this._listeners = [];
    this._stateTimeout = null;
    this._maxStateTimeout = 30000; // 30s safety timeout
  }

  get state() {
    return this._state;
  }

  /**
   * Transition to a new state. Validates transition is legal.
   * @param {string} newState
   * @param {object} [data] Optional data payload
   * @returns {boolean} Whether the transition succeeded
   */
  transition(newState, data = {}) {
    const allowed = TRANSITIONS[this._state];
    if (!allowed || !allowed.includes(newState)) {
      console.warn(`[StateMachine] Invalid transition: ${this._state} → ${newState}`);
      return false;
    }

    const oldState = this._state;
    this._state = newState;

    // Clear safety timeout
    if (this._stateTimeout) {
      clearTimeout(this._stateTimeout);
      this._stateTimeout = null;
    }

    // Set safety timeout for non-terminal states
    if ([STATES.LISTENING, STATES.TRANSCRIBING, STATES.RETRIEVING, STATES.GENERATING].includes(newState)) {
      this._stateTimeout = setTimeout(() => {
        console.warn(`[StateMachine] Safety timeout: stuck in ${this._state}`);
        this.transition(STATES.ERROR, { error: `Timeout in state: ${this._state}` });
      }, this._maxStateTimeout);
    }

    // Notify listeners
    for (const listener of this._listeners) {
      try {
        listener(newState, oldState, data);
      } catch (err) {
        console.error('[StateMachine] Listener error:', err);
      }
    }

    return true;
  }

  /**
   * Reset to idle state (bypass transition validation)
   */
  reset() {
    if (this._stateTimeout) {
      clearTimeout(this._stateTimeout);
      this._stateTimeout = null;
    }
    const oldState = this._state;
    this._state = STATES.IDLE;
    for (const listener of this._listeners) {
      try {
        listener(STATES.IDLE, oldState, { reset: true });
      } catch (err) {
        console.error('[StateMachine] Listener error on reset:', err);
      }
    }
  }

  /**
   * Subscribe to state changes
   * @param {Function} fn - (newState, oldState, data) => void
   * @returns {Function} unsubscribe function
   */
  subscribe(fn) {
    this._listeners.push(fn);
    return () => {
      this._listeners = this._listeners.filter(l => l !== fn);
    };
  }
}

// Global state machine instance
window.appState = new StateMachine();

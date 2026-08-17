/**
 * Latency Tracker — Voice RAG 2026
 * High-resolution timing for pipeline stages.
 */

class LatencyTracker {
  constructor() {
    this._records = [];  // All timing records
    this._stages = {};   // Aggregate stats per stage
  }

  /**
   * Start a timer for a named stage
   * @param {string} stageName
   * @returns {{stop: Function, elapsed: Function}}
   */
  start(stageName) {
    const startTime = process.hrtime.bigint();
    let endTime = null;

    return {
      stop: () => {
        endTime = process.hrtime.bigint();
        const elapsedMs = Number(endTime - startTime) / 1e6;

        this._record(stageName, elapsedMs);
        return elapsedMs;
      },
      elapsed: () => {
        if (endTime === null) {
          return Number(process.hrtime.bigint() - startTime) / 1e6;
        }
        return Number(endTime - startTime) / 1e6;
      }
    };
  }

  _record(stageName, elapsedMs) {
    this._records.push({
      stage: stageName,
      latency: elapsedMs,
      timestamp: Date.now()
    });

    if (!this._stages[stageName]) {
      this._stages[stageName] = [];
    }
    this._stages[stageName].push(elapsedMs);
  }

  /**
   * Get percentile stats for all stages
   * @returns {object}
   */
  getStats() {
    const stats = {};

    for (const [stage, timings] of Object.entries(this._stages)) {
      if (timings.length === 0) continue;
      stats[stage] = this._calcPercentiles(timings);
    }

    // Overall pipeline stats
    const pipelineTimings = this._stages['pipeline'] || [];
    if (pipelineTimings.length > 0) {
      stats.pipeline = this._calcPercentiles(pipelineTimings);
    }

    return {
      stages: stats,
      totalRecords: this._records.length,
      timestamp: Date.now()
    };
  }

  _calcPercentiles(timings) {
    const sorted = [...timings].sort((a, b) => a - b);
    const n = sorted.length;

    return {
      count: n,
      min: sorted[0],
      max: sorted[n - 1],
      mean: timings.reduce((a, b) => a + b, 0) / n,
      p50: this._percentile(sorted, 50),
      p70: this._percentile(sorted, 70),
      p100: sorted[n - 1] // Max observed
    };
  }

  _percentile(sorted, p) {
    const idx = Math.ceil((p / 100) * sorted.length) - 1;
    return sorted[Math.max(0, idx)];
  }

  /**
   * Clear all records
   */
  reset() {
    this._records = [];
    this._stages = {};
  }
}

module.exports = { LatencyTracker };

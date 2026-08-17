/**
 * MSMARCO-XI Dataset Inspection — Node Runner
 * Executes streaming dataset inspection for HH Goa 2026 Task 2.
 */

const { spawn } = require('child_process');
const path = require('path');
const { inspectDatasetNode } = require('../../scripts/inspect_dataset_node');

console.log('\n  🔍 MSMARCO-XI Dataset Inspection (HH Goa 2026 Task 2)\n');

const pyScript = path.join(__dirname, '..', '..', 'scripts', 'inspect_dataset.py');
const pyProcess = spawn('python', [pyScript, 'hin', 'validation']);

pyProcess.stdout.on('data', (data) => {
  process.stdout.write(data.toString());
});

pyProcess.stderr.on('data', (data) => {
  process.stderr.write(data.toString());
});

pyProcess.on('close', (code) => {
  if (code !== 0) {
    console.log('  Notice: Python pyarrow unavailable, executing native Node inspection...\n');
    inspectDatasetNode();
  }
});

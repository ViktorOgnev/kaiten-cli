import readline from 'node:readline';
import { once } from 'node:events';
import { syncDocument, SyncFailure } from './core.mjs';

async function main() {
  const lines = readline.createInterface({ input: process.stdin, terminal: false });
  const emit = value => process.stdout.write(JSON.stringify(value) + '\n');
  try {
    const [line] = await once(lines, 'line');
    const request = JSON.parse(line);
    const result = await syncDocument(request, {
      emit,
      authorize: () => {
        const permission = once(lines, 'line').then(([command]) => {
          if (JSON.parse(command).action !== 'write') throw new SyncFailure('invalid_permission');
        });
        emit({ event: 'write_ready' });
        return permission;
      },
    });
    emit({ event: 'result', result });
  } catch (error) {
    emit({ event: 'error', code: error instanceof SyncFailure ? error.code : 'helper_error' });
    process.exitCode = 1;
  } finally {
    lines.close();
    process.stdin.unref();
  }
}
main();

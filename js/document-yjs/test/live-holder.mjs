// Local integration probe only. Holds an editor's old state across a CLI update.
// Request/JWT arrive over stdin; stdout contains structural evidence only.
import readline from 'node:readline';
import { once } from 'node:events';
import { io } from 'socket.io-client';
import * as Y from 'yjs';
import { yDocToProsemirrorJSON } from 'y-prosemirror';

const lines = readline.createInterface({ input: process.stdin });
const [input] = await once(lines, 'line');
const request = JSON.parse(input);
if (process.env.KAITEN_LIVE !== '1' || !['localhost', '127.0.0.1'].includes(new URL(request.socketUrl).hostname)) {
  throw new Error('This probe requires KAITEN_LIVE=1 and a loopback socket origin.');
}
const doc = new Y.Doc();
let oldState;
let stage = 'initial';
const emit = data => process.stdout.write(JSON.stringify(data) + '\n');
const evidence = state => {
  const json = yDocToProsemirrorJSON(state, 'prosemirror');
  const tables = (json.content || []).filter(node => node.type === 'table');
  return { tables: tables.length, rows: tables.map(node => node.content.length) };
};
const socket = io(request.socketUrl, {
  autoConnect: false, reconnection: false, transports: ['websocket'],
  auth: { token: request.token }, query: { state_include: 'none' },
});
const timer = setTimeout(() => { emit({ stage: 'error', code: 'timeout' }); socket.disconnect(); process.exit(1); }, 30000);
const subscribe = vector => socket.emit('yjs-subscribe', {
  documentId: request.documentId, schemaVersion: request.schemaVersion,
  stateVector: vector, clientID: doc.clientID,
});
socket.on('connect', () => subscribe(Array.from(Y.encodeStateVector(doc))));
socket.on('connect_error', () => { emit({ stage: 'error', code: 'connect_error' }); process.exit(1); });
socket.on('yjs-event', event => {
  if (event.data.documentId !== request.documentId) return;
  if (event.name === 'yjs-document-disconnect') { emit({ stage: 'error', code: 'rejected' }); process.exit(1); }
  if (event.name !== 'yjs-sync') return;
  if (stage === 'verifying') {
    const fresh = new Y.Doc();
    Y.applyUpdateV2(fresh, new Uint8Array(event.data.update));
    emit({ stage: 'fresh', ...evidence(fresh) });
    fresh.destroy();
    clearTimeout(timer); socket.disconnect(); doc.destroy(); lines.close(); process.stdin.unref();
    return;
  }
  Y.applyUpdateV2(doc, new Uint8Array(event.data.update));
  if (stage === 'initial') {
    oldState = Y.encodeStateAsUpdateV2(doc);
    stage = 'held';
    socket.disconnect();
    emit({ stage: 'held', ...evidence(doc) });
  } else if (stage === 'reconnecting') {
    socket.emit('yjs-update', { documentId: request.documentId, schemaVersion: request.schemaVersion, update: Array.from(oldState) });
    stage = 'reconnected';
    emit({ stage: 'reconnected', ...evidence(doc) });
  }
});
lines.on('line', inputLine => {
  const command = JSON.parse(inputLine);
  if (command.action === 'reconnect' && stage === 'held') { stage = 'reconnecting'; socket.connect(); }
  if (command.action === 'verify' && stage === 'reconnected') { stage = 'verifying'; subscribe([]); }
});
socket.connect();

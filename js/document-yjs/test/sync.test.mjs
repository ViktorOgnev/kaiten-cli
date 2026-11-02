import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import readline from 'node:readline';
import { once } from 'node:events';
import { fileURLToPath } from 'node:url';
import { test } from 'node:test';
import { Server } from 'socket.io';
import * as Y from 'yjs';
import { prosemirrorJSONToYDoc, yDocToProsemirrorJSON } from 'y-prosemirror';
import { makeSchema, parseDocument, replaceContent, syncDocument } from '../core.mjs';

const p = (text, id) => ({ type: 'paragraph', ...(id ? { attrs: { 'data-block-id': id } } : {}), content: [{ type: 'text', text }] });
const original = { type: 'doc', content: [p('Вступление', 'intro'), {
  type: 'table', content: Array.from({ length: 122 }, (_, i) => ({
    type: 'table_row', content: [0, 1].map(j => ({
      type: i ? 'table_cell' : 'table_header', attrs: { colspan: 1, rowspan: 1, colwidth: [140] },
      content: [p(`${i}:${j}`)],
    })),
  })),
}, { type: 'paragraph' }] };
const target = structuredClone(original);
target.content[1].content[6].content[1].content = [p('Изменено')];
const schema = makeSchema('v1');
const targetNode = parseDocument(schema, target);
const asNode = doc => parseDocument(schema, yDocToProsemirrorJSON(doc, 'prosemirror'));
const tableCount = doc => yDocToProsemirrorJSON(doc, 'prosemirror').content.filter(n => n.type === 'table').length;

test('122 rows: baseline duplicates; same ancestry converges and preserves block identity', () => {
  const browser = prosemirrorJSONToYDoc(schema, original);
  const independent = prosemirrorJSONToYDoc(schema, target);
  const bad = new Y.Doc();
  Y.applyUpdateV2(bad, Y.encodeStateAsUpdateV2(browser));
  Y.applyUpdateV2(bad, Y.encodeStateAsUpdateV2(independent));
  assert.equal(tableCount(bad), 2);
  const server = new Y.Doc();
  Y.applyUpdateV2(server, Y.encodeStateAsUpdateV2(browser));
  const intro = server.getXmlFragment('prosemirror').get(0);
  const delta = replaceContent(server, schema, targetNode);
  Y.applyUpdateV2(browser, delta);
  Y.applyUpdateV2(browser, delta);
  Y.applyUpdateV2(server, Y.encodeStateAsUpdateV2(browser, Y.encodeStateVector(server)));
  assert.equal(tableCount(server), 1);
  assert.equal(yDocToProsemirrorJSON(server, 'prosemirror').content[1].content.length, 122);
  assert.equal(asNode(server).eq(targetNode), true);
  assert.equal(asNode(browser).eq(targetNode), true);
  assert.equal(server.getXmlFragment('prosemirror').get(0), intro);
  [browser, independent, bad, server].forEach(doc => doc.destroy());
});

test('distributed row deletions and insertions survive stale-state replay and duplicate delivery', () => {
  const desired = structuredClone(original);
  const rows = desired.content[1].content;
  desired.content[1].content = rows.filter((_, i) => !i || i % 5 !== 0);
  for (let i = 0; i < 36; i++) {
    const row = structuredClone(rows[1]);
    row.content[0].content = [p(`NEW-${i + 1}`)];
    row.content[1].content = [p(`New scenario ${i + 1}`)];
    desired.content[1].content.splice(1 + i * 3, 0, row);
  }
  desired.content.splice(2, 0, p('New material near the end', 'new-material'));
  const expected = parseDocument(schema, desired);
  const browser = prosemirrorJSONToYDoc(schema, original);
  const staleState = Y.encodeStateAsUpdateV2(browser);
  const server = new Y.Doc();
  try {
    Y.applyUpdateV2(server, staleState);
    const unchangedIntro = server.getXmlFragment('prosemirror').get(0);
    const delta = replaceContent(server, schema, expected);
    Y.applyUpdateV2(browser, delta);
    Y.applyUpdateV2(browser, delta);
    Y.applyUpdateV2(server, staleState);
    Y.applyUpdateV2(server, Y.encodeStateAsUpdateV2(browser));
    assert.equal(asNode(server).eq(expected), true);
    assert.equal(asNode(browser).eq(expected), true);
    assert.equal(tableCount(server), 1);
    const savedRows = yDocToProsemirrorJSON(server, 'prosemirror').content[1].content;
    assert.equal(savedRows.length, 134);
    const codes = savedRows.slice(1).map(row => row.content[0].content[0].content[0].text);
    assert.equal(new Set(codes).size, 133);
    for (let i = 5; i <= 120; i += 5) assert.equal(codes.includes(`${i}:0`), false);
    assert.equal(server.getXmlFragment('prosemirror').get(0), unchangedIntro);
  } finally {
    browser.destroy(); server.destroy();
  }
});

test('unknown schema, nodes, marks, attributes and invalid structure fail rather than disappear', () => {
  assert.throws(() => makeSchema('v999'), /unsupported_schema/);
  assert.throws(() => parseDocument(schema, { type: 'new_node' }), /unsupported_node/);
  assert.throws(() => parseDocument(schema, { type: 'doc', attrs: { unknown: 1 } }), /unsupported_attribute/);
  assert.throws(() => parseDocument(schema, { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'a', marks: [{ type: 'new_mark' }] }] }] }), /unsupported_mark/);
  assert.throws(() => parseDocument(schema, { type: 'doc', content: [{ type: 'table_row' }] }), /invalid_content/);
  assert.throws(() => parseDocument(schema, { type: 'doc', content: [{ type: 'paragraph', text: 'silently lost' }] }), /invalid_content/);
  assert.throws(() => parseDocument(schema, { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'a', content: [{ type: 'text', text: 'silently lost' }] }] }] }), /invalid_content/);
});

test('socket content obeys the API javascript URL restriction', () => {
  const data = structuredClone(original);
  data.content[0].content[0].marks = [{ type: 'link', attrs: { href: 'javascript:alert(1)' } }];
  assert.throws(() => parseDocument(schema, data), /unsafe_content_url/);
  data.content[0] = { type: 'image', attrs: { src: 'javascript:alert(1)' } };
  assert.throws(() => parseDocument(schema, data), /unsafe_content_url/);
});

test('all bundled schema versions roundtrip table edits without loss', () => {
  for (let version = 1; version <= 28; version++) {
    const currentSchema = makeSchema(`v${version}`);
    const desired = parseDocument(currentSchema, target);
    const doc = prosemirrorJSONToYDoc(currentSchema, original);
    replaceContent(doc, currentSchema, desired);
    assert.equal(parseDocument(currentSchema, yDocToProsemirrorJSON(doc, 'prosemirror')).eq(desired), true, `v${version}`);
    doc.destroy();
  }
});

test('parallel edits in another block survive CRDT merge without cloning the document', () => {
  const browser = prosemirrorJSONToYDoc(schema, original);
  const cli = new Y.Doc();
  Y.applyUpdateV2(cli, Y.encodeStateAsUpdateV2(browser));
  const cliDelta = replaceContent(cli, schema, targetNode);
  const text = browser.getXmlFragment('prosemirror').get(0).get(0);
  text.insert(text.length, ' + UI');
  Y.applyUpdateV2(browser, cliDelta);
  Y.applyUpdateV2(cli, Y.encodeStateAsUpdateV2(browser));
  assert.equal(tableCount(cli), 1);
  assert.equal(asNode(cli).textContent.includes(' + UI'), true);
  assert.equal(asNode(cli).textContent.includes('Изменено'), true);
  assert.equal(asNode(cli).eq(targetNode), false);
  browser.destroy(); cli.destroy();
});

async function fixture(t, options = {}) {
  const server = createServer();
  const io = new Server(server);
  const doc = prosemirrorJSONToYDoc(schema, options.alreadyUpdated ? target : original);
  const stale = new Y.Doc();
  Y.applyUpdateV2(stale, Y.encodeStateAsUpdateV2(doc));
  let writes = 0;
  io.use((socket, next) => next(socket.handshake.auth.token === 'test-jwt' ? undefined : new Error('auth')));
  io.on('connection', socket => {
    socket.on('yjs-subscribe', data => {
      if (options.reject) {
        socket.emit('yjs-event', { name: 'yjs-document-disconnect', data: { documentId: 'doc', reason: options.reject } });
      } else if (!options.noSync) {
        socket.emit('yjs-event', { name: 'yjs-sync', data: { documentId: 'doc', update: Array.from(Y.encodeStateAsUpdateV2(doc)), stateVector: Array.from(Y.encodeStateVector(doc)) } });
      }
    });
    socket.on('yjs-update', data => {
      writes++;
      Y.applyUpdateV2(doc, new Uint8Array(data.update));
      Y.applyUpdateV2(doc, Y.encodeStateAsUpdateV2(stale, Y.encodeStateVector(doc)));
      if (options.conflict) doc.getXmlFragment('prosemirror').get(0).get(0).insert(0, 'UI: ');
      if (options.disconnect) { socket.disconnect(true); return; }
      if (!options.noAck) socket.emit('yjs-event', { name: 'yjs-update-ack', data: { documentId: 'doc', batchId: data.batchId, updatedAt: '2026-10-20T12:00:00Z' } });
    });
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(async () => { await new Promise(resolve => io.close(resolve)); doc.destroy(); stale.destroy(); });
  return {
    request: { documentId: 'doc', schemaVersion: 'v1', socketUrl: `http://127.0.0.1:${server.address().port}`, token: 'test-jwt', data: target, timeoutMs: 1000 },
    doc, writes: () => writes,
  };
}

test('Socket.IO: ack and fresh authoritative state verify a single update', async t => {
  const f = await fixture(t);
  const events = [];
  const result = await syncDocument(f.request, { emit: event => events.push(event), authorize: async () => {} });
  assert.equal(result.status, 'verified');
  assert.deepEqual(events.map(event => event.event), ['connecting', 'acknowledged']);
  assert.equal(f.writes(), 1);
  assert.equal(tableCount(f.doc), 1);
  assert.equal(asNode(f.doc).eq(targetNode), true);
});

test('Socket.IO: identical content does not send a mutation', async t => {
  const f = await fixture(t, { alreadyUpdated: true });
  const result = await syncDocument(f.request, { emit: event => assert.equal(event.event, 'connecting'), authorize: () => assert.fail() });
  assert.equal(result.status, 'unchanged');
  assert.equal(f.writes(), 0);
});

for (const [name, options, code] of [
  ['read only', { reject: 1 }, 'read_only'],
  ['no access', { reject: 2 }, 'no_access'],
  ['unsupported server schema', { reject: 4 }, 'unsupported_schema'],
  ['initial sync timeout', { noSync: true }, 'timeout'],
  ['lost ack', { noAck: true }, 'timeout'],
  ['disconnect after send', { disconnect: true }, 'disconnected'],
  ['parallel update', { conflict: true }, 'verification_conflict'],
]) {
  test(`Socket.IO: ${name} fails without retry`, async t => {
    const f = await fixture(t, options);
    await assert.rejects(syncDocument(f.request, { emit: () => {}, authorize: async () => {} }), error => error.code === code);
    assert.equal(f.writes(), options.noAck || options.disconnect || options.conflict ? 1 : 0);
  });
}

test('bundled helper runs without npm modules and waits for parent write permission', async t => {
  const f = await fixture(t);
  const helper = fileURLToPath(new URL('../../../src/kaiten_cli/assets/document_yjs.cjs', import.meta.url));
  const child = spawn(process.execPath, [helper], { stdio: ['pipe', 'pipe', 'pipe'], cwd: '/tmp' });
  t.after(() => child.kill());
  const lines = readline.createInterface({ input: child.stdout });
  const output = [];
  lines.on('line', line => {
    const event = JSON.parse(line);
    output.push(event);
    if (event.event === 'write_ready') {
      assert.equal(f.writes(), 0);
      child.stdin.write('{"action":"write"}\n');
    }
  });
  child.stdin.write(JSON.stringify(f.request) + '\n');
  const [exit] = await once(child, 'exit');
  assert.equal(exit, 0);
  assert.deepEqual(output.map(event => event.event), ['connecting', 'write_ready', 'acknowledged', 'result']);
  assert.equal(output.at(-1).result.status, 'verified');
  assert.equal(JSON.stringify(output).includes('test-jwt'), false);
});

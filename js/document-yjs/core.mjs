import { randomUUID } from 'node:crypto';
import { Schema } from 'prosemirror-model';
import { io } from 'socket.io-client';
import * as Y from 'yjs';
import { prosemirrorToYXmlFragment, yDocToProsemirrorJSON } from 'y-prosemirror';
import schemaSpecs from './schemas.json' with { type: 'json' };

export class SyncFailure extends Error {
  constructor(code) { super(code); this.code = code; }
}

export function makeSchema(version) {
  if (!Object.hasOwn(schemaSpecs, version)) throw new SyncFailure('unsupported_schema');
  const spec = JSON.parse(JSON.stringify(schemaSpecs[version]));
  for (const group of [spec.nodes, spec.marks]) {
    for (const node of Object.values(group)) {
      for (const attr of Object.values(node.attrs || {})) {
        if (attr.undefinedDefault) {
          delete attr.undefinedDefault;
          attr.default = undefined;
        }
      }
    }
  }
  return new Schema(spec);
}

export function parseDocument(schema, data) {
  function checkUrl(value) {
    // Match document API validation; the socket transport must not bypass it.
    let protocol;
    try { protocol = new URL(value).protocol; } catch { return; }
    if (protocol === 'javascript:') throw new SyncFailure('unsafe_content_url');
  }
  function checkAttributes(attrs, spec) {
    if (attrs === undefined) return;
    if (!attrs || typeof attrs !== 'object' || Array.isArray(attrs)) throw new SyncFailure('invalid_content');
    for (const key of Object.keys(attrs)) {
      if (!Object.hasOwn(spec.attrs || {}, key)) throw new SyncFailure('unsupported_attribute');
    }
  }
  function visit(node) {
    if (!node || typeof node !== 'object' || Array.isArray(node)) throw new SyncFailure('invalid_content');
    const type = schema.nodes[node.type];
    if (!type) throw new SyncFailure('unsupported_node');
    for (const key of Object.keys(node)) {
      if (!['type', 'attrs', 'text', 'content', 'marks'].includes(key)) throw new SyncFailure('unsupported_attribute');
    }
    if ((node.type === 'text' && node.content !== undefined)
      || (node.type !== 'text' && node.text !== undefined)
      || (type.isLeaf && node.content?.length)) throw new SyncFailure('invalid_content');
    checkAttributes(node.attrs, type.spec);
    if (['embed', 'image'].includes(node.type) && node.attrs?.src) checkUrl(node.attrs.src);
    if (node.marks !== undefined && !Array.isArray(node.marks)) throw new SyncFailure('invalid_content');
    for (const mark of node.marks || []) {
      const markType = schema.marks[mark.type];
      if (!markType) throw new SyncFailure('unsupported_mark');
      if (Object.keys(mark).some(key => !['type', 'attrs'].includes(key))) throw new SyncFailure('unsupported_attribute');
      checkAttributes(mark.attrs, markType.spec);
      if (mark.type === 'link' && mark.attrs?.href) checkUrl(mark.attrs.href);
    }
    if (node.content !== undefined && !Array.isArray(node.content)) throw new SyncFailure('invalid_content');
    for (const child of node.content || []) visit(child);
  }
  try {
    visit(data);
    const doc = schema.nodeFromJSON(data);
    if (doc.type !== schema.topNodeType) throw new SyncFailure('invalid_content');
    doc.check();
    return doc;
  } catch (error) {
    if (error instanceof SyncFailure) throw error;
    throw new SyncFailure('invalid_content');
  }
}

export function replaceContent(doc, schema, target) {
  const before = Y.encodeStateVector(doc);
  prosemirrorToYXmlFragment(target, doc.getXmlFragment('prosemirror'));
  const actual = parseDocument(schema, yDocToProsemirrorJSON(doc, 'prosemirror'));
  if (!actual.eq(target)) throw new SyncFailure('content_roundtrip_mismatch');
  return Y.encodeStateAsUpdateV2(doc, before);
}

export async function syncDocument(request, { emit, authorize }) {
  const schema = makeSchema(request.schemaVersion);
  const target = parseDocument(schema, request.data);
  const doc = new Y.Doc();
  const batchId = randomUUID();
  const timeoutMs = Math.min(Math.max(request.timeoutMs || 20000, 100), 60000);
  let stage = 'initial';
  let updatedAt;
  const socket = io(request.socketUrl, {
    auth: { token: request.token },
    query: { state_include: 'none' },
    autoConnect: false, reconnection: false,
    transports: ['websocket', 'polling'], tryAllTransports: true,
    timeout: timeoutMs,
  });
  const subscribe = () => socket.emit('yjs-subscribe', {
    documentId: request.documentId, schemaVersion: request.schemaVersion,
    stateVector: [], clientID: doc.clientID,
  });
  try {
    return await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new SyncFailure('timeout')), timeoutMs);
      const fail = code => { clearTimeout(timer); stage = 'finished'; reject(new SyncFailure(code)); };
      const succeed = (state, status) => {
        clearTimeout(timer);
        stage = 'finished';
        resolve({
          document_uid: request.documentId, content_mode: 'yjs', status,
          schema_version: request.schemaVersion,
          data: yDocToProsemirrorJSON(state, 'prosemirror'),
          ...(updatedAt ? { updated: updatedAt } : {}),
        });
      };
      socket.on('connect', subscribe);
      socket.on('connect_error', () => fail('connection_error'));
      socket.on('disconnect', () => { if (stage !== 'finished') fail('disconnected'); });
      socket.on('yjs-event', async event => {
        if (stage === 'finished' || event?.data?.documentId !== request.documentId) return;
        const { name, data } = event;
        try {
          if (name === 'yjs-document-disconnect') {
            fail(({ 1: 'read_only', 2: 'no_access', 3: 'archived', 4: 'unsupported_schema' })[data.reason] || 'server_rejected');
          } else if (name === 'yjs-force-sync') {
            fail('server_force_sync');
          } else if (name === 'yjs-update') {
            Y.applyUpdateV2(doc, new Uint8Array(data.update));
            if (stage === 'ready') fail('concurrent_change');
          } else if (name === 'yjs-update-ack' && stage === 'sent' && data.batchId === batchId) {
            emit({ event: 'acknowledged' });
            updatedAt = data.updatedAt;
            stage = 'verifying';
            subscribe();
          } else if (name === 'yjs-sync' && stage === 'verifying') {
            const saved = new Y.Doc();
            try {
              Y.applyUpdateV2(saved, new Uint8Array(data.update));
              if (!parseDocument(schema, yDocToProsemirrorJSON(saved, 'prosemirror')).eq(target)) {
                fail('verification_conflict');
              } else succeed(saved, 'verified');
            } finally { saved.destroy(); }
          } else if (name === 'yjs-sync' && stage === 'initial') {
            Y.applyUpdateV2(doc, new Uint8Array(data.update));
            const original = parseDocument(schema, yDocToProsemirrorJSON(doc, 'prosemirror'));
            if (original.eq(target)) { succeed(doc, 'unchanged'); return; }
            const update = replaceContent(doc, schema, target);
            stage = 'ready';
            // Parent invalidates caches before allowing a socket write.
            await authorize();
            if (stage !== 'ready') return;
            stage = 'sent';
            socket.emit('yjs-update', {
              documentId: request.documentId, schemaVersion: request.schemaVersion,
              update: Array.from(update), batchId,
            });
          }
        } catch (error) { fail(error instanceof SyncFailure ? error.code : 'invalid_sync_state'); }
      });
      emit({ event: 'connecting' });
      socket.connect();
    });
  } finally {
    stage = 'finished';
    socket.removeAllListeners();
    socket.disconnect();
    doc.destroy();
  }
}

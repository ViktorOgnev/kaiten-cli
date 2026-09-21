/* Extract the portal's modal tables; no browser, profile, or tenant calls.
 * The portal builds these tables from constants and four collection helpers.
 * Run only on a reviewed local bundle. Unknown layouts fail closed.
 */
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(process.argv[2], 'utf8');
const start = source.indexOf('aJ="on_action"');
const end = source.indexOf(',s5=e=>', start);
const operators = source.match(/29001:e=>\{"use strict";e.exports=(\{[^}]+\})/);
if (start < 0 || end < 0 || !operators) throw new Error('Unknown automation bundle layout');
const expression = source.slice(start, end);
const prelude = `const ops=${operators[1]}; const n=()=>ops; n.n=x=>()=>x;
const values=x=>Array.isArray(x)?x:Object.values(x);
const nT=()=>({join:(x,s)=>x.join(s),forEach:(x,f)=>values(x).forEach(f),map:(x,f)=>values(x).map(f),reject:(x,f)=>values(x).filter(v=>!f(v))});`;
const output = `JSON.stringify({
 create:[sX,s0,s1].map(x=>({name:x.name,schema:{columns:x.schema.columns,data:x.schema.data}})),
 update:[s2,s4,s3].map(x=>({name:x.name,schema:{columns:x.schema.columns,data:x.schema.data}})),
 conditions:Object.values(sv), actions:sQ,
 triggers:[...s$,...sZ].map(x=>({type:x.type,name:x.name,attributes:x.attributes,conditions:x.conditions,actions:x.actions.schema.data.map(x=>x.key),automationType:sZ.includes(x)?'on_date':'on_action'}))
})`;
try {
 const result = vm.runInNewContext(prelude + 'let ' + expression + ';' + output,
  Object.create(null), {timeout:1000,contextCodeGeneration:{strings:false,wasm:false}});
 process.stdout.write(result);
} catch (error) {
 // Never print the downloaded program in an exception trace.
 process.stderr.write('Automation extraction failed: ' + error.message + '\n');
 process.exitCode = 1;
}

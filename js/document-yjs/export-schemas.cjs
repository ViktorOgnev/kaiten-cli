// Maintenance only: extract JSON construction/validation rules, never browser code.
// Usage: node export-schemas.cjs /path/to/kaiten-lib
const { createRequire } = require('node:module');
const fs = require('node:fs');
const path = require('node:path');
const req = createRequire(path.resolve(process.argv[2], 'package.json'));
const makeSchema = req('./lib/shared/ProseMirror/document/makeSchema');
const result = {};
for (let version = 1; version <= 28; version++) {
  const schema = makeSchema(`v${version}`, {});
  const extract = (ordered) => {
    const specs = {};
    ordered.forEach((name, spec) => {
      const copy = {};
      for (const key of ['content', 'marks', 'group', 'inline', 'atom', 'isolating', 'defining', 'code', 'whitespace']) {
        if (key in spec) copy[key] = spec[key];
      }
      if (spec.attrs) {
        copy.attrs = {};
        for (const [key, attr] of Object.entries(spec.attrs)) {
          const value = {};
          if (Object.hasOwn(attr, 'default')) {
            if (typeof attr.default === 'function') throw new Error('Dynamic attribute default');
            if (attr.default === undefined) value.undefinedDefault = true;
            else value.default = attr.default;
          }
          if (typeof attr.validate === 'string') value.validate = attr.validate;
          copy.attrs[key] = value;
        }
      }
      specs[name] = copy;
    });
    return specs;
  };
  result[`v${version}`] = { nodes: extract(schema.spec.nodes), marks: extract(schema.spec.marks) };
}
fs.writeFileSync(path.join(__dirname, 'schemas.json'), JSON.stringify(result) + '\n');

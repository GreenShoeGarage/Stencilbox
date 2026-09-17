#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const E = require('../src/engine.js');
const root = path.resolve(__dirname, '..');
const output = path.resolve(process.env.STENCILBOX_TEST_OUTPUT || path.join(root, 'artifacts/test-results'));
fs.mkdirSync(output, {recursive: true});
const checks = [];
for (const family of E.patterns) {
  const legacy = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/legacy', family + '-study.json')));
  const current = JSON.parse(fs.readFileSync(path.join(root, 'examples', family + '-study.json')));
  assert.equal(legacy.format, 'traceform-project');
  assert.equal(current.format, 'stencilbox-project');
  const restored = E.deserialize(legacy);
  const exported = E.serialize(restored.p, restored.edits, restored.model);
  assert.deepEqual(exported.geometry, legacy.geometry);
  assert.equal(exported.format, 'stencilbox-project');
  assert.equal(exported.settings.name, legacy.settings.name);
  assert.equal(exported.settings.notes, legacy.settings.notes);
  assert.deepEqual(E.deserialize(current).model.outer, restored.model.outer);
  assert.deepEqual(E.deserialize(current).model.holes, restored.model.holes);
  assert.deepEqual(E.deserialize(exported).model.holes, restored.model.holes);
  const binary = Buffer.from(E.stl(E.mesh(restored.model)));
  assert.ok(binary.subarray(0,80).toString().startsWith('STENCILBOX 1.0.0'));
  assert.ok(E.svg(restored.model).includes('<title>STENCILBOX stencil'));
  const damaged = JSON.parse(JSON.stringify(legacy));
  damaged.geometry.openings[0].points[0][0] += 1;
  assert.throws(() => E.deserialize(damaged), /saved geometry and recipe/);
  assert.throws(() => E.deserialize({...legacy, generatorVersion: '99.0.0'}));
  checks.push(family + ': legacy/current geometry match, title/notes preserved, re-export and validation pass');
}
const report = {suite: 'STENCILBOX rename compatibility', generatorVersion: E.VERSION, passed: checks.length, checks};
fs.writeFileSync(path.join(output, 'rename-geometry-results.json'), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));

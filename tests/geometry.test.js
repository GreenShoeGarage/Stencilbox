#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs'),path=require('node:path');
const E=require('../src/engine.js');const root=path.resolve(__dirname,'..');const report={suite:'STENCILBOX geometry regression',version:E.VERSION,cases:0,failures:[],patterns:{},examples:[]};
const output=path.resolve(process.env.STENCILBOX_TEST_OUTPUT||path.join(root,'artifacts/test-results'));
const exampleOutput=path.join(output,'examples');fs.mkdirSync(exampleOutput,{recursive:true});
let num=0;
function check(p,label){const start=Date.now();const model=E.generate(p),mesh=E.mesh(model);report.cases++;num++;try{
 assert.equal(mesh.validation.ok,true,JSON.stringify(mesh.validation));
 assert.equal(mesh.validation.components,1);assert.equal(mesh.validation.badEdges,0);assert.equal(mesh.validation.degenerate,0);
 assert.equal(E.simple(model.outer),true,'Outer polygon self-intersects');
 for(const h of model.holes)assert.equal(E.simple(h.poly),true,'Opening self-intersects '+h.id);
 const measured=E.measure(model);if(measured.minWeb!==null)assert.ok(measured.minWeb>=p.minWeb-.00011,'Web below target');if(measured.minBorder!==null)assert.ok(measured.minBorder>=p.border-.00011,'Border below target');
 const stl=E.stl(mesh);assert.equal(stl.byteLength,84+50*mesh.faces.length);assert.equal(new DataView(stl).getUint32(80,true),mesh.faces.length);
 const project=E.serialize(p,{},model);const restored=E.deserialize(JSON.parse(JSON.stringify(project)));assert.deepEqual(restored.model.outer,model.outer);assert.deepEqual(restored.model.holes.map(h=>h.poly),model.holes.map(h=>h.poly));
 const again=E.generate(p);assert.deepEqual(again.holes.map(h=>h.poly),model.holes.map(h=>h.poly),'Not deterministic');
 }catch(err){report.failures.push({label,settings:p,error:err.message});}
 const old=report.patterns[p.pattern]||{cases:0,maxMs:0};old.cases++;old.maxMs=Math.max(old.maxMs,Date.now()-start);report.patterns[p.pattern]=old;return{model,mesh};}
for(const pattern of E.patterns){
 const presets={scatter:{shape:'mixed',roundness:20},grid:{shape:'circle',jitter:15,variation:35},honeycomb:{jitter:0,variation:10,openingScale:94},triangles:{openingScale:94,roundness:15,variation:0},voronoi:{openingScale:90,variation:20,jitter:90},radial:{board:'ellipse',width:150,height:150,shape:'triangle',jitter:15,variation:25,count:80},waves:{width:170,height:100,jitter:100,variation:10},weave:{width:140,height:140,jitter:0,variation:10}};
 const p={...E.defaults,...presets[pattern],pattern,name:'STENCILBOX '+pattern+' study'};const {model,mesh}=check(p,'example-'+pattern);if(mesh.validation.ok){const base=path.join(exampleOutput,pattern+'-study');fs.writeFileSync(base+'.stl',Buffer.from(E.stl(mesh)));fs.writeFileSync(base+'.json',JSON.stringify(E.serialize(p,{},model),null,2));fs.writeFileSync(base+'.svg',E.svg(model));report.examples.push({file:pattern+'-study.stl',holes:model.holes.length,triangles:mesh.faces.length,dimensions:[p.width,p.height,p.thickness]});}
 for(let seed=0;seed<24;seed++){const r=E.rng('test'+seed+pattern);const p={...E.defaults,pattern,seed:'TEST-'+seed,shape:E.shapes[seed%E.shapes.length],board:['rounded','rectangle','ellipse','hexagon'][seed%4],width:60+r()*210,height:60+r()*170,thickness:.6+r()*4,minWeb:.5+r()*5,border:2+r()*10,count:12+Math.round(r()*125),openingScale:45+r()*85,patternScale:70+r()*60,rotation:-70+r()*140,holeRotation:seed%4===0?30:0,jitter:r()*100,variation:r()*65,roundness:seed%3===0?0:r()*60,stretchX:70+r()*60,stretchY:70+r()*60,shear:-25+r()*50,mirrorX:seed%2===0,mirrorY:seed%3===0,offsetX:seed%5===0?8:0};check(p,pattern+'-'+seed);}
 check({...E.defaults,pattern,count:0},pattern+'-blank');check({...E.defaults,pattern,width:40,height:40,border:30,count:180,openingScale:160},pattern+'-no-room');check({...E.defaults,pattern,count:180,jitter:0,variation:0,roundness:0,openingScale:70,minWeb:.4},pattern+'-dense-collinear');
}
// Input validation is intentionally strict, including the reproducibility snapshot.
const sample=JSON.parse(fs.readFileSync(path.join(root,'examples/voronoi-study.json'),'utf8'));
assert.throws(()=>E.deserialize({...sample,format:'other'}));assert.throws(()=>E.deserialize({...sample,units:'inch'}));assert.throws(()=>E.deserialize({...sample,generatorVersion:'9.0.0'}));
const bad=JSON.parse(JSON.stringify(sample));bad.geometry.openings[0].points[0][0]+=1;assert.throws(()=>E.deserialize(bad));assert.throws(()=>E.normalize({width:Infinity}));assert.throws(()=>E.normalize({pattern:'unknown'}));
report.inputRejections=6;fs.writeFileSync(path.join(output,'geometry-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(report.failures.length)process.exitCode=1;

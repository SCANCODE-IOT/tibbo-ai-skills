// Test stand-in for tibbotech/tibbo-basic compile-project.js: same CLI and output format.
const fs = require('fs'), path = require('path');
const a = process.argv.slice(2), dir = a[0], out = a[a.indexOf('-o') + 1];
const tpr = fs.readdirSync(dir).find(f => f.endsWith('.tpr'));
const src = fs.readFileSync(path.join(dir, 'main.tbs'), 'latin1');
const debug = /^\s*debug\s*=\s*on/mi.test(fs.readFileSync(path.join(dir, tpr), 'latin1'));
console.warn(path.join(dir, '..', 'Platforms', 'TPP3W(G2)', 'TPP3W(G2).tph') + ":16:0: warning: preprocessor redefinition of 'OBJECT_KP'");
const i = src.split(/\r?\n/).findIndex(l => l.includes('sock.nmu'));
if (i >= 0) {
  console.error(path.join(dir, 'main.tbs') + ':' + (i + 1) + ":0: error: 'nmu' is not member of 'sock' object");
  console.error('\nCompilation failed with 1 error(s)');
  process.exit(1);
}
const tpc = Buffer.alloc(64); tpc.write('TBIN', 0); tpc.writeUInt32LE(debug ? 0xf : 0xe, 28);
fs.writeFileSync(out, tpc); console.log(out + ' (64 bytes)');

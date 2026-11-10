#!/usr/bin/env node
// Ground truth of the TiOS API per platform, taken from Tibbo's own compiler (github.com/tibbotech/tibbo-basic,
// branch feature/compiler) after it has parsed the platform headers: objects, properties (read/write, type),
// methods (argument count), events (exact arguments), enums, global syscalls.
// Dev tool, not shipped in the skill. Output feeds skills/tibbo-firmware/data/platform_api.json.
//
//   node tools/dump_platform_api.js <tibbo-basic folder> <Platforms folder> <out.json>
'use strict';
const fs = require('fs'), path = require('path'), os = require('os');
const [home, platformsDir, outFile] = process.argv.slice(2);
const comp = require(path.join(home, 'server/out/compiler/tbc/compiler.js'));
const { tmakeBuild } = require(path.join(home, 'server/out/compiler/tmake.js'));

let captured = null;
const orig = comp.TibboBasicCompiler.prototype.Compile;
comp.TibboBasicCompiler.prototype.Compile = function (opts) {
    try { return orig.call(this, opts); } finally { if (/probe\.tbs$/i.test(opts.sourceFile)) captured = this; }
};
const entries = (strMap) => [...strMap.m.values()].map((e) => e.value);
const ptr = (p) => (p && (p.p || p.m_p || p.ptr || p.value || (typeof p.get === 'function' ? p.get() : null))) || null;
const tname = (t) => (t && t.m_strName) || null;
const args = (f) => (f.m_lstFormalArgs || []).map((a) => {
    const v = ptr(a.m_Value) || a.m_Value;
    const variable = v && v.m_pVariable;
    return { n: variable ? variable.m_strName : null, t: tname((v && v.m_pDataType) || (variable && variable.m_pDataType)),
        byref: !!(variable && (variable.m_bByRef || variable.m_Flags & 1)) };
});

// Objects that exist only when the project enables them (Project Settings -> Customize; "defines=" in the .tpr)
const OPTIONAL = ['OBJECT_LCD=LCD_ENABLED', 'OBJECT_FD=FD_ENABLED', 'OBJECT_KP=KP_ENABLED', 'OBJECT_WLN=WLN_ENABLED'];

function probe(p, defines) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tbprobe-'));
    const def = defines.length ? 'defines=' + defines.map((d) => ' /d' + d).join('') + '\n' : '';
    fs.writeFileSync(path.join(dir, 'probe.tpr'), `[project]\nname=probe\noutput=probe.tpc\ndebug=off\nplatform=${p}\n${def}[file1]\npath=probe.tbs\ntype=basic\n`);
    fs.writeFileSync(path.join(dir, 'probe.tbs'), 'sub on_sys_init()\r\nend sub\r\n');
    captured = null;
    let r;
    try { r = tmakeBuild(dir, platformsDir, {}); } catch (e) { r = { errors: [{ message: String(e) }] }; }
    fs.rmSync(dir, { recursive: true, force: true });
    if (!captured || (r.errors && r.errors.length)) return { error: (r.errors && r.errors[0] && r.errors[0].message) || 'no compiler instance' };
    const c = captured, objects = {}, events = {}, enums = {}, functions = {};
    for (const o of c.m_lstObjects) {
        const props = {}, methods = {};
        for (const pr of o.m_lstProperties) props[pr.m_strName] = { r: !!pr.m_pPropertyGet, w: !!pr.m_pPropertySet, t: tname(pr.m_pDataType) };
        for (const id of entries(o.m_mapIdentifiers)) {
            const f = id.m_pvObject;
            if (f && Array.isArray(f.m_lstFormalArgs) && !(id.m_strName in props)) methods[id.m_strName] = args(f).length;
        }
        objects[o.m_strName] = { props, methods };
    }
    for (const f of c.m_lstFunctions) if ('m_nEventIdx' in f) events[f.m_strName] = args(f);
    for (const t of c.m_lstTypes) if (Array.isArray(t.m_lstMembers) && t.m_lstMembers.length && t.m_strName) enums[t.m_strName] = t.m_lstMembers.map((m) => m.m_strName);
    for (const s of c.m_lstSyscalls) if (s.m_strName && !s.m_strName.includes('.')) functions[s.m_strName] = args(s).length;
    const types = c.m_lstTypes.map((t) => t.m_strName).filter(Boolean);
    return { objects, events, enums, functions, types };
}

const result = {};
const platforms = fs.readdirSync(platformsDir).filter((d) => fs.existsSync(path.join(platformsDir, d, d + '.tph'))).sort();
for (const p of platforms) {
    const base = probe(p, []);
    if (base.error) { result[p] = base; continue; }
    // LCD needs a panel type too; take the platform's first LCD_TYPE option if the .tp lists one
    base.optional = {};
    for (const d of OPTIONAL) {
        const extra = d.startsWith('OBJECT_LCD') ? ['LCD_TYPE=SAMSUNG_S6B0108'] : [];
        const v = probe(p, [d, ...extra]);
        if (v.error) continue;
        for (const o of Object.keys(v.objects)) {
            if (!(o in base.objects) && !o.startsWith('!')) {
                base.optional[o] = { define: d, props: v.objects[o].props, methods: v.objects[o].methods,
                    events: Object.fromEntries(Object.entries(v.events).filter(([e]) => !(e in base.events))),
                    enums: Object.fromEntries(Object.entries(v.enums).filter(([e]) => !(e in base.enums))) };
            }
        }
    }
    result[p] = base;
}
fs.writeFileSync(outFile, JSON.stringify(result));
for (const [p, v] of Object.entries(result)) {
    console.log(p.padEnd(14), v.error ? 'ERROR ' + v.error : `${Object.keys(v.objects).length} objects, ${Object.keys(v.events).length} events, optional: ${Object.keys(v.optional).join(' ') || '-'}`);
}

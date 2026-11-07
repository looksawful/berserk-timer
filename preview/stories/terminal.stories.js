const css="font:15px/1.55 Consolas, 'Cascadia Mono', monospace;background:#0e0e0e;color:#e8e8e8;min-height:100vh;padding:32px;box-sizing:border-box";
const wrap=(inner)=>{const root=document.createElement("main");root.style.cssText=css;const box=document.createElement("section");box.style.cssText="max-width:780px;margin:0 auto;border:1px solid #444;background:#161616;padding:26px;white-space:pre-wrap";box.innerHTML=inner;root.append(box);const note=document.createElement("p");note.style.cssText="margin:16px auto;max-width:780px;color:#999;font-size:12px";note.textContent="Документационный HTML-референс Python CLI; поведение таймера проверяется только в реальном терминале.";root.append(note);return root};
const h=(s)=>"<strong style='color:#fff'>"+s+"</strong>";
export default { title:"Berserk Timer",parameters:{layout:"fullscreen"} };
export const Typography={render:()=>wrap(h("BERSERK TIMER")+"\n\n00:25:00\n\n[p] pause / resume    [q] quit    [r] restart\n\nКегль 15px · Consolas/Cascadia Mono (браузерный референс)")};Typography.storyName="Foundations / Monospace typography";
export const Presets={render:()=>wrap(h("PRESETS")+"\n\n-x 5 min\n-s 10 min\n-m 15 min\n-l 20 min\n-X 25 min\n-t 1 min test")};Presets.storyName="Atoms / Duration presets";
const state=(title,time,help)=>wrap(h(title)+"\n\n<span style='font-size:44px;color:#f5f5f5'>"+time+"</span>\n\n"+help);
export const Ready={render:()=>state("READY","25:00","Press Enter to start")};Ready.storyName="Screens / Ready";
export const Running={render:()=>state("RUNNING","14:35","[p] pause  [q] quit  [r] restart  [u] change duration")};Running.storyName="Screens / Running";
export const Paused={render:()=>state("PAUSED","14:35","[p] resume  [q] quit")};Paused.storyName="Screens / Paused";
export const Complete={render:()=>state("COMPLETE","00:00","Session complete. Alert / witness are separate optional flows.")};Complete.storyName="Screens / Completed";
export const Commands={render:()=>wrap(h("COMMANDS")+
"\n\np  pause/resume\nq  quit\nx  zero\nr  restart\nv  view witness log\nd  delete witness log\nu  change duration\ng  set or clear goal\nm  toggle mute\ns  audio settings\nk  stop alert\nh  help")};Commands.storyName="Organisms / Help";
export const Witness={render:()=>wrap(h("WITNESS MODE")+"\n\nWhat was accomplished?\n> [user input]\n\nDefault safe word: skip")};Witness.storyName="Patterns / Witness logging";

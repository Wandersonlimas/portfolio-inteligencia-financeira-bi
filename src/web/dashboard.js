(() => {
'use strict';
const model=JSON.parse(document.getElementById('model-data').textContent);
const all=model.registros;
const months=['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];
const fields=['receita_bruta','deducoes','receita_liquida','cmv','lucro_bruto','taxas','frete','margem_contribuicao','despesas_fixas','ebitda'];
const state={period:'ytd',channel:'*',line:'*',growth:0,eff:0,tab:'executiva'};
const brl=new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL',maximumFractionDigits:0});
const fmt=(n)=>brl.format(n/100);
const compact=(n)=>{let x=n/100;return x>=1e6||x<=-1e6?(x/1e6).toLocaleString('pt-BR',{maximumFractionDigits:2})+' mi':(x/1e3).toLocaleString('pt-BR',{maximumFractionDigits:0})+' mil'};
const pct=(n)=>Number.isFinite(n)?n.toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+'%':'n/d';
const fsign=(n)=> (n>0?'+':'')+pct(n);
const sum=(rs)=>{let out={pedidos:0};for(const f of fields)out[f]=0;for(const r of rs){out.pedidos+=r.pedidos;for(const f of fields)out[f]+=r[f]}return out};
const monthsOf=()=>state.period==='ytd'?Array.from({length:10},(_,i)=>i+1):state.period==='full'?Array.from({length:12},(_,i)=>i+1):state.period==='h2'?[7,8,9,10,11,12]:state.period==='q3'?[7,8,9]:[10];
const dimensions=(r)=> (state.channel==='*'||r.canal===state.channel)&&(state.line==='*'||r.linha===state.line);
const calcProjected=(r,growth=0,eff=0)=>{if(r.tipo!=='projetado')return r;const q=(1+growth/100),c=q*(1-eff/100),gross=Math.round(r.receita_bruta*q),deduct=Math.round(r.deducoes*q),net=gross-deduct,cogs=Math.round(r.cmv*c),fees=Math.round(r.taxas*c),freight=Math.round(r.frete*c),gp=net-cogs,contrib=gp-fees-freight;return {...r,pedidos:Math.round(r.pedidos*q),receita_bruta:gross,deducoes:deduct,receita_liquida:net,cmv:cogs,lucro_bruto:gp,taxas:fees,frete:freight,margem_contribuicao:contrib,ebitda:contrib-r.despesas_fixas}};
const getRows=(period=monthsOf(),growth=state.growth,eff=state.eff)=>all.filter(r=>period.includes(r.mes)&&dimensions(r)).filter(r=>r.tipo==='realizado'||r.tipo==='projetado').map(r=>calcProjected(r,growth,eff));
const getBudget=(period=monthsOf())=>all.filter(r=>r.tipo==='orcamento'&&period.includes(r.mes)&&dimensions(r));
const diff=(a,b)=>b===0?NaN:(a/b-1)*100;
const safePct=(n,d)=>d===0?NaN:n/d*100;
const el=(id)=>document.getElementById(id);
function chip(label,value){
  const positive=Number.isFinite(value)&&value>0,negative=Number.isFinite(value)&&value<0;
  const icon=positive?'↗':negative?'↘':'•';
  const isPp=label.startsWith('p.p.');
  const labelText=isPp?label.replace('p.p.','').trim():label;
  const number=Number.isFinite(value)?(isPp?((value>0?'+':'')+value.toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})+' p.p.'):fsign(value)):'n/d';
  return `<span class="kpi-tag ${negative?'negative':positive?'positive':'neutral'}" title="Comparação de mesmo período e filtros">${icon} <strong>${number}</strong> <small>${labelText}</small></span>`;
}
function kpiIcon(name){
 const paths={
  receita:'<ellipse cx="10" cy="6" rx="6" ry="3"/><path d="M4 6v7c0 2 12 2 12 0V6M4 9c0 2 12 2 12 0M4 13v4c0 2 12 2 12 0v-4M17 8h4v10c0 2-4 2-4 0V8z"/>',
  ebitda:'<path d="M3 19V12h4v7M10 19V8h4v11M17 19V4h4v15M2 21h20"/>',
  margem:'<path d="M5 20 19 4"/><circle cx="7.5" cy="6.5" r="2.5"/><circle cx="16.5" cy="17.5" r="2.5"/>',
  contribuicao:'<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.6"/><path d="m12 12 8-8"/>',
  pedidos:'<circle cx="9" cy="20" r="1"/><circle cx="19" cy="20" r="1"/><path d="M2 3h3l3 13h12l2-9H6"/>'
 };
 return `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name]||paths.receita}</svg>`;
}
function kpi(icon,label,value,tag,negative=false){return `<div class="kpi"><div class="kpi-top"><span class="kpi-icon" aria-hidden="true">${kpiIcon(icon)}</span><span class="kpi-label">${label}</span></div><div class="kpi-value ${negative?'negative':''}">${value}</div>${tag}</div>`}
function renderKpis(rows,budget){
 const a=sum(rows),b=sum(budget);
 const am=safePct(a.ebitda,a.receita_liquida),bm=safePct(b.ebitda,b.receita_liquida);
 const ac=safePct(a.margem_contribuicao,a.receita_liquida),bc=safePct(b.margem_contribuicao,b.receita_liquida);
 const marginChip=(val,comparison)=>chip('p.p. vs orçamento',val-comparison);
 el('kpis').innerHTML=[
  kpi('receita','Receita líquida',fmt(a.receita_liquida),chip('vs orçamento',diff(a.receita_liquida,b.receita_liquida))),
  kpi('ebitda','EBITDA gerencial',fmt(a.ebitda),chip('vs orçamento',diff(a.ebitda,b.ebitda)),a.ebitda<0),
  kpi('margem','Margem EBITDA',pct(am),marginChip(am,bm),am<0),
  kpi('contribuicao','Margem de contribuição',pct(ac),marginChip(ac,bc)),
  kpi('pedidos','Pedidos consolidados',a.pedidos.toLocaleString('pt-BR'),chip('vs orçamento',diff(a.pedidos,b.pedidos)))
 ].join('');
}
function renderChart(rows,budget){
 const active=monthsOf(),WIDTH=900,HEIGHT=290, left=67,right=57,top=20,bottom=47;
 const plotW=WIDTH-left-right, plotH=HEIGHT-top-bottom;
 const series=active.map(m=>{let v=sum(rows.filter(r=>r.mes===m));return {m,net:v.receita_liquida,margin:safePct(v.ebitda,v.receita_liquida),future:m>10}});
 const moneyMax=Math.max(1,...series.map(x=>x.net));
 const moneyAxis=Math.ceil((moneyMax/100/1000)/50)*50 || 50;
 const margins=series.map(x=>Number.isFinite(x.margin)?x.margin:0);
 const bottomPct=Math.min(0,Math.floor(Math.min(...margins)/2)*2);
 const topPct=Math.max(5,Math.ceil(Math.max(...margins)/2)*2);
 const yMargin=v=>top+(topPct-v)/(topPct-bottomPct)*plotH;
 const slot=plotW/series.length;
 const xCenter=i=>left+slot*(i+.5);
 const yNet=v=>top+plotH-(v/100/1000)/moneyAxis*plotH;
 let svg=`<svg class="finance-svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" preserveAspectRatio="xMidYMid meet" aria-label="Receita mensal e margem EBITDA" xmlns="http://www.w3.org/2000/svg">`;
 for(let i=0;i<=4;i++){
  let y=top+i*plotH/4,amount=moneyAxis*(1-i/4),percentage=topPct-(topPct-bottomPct)*i/4;
  svg+=`<line x1="${left}" y1="${y}" x2="${WIDTH-right}" y2="${y}" class="axis-grid"/>`;
  svg+=`<text x="${left-11}" y="${y+4}" text-anchor="end" class="axis-label">${Math.round(amount).toLocaleString('pt-BR')}</text>`;
  svg+=`<text x="${WIDTH-right+10}" y="${y+4}" class="axis-label">${pct(percentage)}</text>`;
 }
 let points=[];
 series.forEach((s,i)=>{
  const x=xCenter(i),w=Math.min(42,slot*.58),y=yNet(s.net),barh=top+plotH-y;
  svg+=`<rect x="${(x-w/2).toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${Math.max(0,barh).toFixed(1)}" rx="5" class="month-bar ${s.future?'bar-future':''}"><title>${months[s.m-1]}: Receita ${fmt(s.net)}; Margem EBITDA ${pct(s.margin)}</title></rect>`;
  svg+=`<text x="${x.toFixed(1)}" y="${HEIGHT-18}" text-anchor="middle" class="month-label">${months[s.m-1].toLowerCase()}/26</text>`;
  if(Number.isFinite(s.margin))points.push({x,y:yMargin(s.margin),margin:s.margin,m:s.m});
 });
 if(points.length>1)svg+=`<polyline points="${points.map(p=>`${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')}" fill="none" class="margin-line"/>`;
 for(const p of points)svg+=`<circle cx="${p.x}" cy="${p.y}" r="4.2" class="margin-point"><title>${months[p.m-1]}: Margem EBITDA ${pct(p.margin)}</title></circle>`;
 svg+='</svg>';el('revenueChart').innerHTML=svg;
}
function renderDonut(rows){
 const names=['Marketplace A','Marketplace B','Loja online'];
 const a=sum(rows),colors=['#c06b45','#e1c7a5','#8e9b81'];
 const parts=names.map((name,i)=>({name,color:colors[i],net:sum(rows.filter(r=>r.canal===name)).receita_liquida}));
 let accum=0;
 const stops=parts.map(p=>{const x=a.receita_liquida>0?Math.max(0,p.net/a.receita_liquida*100):0;const stop=`${p.color} ${accum.toFixed(2)}% ${(accum+x).toFixed(2)}%`;accum+=x;return stop;}).join(',');
 const total=compact(a.receita_liquida);
 el('channelDonut').style.background=a.receita_liquida>0?`conic-gradient(${stops})`:'#e4e1dc';
 el('channelDonut').innerHTML=`<div class="donut-hole"><strong>${total}</strong><span>Receita líquida</span></div>`;
 el('channelDonut').setAttribute('aria-label','Distribuição por canal: '+parts.map(p=>`${p.name}, ${pct(safePct(p.net,a.receita_liquida))}`).join('; '));
 el('channelLegend').innerHTML=parts.map(p=>`<div class="donut-row"><span class="legend-bullet" style="background:${p.color}"></span><div class="donut-info"><div class="donut-name">${p.name}</div><div class="donut-money">${fmt(p.net)}</div></div><b>${pct(safePct(p.net,a.receita_liquida))}</b></div>`).join('');
}
function renderDreSummary(rows){
 const a=sum(rows),cost=a.receita_liquida-a.ebitda;
 const rowsToShow=[
  ['Receita líquida',fmt(a.receita_liquida),''],
  ['Custos e despesas','−'+fmt(Math.abs(cost)), 'cost'],
  ['EBITDA gerencial',fmt(a.ebitda),'highlight'],
  ['Margem EBITDA',pct(safePct(a.ebitda,a.receita_liquida)),''],
  ['Margem de contribuição',pct(safePct(a.margem_contribuicao,a.receita_liquida)),'']
 ];
 el('dreSummary').innerHTML=rowsToShow.map(([k,v,cl])=>`<div class="summary-line ${cl}"><span>${k}</span><strong>${v}</strong></div>`).join('');
 el('dreMiniPeriod').textContent=el('period').selectedOptions[0].textContent.replace(' / realizado simulado','').replace(' / fechamento estimado','')+' (R$)';
}
function bars(target,values,max){el(target).innerHTML=values.map(v=>`<div><div class="bar-head"><span>${v.name} <span class="muted">· ${pct(v.share)}</span></span><strong>${fmt(v.net)}</strong></div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(v.net>0?3:0,v.net/max*100).toFixed(2)}%"></div></div><div class="bar-sub">Margem de contribuição ${pct(v.margin)} · ${v.pedidos.toLocaleString('pt-BR')} pedidos</div></div>`).join('')}
function renderMix(rows){const a=sum(rows);for(const [target,key,options] of [['lineBars','linha',['Essencial','Premium','Acessórios']]]){const values=options.map(name=>{const t=sum(rows.filter(r=>r[key]===name));return {name,net:t.receita_liquida,share:safePct(t.receita_liquida,a.receita_liquida),margin:safePct(t.margem_contribuicao,t.receita_liquida),pedidos:t.pedidos}});bars(target,values,Math.max(1,...values.map(v=>v.net)))}}
const dreLines=[['receita_bruta','(+) Receita bruta',''],['deducoes','(-) Deduções',''],['receita_liquida','(=) Receita líquida','major'],['cmv','(-) CMV',''],['lucro_bruto','(=) Lucro bruto','major'],['taxas','(-) Taxas de venda',''],['frete','(-) Frete e logística',''],['margem_contribuicao','(=) Margem de contribuição','major'],['despesas_fixas','(-) Despesas fixas alocadas',''],['ebitda','(=) EBITDA gerencial','total']];
function dreTable(rows,budget,mini=false){const a=sum(rows),b=sum(budget);const lines=mini?dreLines.filter(x=>['receita_liquida','lucro_bruto','margem_contribuicao','despesas_fixas','ebitda'].includes(x[0])):dreLines;return `<table class="metric-table"><thead><tr><th>Conta gerencial</th><th>Simulado</th><th>Orçado</th><th>Desvio</th></tr></thead><tbody>${lines.map(([key,label,style])=>`<tr class="${style}"><td>${label}</td><td>${fmt(a[key])}</td><td>${fmt(b[key])}</td><td>${fmt(a[key]-b[key])}</td></tr>`).join('')}</tbody></table>`}
function renderDre(rows,budget){el('dreMini').innerHTML=dreTable(rows,budget,true);el('dreFull').innerHTML=dreTable(rows,budget,false);const a=sum(rows),b=sum(budget);let cm=safePct(a.margem_contribuicao,a.receita_liquida),net=safePct(a.ebitda,a.receita_liquida),breakeven=(cm>0)?a.despesas_fixas/(cm/100):NaN;el('profitStats').innerHTML=[['Margem bruta',pct(safePct(a.lucro_bruto,a.receita_liquida))],['Margem de contribuição',pct(cm)],['Margem EBITDA',pct(net)],['Ponto de equilíbrio gerencial',Number.isFinite(breakeven)?fmt(breakeven):'n/d'],['Orçamento EBITDA',fmt(b.ebitda)]].map(x=>`<div class="miniStat"><span class="tiny">${x[0]}</span><span class="tinystrong">${x[1]}</span></div>`).join('');const activeMonths=monthsOf();const tableRows=activeMonths.map(m=>{let r=sum(rows.filter(x=>x.mes===m)),b=sum(budget.filter(x=>x.mes===m)),isF=m>10;return `<tr><td>${months[m-1]}/26 ${isF?'<span style="color:#9b713a">(projetado)</span>':''}</td><td>${fmt(r.receita_liquida)}</td><td>${fmt(b.receita_liquida)}</td><td>${fmt(r.margem_contribuicao)}</td><td class="${r.ebitda<0?'negative':''}">${fmt(r.ebitda)}</td><td>${pct(safePct(r.ebitda,r.receita_liquida))}</td></tr>`}).join('');el('monthTable').innerHTML=`<table class="metric-table"><thead><tr><th>Mês</th><th>Receita líquida</th><th>Orçamento</th><th>Contribuição</th><th>EBITDA</th><th>Margem</th></tr></thead><tbody>${tableRows}</tbody></table>`}
function renderInsights(rows,budget){const a=sum(rows),b=sum(budget),channels=['Marketplace A','Marketplace B','Loja online'].map(name=>({name,sum:sum(rows.filter(r=>r.canal===name))}));channels.sort((x,y)=>safePct(x.sum.margem_contribuicao,x.sum.receita_liquida)-safePct(y.sum.margem_contribuicao,y.sum.receita_liquida));const available=channels.filter(x=>x.sum.receita_liquida>0);const poor=(available.length?available:channels)[0];const channelLead=available.length===1?'O canal selecionado':'Entre os canais do recorte, o canal com menor margem de contribuição';const d=a.ebitda-b.ebitda;const fx=safePct(a.despesas_fixas,a.receita_liquida);el('insights').innerHTML=`<div class="insight"><strong>Desempenho frente ao orçamento</strong><br>O EBITDA está ${d>=0?'acima':'abaixo'} do planejado em <strong>${fmt(Math.abs(d))}</strong>, no mesmo recorte de meses e dimensões.</div><div class="insight"><strong>Pressão de estrutura</strong><br>As despesas fixas alocadas representam <strong>${pct(fx)}</strong> da receita líquida selecionada. O rateio é gerencial, não contábil.</div><div class="insight"><strong>Leitura por canal</strong><br>${channelLead}: <strong>${poor.name}</strong>, com margem de contribuição de <strong>${pct(safePct(poor.sum.margem_contribuicao,poor.sum.receita_liquida))}</strong>. Investigar preço, CMV, taxas e logística antes de decidir.</div>`}
function scenario(g,eff){const annual=Array.from({length:12},(_,i)=>i+1);return sum(getRows(annual,g,eff))}
function renderScenarios(){const cur=scenario(state.growth,state.eff),base=scenario(0,0),cm=safePct(cur.margem_contribuicao,cur.receita_liquida);el('scRevenue').textContent=fmt(cur.receita_liquida);el('scEbitda').textContent=fmt(cur.ebitda);el('scEbitda').className='tinystrong '+(cur.ebitda<0?'negative':'positive');el('scMargin').textContent=pct(safePct(cur.ebitda,cur.receita_liquida));el('scDelta').textContent=fmt(cur.ebitda-base.ebitda);el('scBreakEven').textContent=cm>0?fmt(cur.despesas_fixas/(cm/100)):'n/d';el('growthDisplay').textContent=(state.growth>0?'+':'')+state.growth+'%';el('effDisplay').textContent=state.eff+'%';const presets=[['Conservador',-8,0],['Base',0,0],['Otimista',10,4]];el('scenarioCards').innerHTML=presets.map(([name,g,e])=>{const x=scenario(g,e);let on=g===state.growth&&e===state.eff;return `<div class="scenario-card ${on?'selected':''}"><div class="tinystrong">${name}</div><div class="tiny">Receita ${g>0?'+':''}${g}% · Eficiência ${e}%</div><div class="big ${x.ebitda<0?'negative':''}">${fmt(x.ebitda)}</div><div class="tiny">EBITDA estimado no ano</div><div class="miniStat"><span class="tiny">Receita líquida</span><strong>${fmt(x.receita_liquida)}</strong></div><div class="miniStat"><span class="tiny">Margem</span><strong>${pct(safePct(x.ebitda,x.receita_liquida))}</strong></div></div>`}).join('')}
function refresh(){const rows=getRows(),budget=getBudget();renderKpis(rows,budget);renderChart(rows,budget);renderDonut(rows);renderDreSummary(rows);renderMix(rows);renderDre(rows,budget);renderInsights(rows,budget);renderScenarios();el('disclaimer').innerHTML=`<strong>Base 100% sintética.</strong> ${state.period==='full'||state.period==='h2'?'Jan–Out são valores simulados como realizados; Nov–Dez são projeções ilustrativas ajustáveis.':'O recorte selecionado utiliza observações fictícias do período, não resultados de empresa real.'} Orçamento e resultado são comparados apenas nos mesmos meses e dimensões.`}
function setTab(name){state.tab=name;for(const b of document.querySelectorAll('.navbtn')){b.classList.toggle('active',b.dataset.tab===name);b.setAttribute('aria-pressed',String(b.dataset.tab===name))};for(const n of ['executiva','dre','cenarios','engenharia'])el('tab-'+n).classList.toggle('hidden',n!==name);}
for(const b of document.querySelectorAll('.navbtn'))b.addEventListener('click',()=>setTab(b.dataset.tab));
for(const [id,k] of [['period','period'],['channel','channel'],['line','line']])el(id).addEventListener('change',e=>{state[k]=e.target.value;refresh()});
el('reset').addEventListener('click',()=>{state.period='ytd';state.channel='*';state.line='*';for(const id of ['period','channel','line'])el(id).value=state[id==='line'?'line':id];refresh()});
function setSc(g,e){state.growth=g;state.eff=e;el('growth').value=g;el('eff').value=e;for(const b of document.querySelectorAll('.preset'))b.classList.toggle('active',b.dataset.preset===(g===-8&&e===0?'conservador':g===0&&e===0?'base':g===10&&e===4?'otimista':'manual'));refresh()}
for(const b of document.querySelectorAll('.preset'))b.addEventListener('click',()=>{const x=b.dataset.preset==='conservador'?[-8,0]:b.dataset.preset==='otimista'?[10,4]:[0,0];setSc(...x)});
for(const [id,k] of [['growth','growth'],['eff','eff']])el(id).addEventListener('input',e=>{state[k]=Number(e.target.value);document.querySelectorAll('.preset').forEach(b=>b.classList.remove('active'));refresh()});
el('auditValid').textContent=model.resumo.linhas_validas;el('auditRejected').textContent=model.resumo.linhas_rejeitadas;el('auditProjected').textContent=model.resumo.linhas_projetadas;
el('exportCsv').addEventListener('click',()=>{const rows=getRows();const hdr=['mes','canal','linha','tipo','pedidos',...fields];const csv=[hdr.join(';'),...rows.map(r=>hdr.map(f=>String(r[f]).replaceAll(';',',')).join(';'))].join('\n');const bom='\ufeff';const link=document.createElement('a');const url=URL.createObjectURL(new Blob([bom+csv],{type:'text/csv;charset=utf-8'}));link.href=url;link.download='case03_recorte_financeiro.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),500)});
refresh();
})();

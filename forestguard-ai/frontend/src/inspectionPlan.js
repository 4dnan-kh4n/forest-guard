import {annualChange} from './annualChange.js';

export function inspectionItems(report) {
  return (report?.comparisons||[]).filter(pair=>annualChange(pair)&&pair.suspected_tree_proxy_loss_ha>0&&
      [pair.suspected_tree_proxy_loss_ha,pair.suspected_tree_proxy_gain_ha,pair.common_area_ha,pair.common_coverage_percent].every(value=>Number.isFinite(value)&&value>=0))
    .sort((a,b)=>b.suspected_tree_proxy_loss_ha-a.suspected_tree_proxy_loss_ha)
    .map(pair=>({id:`${pair.before_year}-${pair.after_year}`,year:pair.after_year,
      title:`Review ${pair.before_year}–${pair.after_year} tree-cover change`,
      before:pair.before_date,after:pair.after_date,loss:pair.suspected_tree_proxy_loss_ha,
      gain:pair.suspected_tree_proxy_gain_ha,coverage:pair.common_coverage_percent,area:pair.common_area_ha}));
}

export function inspectionCsv(items) {
  const quote=value=>'"'+String(value).replace(/^[=+@-]/,"'$&").replaceAll('"','""')+'"';
  const rows=[['Mapped area','Action','Before image','After image','Possible loss ha','Possible gain ha','Compared area ha','Clear coverage %','Basis'],
    ...items.map(item=>['Joga / compartment 279',item.title,item.before,item.after,item.loss.toFixed(2),item.gain.toFixed(2),item.area.toFixed(2),item.coverage.toFixed(1),'Satellite model estimate; review required'])];
  return '\ufeff'+rows.map(row=>row.map(quote).join(',')).join('\r\n')+'\r\n';
}

// Exercise the actual API helper with hypothetical HTTP responses, without a browser/network.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../frontend/src/main.jsx'),'utf8');
const helper=source.slice(source.indexOf('async function api('),source.indexOf('function MapPane(')).trim();
async function check(){
 for(const status of [200,401,503]){
  const events=[];
  const api=vm.runInNewContext('('+helper+')',{fetch:async()=>({status,ok:status===200,headers:{get:()=> 'application/json'},json:async()=>({detail:'test response',value:42})}),window:{dispatchEvent:e=>events.push(e.type)},Event:class{constructor(type){this.type=type;}}});
  if(status===200)assert.equal((await api('/api/research/proxy')).value,42);
  else await assert.rejects(api('/api/research/proxy'),/test response/);
  assert.deepEqual(events,status===401?['forestguard-session-expired']:[]);
 }
 const api=vm.runInNewContext('('+helper+')',{fetch:async()=>({headers:{get:()=> 'text/html'}})});
 await assert.rejects(api('/api/research/proxy'),/did not return JSON/);
 console.log(JSON.stringify({status:'PASS',actual_client_helper_exercised:true,hypothetical_http_responses:true,rejected_session_event_checked:true,data_errors_do_not_trigger_session_expiry:true,non_json_rejected:true}));
}
check().catch(error=>{console.error(error);process.exitCode=1;});

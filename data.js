/* ===== 每日只需更新本文件 =====
 * 1) 改 meta/headline/summary/sections/calendar 文字
 * 2) 在 views 追加新观点（页面自动按行情评价命中与否）
 * 3) series 换成真实数据：{name,unit,type:'px'|'rate',dates:[...],values:[...]}
 *    下方为【演示用随机数据】，上线前请替换，并把 meta.demo 改为 false
 */
(function () {
  function rng(s){return function(){s|=0;s=s+0x6D2B79F5|0;let t=Math.imul(s^s>>>15,1|s);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
  function bdays(end,n){const o=[];let d=new Date(end+'T00:00:00Z');while(o.length<n){const w=d.getUTCDay();if(w&&w<6)o.push(d.toISOString().slice(0,10));d=new Date(d-864e5)}return o.reverse()}
  const dates=bdays('2026-11-12',300);
  const mul=(seed,s,vol,dr,dec)=>{const r=rng(seed);let v=s;return dates.map(()=>{v*=1+dr+vol*(r()+r()+r()-1.5)*1.15;return +v.toFixed(dec)})};
  const add=(seed,s,vol,lo,hi,dec)=>{const r=rng(seed);let v=s;return dates.map(()=>{v+=vol*(r()+r()+r()-1.5)*1.15;v=Math.min(hi,Math.max(lo,v));return +v.toFixed(dec)})};
  const S=(name,unit,type,values)=>({name,unit,type,dates,values});

  window.DATA = {
    meta:{ title:"宏观经济日报", org:"某某研究院 · 宏观策略组", date:"2026-11-12", issue:"第 312 期", demo:true },
    headline:"通胀降温预期升温，美债收益率回落，风险偏好温和修复",
    summary:[
      "美国10Y国债收益率小幅回落，市场继续交易年内降息路径，美元指数承压。",
      "国内政策发力窗口期，关注社融与信贷结构，人民币汇率维持区间波动。",
      "大宗：原油受库存数据扰动震荡，黄金处于高位整理。",
      "风险提示：地缘冲突、美联储沟通口径偏鹰、海外增长放缓超预期。"
    ],
    sections:[
      {title:"一、全球市场",body:["权益：美股窄幅整理，成长风格占优；欧股受能源价格拖累。","利率：美债曲线趋于陡峭化，2s10s 利差小幅走阔。","汇率：美元指数回落，非美货币普遍反弹。"]},
      {title:"二、中国宏观",body:["高频数据显示内需修复仍偏温和，地产链条仍是主要拖累。","政策层面继续强调逆周期调节，财政节奏与专项债发行值得跟踪。","人民币：中间价稳定，波动率处于低位。"]},
      {title:"三、策略观点",body:["短期（1个月）：权益中性偏多，黄金逢低配置，美元谨慎。","中期（3个月）：关注利率下行带来的久期机会，警惕通胀二次反弹。"]}
    ],
    calendar:[
      {d:"11-13",t:"21:30",c:"美国",e:"10月 PPI 同比",imp:2},
      {d:"11-14",t:"09:30",c:"中国",e:"10月 CPI / PPI 同比",imp:3},
      {d:"11-14",t:"21:30",c:"美国",e:"零售销售月率",imp:3},
      {d:"11-17",t:"10:00",c:"中国",e:"10月 工业增加值、社零、固投",imp:3},
      {d:"11-19",t:"03:00",c:"美国",e:"FOMC 会议纪要",imp:2}
    ],
    /* 观点追踪：asset 对应 series 键；dir: 1看多/上行，-1看空/下行；h: 评价窗口（交易日） */
    views:[
      {date:"2026-06-15",asset:"GOLD",dir:1,h:20,text:"黄金逢低配置"},
      {date:"2026-07-20",asset:"SPX",dir:1,h:20,text:"美股成长风格占优"},
      {date:"2026-08-24",asset:"DXY",dir:-1,h:20,text:"降息预期下美元走弱"},
      {date:"2026-09-14",asset:"UST10",dir:-1,h:20,text:"美债收益率中枢下移"},
      {date:"2026-09-28",asset:"WTI",dir:-1,h:20,text:"原油供给宽松，上方受限"},
      {date:"2026-10-12",asset:"SPX",dir:1,h:20,text:"风险偏好修复，权益偏多"},
      {date:"2026-10-26",asset:"USDCNY",dir:-1,h:15,text:"人民币区间偏强"},
      {date:"2026-11-05",asset:"GOLD",dir:1,h:20,text:"黄金高位整理后看多"}
    ],
    series:{
      SPX:S("标普500","点","px",mul(11,6000,.0075,.0003,2)),
      UST10:S("美国10Y国债","%","rate",add(12,4.3,.035,3.2,5.0,3)),
      CN10:S("中国10Y国债","%","rate",add(13,1.9,.012,1.5,2.4,3)),
      DXY:S("美元指数","","px",mul(14,104,.0035,-.00015,2)),
      USDCNY:S("USD/CNY","","px",mul(15,7.2,.0013,-.00005,4)),
      GOLD:S("黄金","美元/盎司","px",mul(16,2900,.0085,.0008,1)),
      WTI:S("WTI原油","美元/桶","px",mul(17,72,.016,-.0003,2)),
      VIX:S("VIX","","rate",add(18,17,.7,11,38,2))
    }
  };
})();

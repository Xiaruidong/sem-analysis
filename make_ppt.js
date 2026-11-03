const pptxgen = require("C:\\Users\\13223\\AppData\\Roaming\\npm\\node_modules\\pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "工作总结汇报";

// 商务简洁配色:白底 + 深藏蓝主色 + 橙色点缀
const BG = "FFFFFF", PRIMARY = "1B3A6B", ACCENT = "E8590C", TEXT = "1E293B", MUTED = "64748B", TINT = "F2F5FA";

const W = 13.33, H = 7.5, M = 0.6;
const F = "微软雅黑";

let s = pres.addSlide();
s.background = { color: BG };

// 标题区
s.addText("2026年第三季度工作总结", {
  x: M, y: 0.45, w: 9, h: 0.7, fontSize: 34, bold: true, color: PRIMARY, fontFace: F, margin: 0,
});
s.addText("汇报人:张三  |  汇报日期:2026年11月2日  |  部门:产品技术部", {
  x: M, y: 1.15, w: 9, h: 0.35, fontSize: 13, color: MUTED, fontFace: F, margin: 0,
});

// 右上角核心结论
s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 9.4, y: 0.45, w: 3.33, h: 1.05, fill: { color: PRIMARY }, rectRadius: 0.08,
});
s.addText([
  { text: "整体结论", options: { fontSize: 11, color: "AFC4E8", breakLine: true } },
  { text: "核心目标达成率 112%", options: { fontSize: 16, bold: true, color: "FFFFFF" } },
], { x: 9.6, y: 0.45, w: 3.0, h: 1.05, valign: "middle", fontFace: F, margin: 0 });

// 三大 KPI
const kpi = [
  { num: "98.6%", label: "任务按时完成率", sub: "环比 +4.2 pct" },
  { num: "35项", label: "交付重点任务", sub: "其中 6 项为公司级" },
  { num: "12个", label: "流程优化落地", sub: "平均提效约 20%" },
];
const kw = (W - 2 * M - 0.8) / 3;
kpi.forEach((k, i) => {
  const x = M + i * (kw + 0.4);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y: 1.85, w: kw, h: 1.55, fill: { color: TINT }, rectRadius: 0.08,
  });
  s.addText([
    { text: k.num, options: { fontSize: 40, bold: true, color: i === 0 ? ACCENT : PRIMARY, breakLine: true } },
    { text: k.label + "   ", options: { fontSize: 14, bold: true, color: TEXT } },
    { text: k.sub, options: { fontSize: 11, color: MUTED } },
  ], { x: x + 0.25, y: 1.85, w: kw - 0.5, h: 1.55, valign: "middle", fontFace: F, margin: 0 });
});

// 左:主要成果
s.addText("主要成果", { x: M, y: 3.75, w: 4, h: 0.4, fontSize: 19, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
const bu = () => ({ code: "25B8", indent: 12 });
s.addText([
  { text: "重点项目全部按期交付,客户满意度评分 4.8/5", options: { bullet: bu(), breakLine: true } },
  { text: "推动跨部门协作机制落地,需求响应周期缩短 30%", options: { bullet: bu(), breakLine: true } },
  { text: "完成团队能力建设,组织内部培训 8 场、覆盖 120 人次", options: { bullet: bu(), breakLine: true } },
  { text: "沉淀标准化文档 15 份,新人上手周期由 4 周缩至 2 周", options: { bullet: bu() } },
], {
  x: M, y: 4.25, w: 6.7, h: 2.4, fontSize: 14, color: TEXT, fontFace: F,
  paraSpaceAfter: 12, margin: 0, valign: "top",
});

// 右:下阶段计划(带编号)
s.addText("下阶段计划(Q4)", { x: 7.9, y: 3.75, w: 4, h: 0.4, fontSize: 19, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
const plans = [
  { n: "01", t: "推进系统迭代升级,12月中旬完成上线" },
  { n: "02", t: "建立数据看板体系,实现核心指标可视化" },
  { n: "03", t: "启动两项流程自动化改造,目标再提效 15%" },
];
plans.forEach((p, i) => {
  const y = 4.3 + i * 0.85;
  s.addText(p.n, { x: 7.9, y, w: 0.55, h: 0.55, fontSize: 20, bold: true, color: ACCENT, fontFace: F, margin: 0 });
  s.addText(p.t, { x: 8.55, y: y + 0.02, w: 4.1, h: 0.7, fontSize: 14, color: TEXT, fontFace: F, margin: 0, valign: "top" });
});

// 底部来源说明
s.addText("注:以上数据统计周期为 2026年7月–9月,来源:部门月度经营分析报表。", {
  x: M, y: 7.0, w: 12, h: 0.3, fontSize: 10.5, color: MUTED, fontFace: F, margin: 0,
});

pres.writeFile({ fileName: "D:\\vue_project\\jinxiangshibie\\工作总结汇报.pptx" }).then(() => console.log("done"));

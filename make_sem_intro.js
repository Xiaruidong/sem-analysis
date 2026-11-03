const pptxgen = require("C:\\Users\\13223\\AppData\\Roaming\\npm\\node_modules\\pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Xiaruidong";
pres.title = "SEM 图像自动定量分析系统 · 项目介绍";

const BG = "FFFFFF", PRIMARY = "1B3A6B", ACCENT = "E8590C", TEXT = "1E293B", MUTED = "64748B", TINT = "F2F5FA", DARK = "14284B";
const W = 13.33, H = 7.5, M = 0.6;
const F = "微软雅黑";
const bu = () => ({ code: "25B8", indent: 12 });

/* ============ 1 封面(深色) ============ */
let s1 = pres.addSlide();
s1.background = { color: DARK };
s1.addText("SEM 图像自动定量分析系统", {
  x: M, y: 2.3, w: 12, h: 1.0, fontSize: 48, bold: true, color: "FFFFFF", fontFace: F, margin: 0,
});
s1.addText("电池材料微观表征 · 从人工读图到一键定量", {
  x: M, y: 3.4, w: 12, h: 0.5, fontSize: 20, color: "AFC4E8", fontFace: F, margin: 0,
});
s1.addText([
  { text: "118 张 JEOL SEM 图像验证", options: { color: "FFFFFF", bold: true } },
  { text: "   ·   像素标定全自动   ·   Web 化分析   ·   项目介绍", options: { color: "AFC4E8" } },
], { x: M, y: 4.15, w: 12, h: 0.4, fontSize: 14, fontFace: F, margin: 0 });
s1.addText("汇报人:Xiaruidong   |   2026年11月", {
  x: M, y: 6.6, w: 8, h: 0.35, fontSize: 13, color: "7D93BE", fontFace: F, margin: 0,
});

/* ============ 2 项目背景与价值 ============ */
let s2 = pres.addSlide();
s2.background = { color: BG };
s2.addText("项目背景与价值", { x: M, y: 0.45, w: 9, h: 0.65, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s2.addText("为什么要把 SEM 图像分析做成自动化系统", { x: M, y: 1.12, w: 9, h: 0.35, fontSize: 14, color: MUTED, fontFace: F, margin: 0 });

// 左:痛点
s2.addText("现状痛点 · 人工分析", { x: M, y: 1.9, w: 5.6, h: 0.4, fontSize: 18, bold: true, color: TEXT, fontFace: F, margin: 0 });
s2.addText([
  { text: "颗粒、涂层、孔隙全靠人工在图像软件上逐个测量", options: { bullet: bu(), breakLine: true } },
  { text: "单张图测量耗时数分钟,批量数据(百余张)难以覆盖", options: { bullet: bu(), breakLine: true } },
  { text: "人工选点主观性强,多人测量结果不可复现", options: { bullet: bu(), breakLine: true } },
  { text: "像素→微米换算依赖手工量尺,易引入系统误差", options: { bullet: bu() } },
], { x: M, y: 2.4, w: 5.7, h: 2.6, fontSize: 14, color: TEXT, fontFace: F, paraSpaceAfter: 10, margin: 0, valign: "top" });

// 右:目标
s2.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y: 1.9, w: 5.83, h: 3.3, fill: { color: TINT }, rectRadius: 0.1 });
s2.addText("项目目标 · 一键定量", { x: 7.2, y: 2.1, w: 5.3, h: 0.4, fontSize: 18, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s2.addText([
  { text: "读取图像元数据自动完成像素标定,零人工量尺", options: { bullet: bu(), breakLine: true } },
  { text: "颗粒统计 / 涂层厚度 / 孔隙参数三类分析全覆盖", options: { bullet: bu(), breakLine: true } },
  { text: "批量分析 0.5 秒/张,结果自动标注并可视化", options: { bullet: bu(), breakLine: true } },
  { text: "统一算法口径,测量结果可复现、可追溯", options: { bullet: bu() } },
], { x: 7.2, y: 2.6, w: 5.3, h: 2.4, fontSize: 14, color: TEXT, fontFace: F, paraSpaceAfter: 10, margin: 0, valign: "top" });

// 底部价值条
const vals = [
  { n: "0.5 s/张", t: "批量分析速度" },
  { n: "0.2% CV", t: "涂层厚度精度" },
  { n: "3 大模块", t: "颗粒·膜厚·孔隙" },
  { n: "118 张", t: "真实数据验证" },
];
vals.forEach((v, i) => {
  const x = M + i * ((W - 2 * M) / 4);
  s2.addText([
    { text: v.n, options: { fontSize: 26, bold: true, color: i === 1 ? ACCENT : PRIMARY, breakLine: true } },
    { text: v.t, options: { fontSize: 13, color: MUTED } },
  ], { x, y: 5.5, w: (W - 2 * M) / 4 - 0.3, h: 1.2, fontFace: F, margin: 0, valign: "top" });
});

/* ============ 3 技术路径总览(流程图) ============ */
let s3 = pres.addSlide();
s3.background = { color: BG };
s3.addText("技术路径总览", { x: M, y: 0.45, w: 9, h: 0.65, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s3.addText("从原始 BMP 到可交付数据的全自动流水线", { x: M, y: 1.12, w: 9, h: 0.35, fontSize: 14, color: MUTED, fontFace: F, margin: 0 });

const steps = [
  { t: "图像接入", d: "JEOL BMP +\n同名 .txt 元数据" },
  { t: "像素标定", d: "解析标尺/放大倍数\nμm/px 自动换算" },
  { t: "预处理", d: "裁信息栏·去噪\n衬度归一化" },
  { t: "目标分割", d: "Otsu / 梯度分水岭\n拆分粘连颗粒" },
  { t: "定量测量", d: "逐颗粒/逐列测量\n亚像素边界定位" },
  { t: "统计输出", d: "D10/D50/D90\n标注图 · Web 呈现" },
];
const sw = 1.85, gap = 0.22, total = steps.length * sw + (steps.length - 1) * gap;
const sx0 = (W - total) / 2;
steps.forEach((st, i) => {
  const x = sx0 + i * (sw + gap);
  s3.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y: 2.0, w: sw, h: 1.7, fill: { color: i === 3 ? PRIMARY : TINT }, rectRadius: 0.08,
  });
  s3.addText([
    { text: `0${i + 1}`, options: { fontSize: 13, bold: true, color: i === 3 ? "AFC4E8" : ACCENT, breakLine: true } },
    { text: st.t, options: { fontSize: 16, bold: true, color: i === 3 ? "FFFFFF" : TEXT, breakLine: true } },
    { text: st.d, options: { fontSize: 10.5, color: i === 3 ? "D7E2F4" : MUTED } },
  ], { x: x + 0.14, y: 2.0, w: sw - 0.28, h: 1.7, fontFace: F, margin: 0, valign: "middle" });
});
// 箭头
steps.forEach((_, i) => {
  if (i < steps.length - 1) {
    const x = sx0 + (i + 1) * (sw + gap) - gap;
    s3.addText("→", { x: x - 0.03, y: 2.55, w: gap + 0.1, h: 0.5, fontSize: 18, bold: true, color: MUTED, fontFace: F, align: "center", margin: 0 });
  }
});
// 关键技术说明
s3.addText("三项关键技术", { x: M, y: 4.15, w: 5, h: 0.4, fontSize: 18, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s3.addText([
  { text: "元数据驱动标定:直接读取 $$SM_MICRON_BAR / $$CM_MAG 字段,无标尺时按放大倍数兜底,支持手工校正", options: { bullet: bu(), breakLine: true } },
  { text: "梯度分水岭分割:针对紧密堆积粉体,灰度梯度标记 + 分水岭拆分粘连颗粒,优于传统单一阈值法", options: { bullet: bu(), breakLine: true } },
  { text: "亚像素边界定位:全局剖面定初值 + 逐列梯度极值抛物线插值,厚度测量变异系数低至 0.2%", options: { bullet: bu() } },
], { x: M, y: 4.65, w: 12.1, h: 1.9, fontSize: 14, color: TEXT, fontFace: F, paraSpaceAfter: 10, margin: 0, valign: "top" });

/* ============ 4 核心模块 ============ */
let s4 = pres.addSlide();
s4.background = { color: BG };
s4.addText("核心功能模块", { x: M, y: 0.45, w: 9, h: 0.65, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s4.addText("三大定量分析模块均已上线并通过真实数据验证", { x: M, y: 1.12, w: 9, h: 0.35, fontSize: 14, color: MUTED, fontFace: F, margin: 0 });

const mods = [
  {
    n: "01", title: "粉末颗粒统计",
    points: ["颗粒计数与等效直径、长径比、圆度等形貌参数", "粒度分布 D10 / D50 / D90 一键输出", "梯度分水岭分割,适配紧密堆积粉体", "最小粒径按物理尺度(μm)过滤碎屑"],
    stat: "0.5 s/张 · 批量分析",
  },
  {
    n: "02", title: "涂层 / 膜厚",
    points: ["截面图自动识别多层结构", "逐列多点测量 + 亚像素边界定位", "倾斜校正 + MAD 外点剔除", "多点统计给出均值 ± 标准差与 CV"],
    stat: "199.53 ± 0.45 μm · CV 0.2%",
  },
  {
    n: "03", title: "孔隙参数",
    points: ["2D 面分析法:孔隙率 = 黑色区域占比", "固定阈值 / Otsu / 自适应三种二值化", "阈值可调,兼顾不同衬度图像", "孔径分布 D10 / D50 / D90"],
    stat: "样例 4.08%(阈值100)",
  },
];
const mw = (W - 2 * M - 0.8) / 3;
mods.forEach((m, i) => {
  const x = M + i * (mw + 0.4);
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: mw, h: 4.7, fill: { color: TINT }, rectRadius: 0.1 });
  s4.addText([
    { text: m.n + "  ", options: { fontSize: 22, bold: true, color: ACCENT } },
    { text: m.title, options: { fontSize: 19, bold: true, color: PRIMARY } },
  ], { x: x + 0.25, y: 1.95, w: mw - 0.5, h: 0.5, fontFace: F, margin: 0 });
  s4.addText(
    m.points.map((p, j) => ({ text: p, options: { bullet: bu(), breakLine: j < m.points.length - 1 } })),
    { x: x + 0.25, y: 2.55, w: mw - 0.5, h: 2.6, fontSize: 12.5, color: TEXT, fontFace: F, paraSpaceAfter: 8, margin: 0, valign: "top" }
  );
  s4.addText(m.stat, { x: x + 0.25, y: 5.6, w: mw - 0.5, h: 0.6, fontSize: 13.5, bold: true, color: ACCENT, fontFace: F, margin: 0, valign: "middle" });
});

/* ============ 5 系统架构 ============ */
let s5 = pres.addSlide();
s5.background = { color: BG };
s5.addText("系统架构", { x: M, y: 0.45, w: 9, h: 0.65, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s5.addText("轻量独立部署:单一 Python 服务同时提供 API 与 Web 界面", { x: M, y: 1.12, w: 9, h: 0.35, fontSize: 14, color: MUTED, fontFace: F, margin: 0 });

// 三层架构
const layers = [
  { t: "Web 前端层", d: "单页应用(原生 HTML/JS):图像浏览 · 参数配置 · 标注图与统计图表展示,由后端直接托管,无需独立部署", c: TINT, tc: TEXT },
  { t: "服务层(FastAPI,端口 8001)", d: "REST API:/api/sem/analyze(颗粒)· /api/sem/thickness(膜厚)· /api/sem/porosity(孔隙)· /api/sem/calibrate(标定);结果目录挂载静态服务", c: PRIMARY, tc: "FFFFFF" },
  { t: "算法层(app/sem 四模块)", d: "calibration 元数据标定 · particles 颗粒分割与测量 · thickness 亚像素膜厚 · porosity 孔隙分析;基于 OpenCV + NumPy,不依赖重型深度学习框架", c: TINT, tc: TEXT },
];
layers.forEach((l, i) => {
  const y = 1.85 + i * 1.45;
  s5.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: M, y, w: 9.0, h: 1.25, fill: { color: l.c }, rectRadius: 0.08 });
  s5.addText([
    { text: l.t, options: { fontSize: 16, bold: true, color: l.c === PRIMARY ? "FFFFFF" : PRIMARY, breakLine: true } },
    { text: l.d, options: { fontSize: 12, color: l.tc } },
  ], { x: M + 0.25, y: y + 0.1, w: 8.5, h: 1.05, fontFace: F, margin: 0, valign: "middle" });
});
// 右侧:部署特性
s5.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.0, y: 1.85, w: 2.73, h: 4.15, fill: { color: DARK }, rectRadius: 0.08 });
s5.addText([
  { text: "部署特性", options: { fontSize: 15, bold: true, color: "FFFFFF", breakLine: true } },
  { text: "", options: { fontSize: 6, breakLine: true } },
  { text: "一条命令启动", options: { fontSize: 12.5, bold: true, color: "AFC4E8", breakLine: true } },
  { text: "python run_sem.py", options: { fontSize: 11, color: "FFFFFF", breakLine: true } },
  { text: "", options: { fontSize: 6, breakLine: true } },
  { text: "无需数据库与 GPU", options: { fontSize: 12.5, bold: true, color: "AFC4E8", breakLine: true } },
  { text: "", options: { fontSize: 6, breakLine: true } },
  { text: "跨平台", options: { fontSize: 12.5, bold: true, color: "AFC4E8", breakLine: true } },
  { text: "Windows / Linux / Docker", options: { fontSize: 11, color: "FFFFFF" } },
], { x: 10.2, y: 2.05, w: 2.35, h: 3.8, fontFace: F, margin: 0, valign: "top" });
s5.addText("数据流:BMP/TXT 读入 → 内存分析 → 标注图与 JSON 落盘 storage/results → 前端经 /results 静态访问", {
  x: M, y: 6.3, w: 12.1, h: 0.4, fontSize: 12.5, color: MUTED, fontFace: F, margin: 0,
});

/* ============ 6 验证数据与成果 ============ */
let s6 = pres.addSlide();
s6.background = { color: BG };
s6.addText("验证数据与阶段性成果", { x: M, y: 0.45, w: 9, h: 0.65, fontSize: 30, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
s6.addText("已在 118 张真实 JEOL SEM 图像(正极/负极粉末、涂层截面、EDS 系列)上完成验证", { x: M, y: 1.12, w: 12, h: 0.35, fontSize: 14, color: MUTED, fontFace: F, margin: 0 });

const rows = [
  { k: "像素标定", v: "JEOL 标尺元数据直读,无标尺图像按放大倍数兜底;修复中文路径 / 缺元数据场景,支持手工标定", tag: "全自动" },
  { k: "涂层厚度", v: "全局初值 + 逐列亚像素定位,多点统计;样例 Chery 59-1(350×)主涂层 199.53 ± 0.45 μm,CV 0.2%", tag: "高精度" },
  { k: "颗粒统计", v: "等效直径 / 长径比 / 圆度 / 粒度分布 D10-D90;梯度分水岭解决紧密堆积粉体粘连拆分", tag: "批量 0.5s/张" },
  { k: "孔隙分析", v: "2D 面分析孔隙率 + 孔径分布;阈值可调,样例孔隙率 4.08%(阈值 100)", tag: "多方法" },
];
rows.forEach((r, i) => {
  const y = 1.75 + i * 1.13;
  s6.addText(r.k, { x: M, y: y + 0.05, w: 1.7, h: 0.5, fontSize: 16, bold: true, color: PRIMARY, fontFace: F, margin: 0 });
  s6.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.5, y, w: 1.5, h: 0.55, fill: { color: PRIMARY }, rectRadius: 0.06 });
  s6.addText(r.tag, { x: 2.5, y, w: 1.5, h: 0.55, fontSize: 11.5, bold: true, color: "FFFFFF", fontFace: F, align: "center", valign: "middle", margin: 0 });
  s6.addText(r.v, { x: 4.35, y: y - 0.05, w: 8.3, h: 0.95, fontSize: 13, color: TEXT, fontFace: F, margin: 0, valign: "middle" });
});
// 分隔线
for (let i = 1; i < rows.length; i++) {
  const y = 1.75 + i * 1.13 - 0.12;
  s6.addShape(pres.shapes.LINE, { x: M, y, w: W - 2 * M, h: 0, line: { color: "E2E8F0", width: 0.75 } });
}

/* ============ 7 规划(深色收尾) ============ */
let s7 = pres.addSlide();
s7.background = { color: DARK };
s7.addText("下一步规划", { x: M, y: 0.6, w: 9, h: 0.7, fontSize: 32, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
s7.addText("从「可用」走向「好用」:深度学习增强 · 数据维度扩展 · 报告自动化", { x: M, y: 1.35, w: 11, h: 0.4, fontSize: 15, color: "AFC4E8", fontFace: F, margin: 0 });

const plans = [
  { n: "01", t: "深度学习分割", d: "引入 Cellpose / SAM 解决弱衬度晶界识别,提升复杂显微组织的分割鲁棒性" },
  { n: "02", t: "EDS 数据接入", d: "元素面分布图解析,实现包覆层成分分析与包覆厚度定量" },
  { n: "03", t: "报告自动化", d: "Excel / PDF 一键生成,含标注图、统计图表与批次汇总" },
  { n: "04", t: "缺陷检测模块", d: "裂纹、掉料等典型缺陷的自动检出与计数,服务产线质量监控" },
];
plans.forEach((p, i) => {
  const x = M + (i % 2) * 6.2, y = 2.2 + Math.floor(i / 2) * 1.9;
  s7.addText(p.n, { x, y, w: 0.8, h: 0.7, fontSize: 30, bold: true, color: ACCENT, fontFace: F, margin: 0 });
  s7.addText(p.t, { x: x + 0.85, y: y + 0.02, w: 4.9, h: 0.4, fontSize: 17, bold: true, color: "FFFFFF", fontFace: F, margin: 0 });
  s7.addText(p.d, { x: x + 0.85, y: y + 0.45, w: 4.9, h: 1.2, fontSize: 12.5, color: "AFC4E8", fontFace: F, margin: 0, valign: "top" });
});
s7.addText("SEM 图像自动定量分析系统 · 电池材料微观表征", {
  x: M, y: 6.6, w: 10, h: 0.35, fontSize: 12, color: "7D93BE", fontFace: F, margin: 0,
});

pres.writeFile({ fileName: "D:\\vue_project\\jinxiangshibie\\SEM项目介绍.pptx" }).then(() => console.log("done"));

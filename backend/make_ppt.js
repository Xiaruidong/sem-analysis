const pptxgen = require("pptxgenjs");
const path = require("path");

const IMG = p => path.resolve("D:/vue_project/jinxiangshibie/storage/results/sem/annotated", p);

// 配色：SEM 电镜暗色主题
const BG = "0D1521";      // 近黑深蓝（电镜屏）
const CARD = "16202E";    // 卡片底
const PRIMARY = "4FC3F7"; // 电镜荧光青
const ACCENT = "F5A623";  // 琥珀（标注色）
const TEXT = "EAF2F8";
const MUTED = "8DA3B5";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "SEM分析";
pres.title = "SEM图像自动定量分析系统进展";

const W = 13.33, H = 7.5, M = 0.5;
const s = pres.addSlide();
s.background = { color: BG };

// ── 标题区 ──
s.addText("SEM 图像自动定量分析系统", {
  x: M, y: 0.32, w: 8.5, h: 0.62, margin: 0,
  fontSize: 30, bold: true, color: TEXT, fontFace: "微软雅黑",
});
s.addText("电池材料微观表征 · 本周进展", {
  x: M, y: 0.94, w: 8.5, h: 0.35, margin: 0,
  fontSize: 14, color: PRIMARY, fontFace: "微软雅黑",
});
s.addText("118 张 JEOL SEM 图像 · 自动标定 · Web 化分析", {
  x: 8.9, y: 0.4, w: 3.93, h: 0.8, margin: 0, align: "right", valign: "middle",
  fontSize: 12, color: MUTED, fontFace: "微软雅黑",
});

// ── 三大功能卡片 ──
const cards = [
  {
    img: IMG("1-1_annotated.png"),
    tag: "01",
    title: "粉末颗粒统计",
    lines: [
      ["颗粒数 / D10 / D50 / D90", "一键输出"],
      ["0.5 s/张", "批量分析速度"],
      ["梯度分水岭分割", "适配紧密堆积粉体"],
    ],
    foot: "样例：10CL0050 · 1000×",
  },
  {
    img: IMG("59-1_layers.png"),
    tag: "02",
    title: "涂层 / 膜厚",
    lines: [
      ["亚像素边界定位", "逐列多点测量"],
      ["199.53 ± 0.45 μm", "主涂层厚度 (CV 0.2%)"],
      ["自动识别层结构", "倾斜校正 + 外点剔除"],
    ],
    foot: "样例：Chery 59-1 · 350×",
  },
  {
    img: IMG("59-10_pores.png"),
    tag: "03",
    title: "孔隙参数",
    lines: [
      ["孔隙率 = 黑色区域占比", "阈值可调"],
      ["4.08 %", "孔隙率（阈值100）"],
      ["孔径分布 D10/D50/D90", "2D 面分析法"],
    ],
    foot: "样例：Chery 59-10 · 2000×",
  },
];

const cw = 3.97, ch = 4.1, gap = 0.21, y0 = 1.5;
cards.forEach((c, i) => {
  const x = M + i * (cw + gap);
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y: y0, w: cw, h: ch, fill: { color: CARD }, rectRadius: 0.08,
    line: { color: "24374D", width: 0.75 },
  });
  // 图（等比裁切填充）
  s.addImage({ path: c.img, x: x + 0.12, y: y0 + 0.12, w: cw - 0.24, h: 1.72, sizing: { type: "cover", w: cw - 0.24, h: 1.72 } });
  // 序号 + 标题
  s.addText(c.tag, {
    x: x + 0.16, y: y0 + 1.92, w: 0.75, h: 0.55, margin: 0,
    fontSize: 26, bold: true, color: PRIMARY, fontFace: "Consolas",
  });
  s.addText(c.title, {
    x: x + 0.78, y: y0 + 1.98, w: cw - 0.9, h: 0.45, margin: 0,
    fontSize: 17, bold: true, color: TEXT, fontFace: "微软雅黑", valign: "middle",
  });
  // 指标行
  const items = c.lines.flatMap(([lead, tail], k) => ([
    { text: lead, options: { fontSize: 11.5, bold: true, color: ACCENT, breakLine: true, paraSpaceAfter: k === c.lines.length - 1 ? 0 : 5 } },
    { text: tail, options: { fontSize: 10.5, color: MUTED, breakLine: true, paraSpaceAfter: 8 } },
  ]));
  s.addText(items, {
    x: x + 0.18, y: y0 + 2.5, w: cw - 0.36, h: 1.3, margin: 0, fontFace: "微软雅黑", valign: "top",
  });
  s.addText(c.foot, {
    x: x + 0.18, y: y0 + ch - 0.34, w: cw - 0.36, h: 0.25, margin: 0,
    fontSize: 9.5, color: MUTED, fontFace: "微软雅黑",
  });
});

// ── 底部：本周要点 / 下一步 ──
const yb = 5.82, hb = 1.28;
s.addText("本周要点", {
  x: M, y: yb, w: 1.6, h: 0.3, margin: 0, fontSize: 12, bold: true, color: PRIMARY, fontFace: "微软雅黑",
});
const bu = () => ({ code: "25B8", indent: 8, color: PRIMARY });
s.addText([
  { text: "像素标定全自动：直接读 JEOL 元数据标尺（μm/px），无需人工量尺", options: { bullet: bu(), breakLine: true } },
  { text: "层厚精度优化：全局初值 + 逐列亚像素定位，CV 低至 0.2%", options: { bullet: bu(), breakLine: true } },
  { text: "修复中文路径 / 缺元数据等问题，支持手工标定", options: { bullet: bu() } },
], {
  x: M, y: yb + 0.32, w: 7.2, h: 0.95, margin: 0, fontSize: 11, color: TEXT,
  fontFace: "微软雅黑", paraSpaceAfter: 5, valign: "top",
});

s.addText("下一步", {
  x: 8.1, y: yb, w: 1.6, h: 0.3, margin: 0, fontSize: 12, bold: true, color: ACCENT, fontFace: "微软雅黑",
});
s.addText([
  { text: "引入 Cellpose / SAM 深度学习分割，解决弱衬度晶界", options: { bullet: bu(), breakLine: true } },
  { text: "EDS 数据接入：元素面分布 + 包覆层厚度", options: { bullet: bu(), breakLine: true } },
  { text: "Excel / PDF 自动报告，缺陷检测（裂纹·掉料）模块", options: { bullet: bu() } },
], {
  x: 8.1, y: yb + 0.32, w: 4.73, h: 0.95, margin: 0, fontSize: 11, color: TEXT,
  fontFace: "微软雅黑", paraSpaceAfter: 5, valign: "top",
});

// 分隔线
s.addShape(pres.shapes.LINE, { x: 7.85, y: yb + 0.05, w: 0, h: 1.1, line: { color: "24374D", width: 0.75 } });
s.addShape(pres.shapes.LINE, { x: M, y: yb - 0.14, w: W - 2 * M, h: 0, line: { color: "24374D", width: 0.75 } });

pres.writeFile({ fileName: "D:/vue_project/jinxiangshibie/SEM周进展汇报.pptx" }).then(() => console.log("done"));

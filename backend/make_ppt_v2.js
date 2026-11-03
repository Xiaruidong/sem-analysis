const pptxgen = require("pptxgenjs");
const path = require("path");

const IMG = p => path.resolve("D:/vue_project/jinxiangshibie/storage/results/sem/annotated", p);

// 浅色正式风格
const BG = "FFFFFF";
const PRIMARY = "0F4C5C";   // 深青
const ACCENT = "C2703A";    // 陶土橙
const TEXT = "1F2937";
const MUTED = "6B7280";
const HAIR = "E3E8EC";
const TINT = "EEF5F6";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "SEM分析";
pres.title = "SEM图像自动定量分析系统";

const W = 13.33, H = 7.5, M = 0.5;
const s = pres.addSlide();
s.background = { color: BG };

// ── 标题 ──
s.addText("SEM 图像自动定量分析系统", {
  x: M, y: 0.42, w: 7.6, h: 0.6, margin: 0,
  fontSize: 29, bold: true, color: PRIMARY, fontFace: "微软雅黑",
});
s.addText("电池材料微观表征 · 工作进展", {
  x: M, y: 1.0, w: 7.6, h: 0.32, margin: 0,
  fontSize: 13, color: MUTED, fontFace: "微软雅黑",
});
// 右上角关键事实
s.addText([
  { text: "118 ", options: { fontSize: 22, bold: true, color: ACCENT } },
  { text: "张 SEM 图像已跑通   ", options: { fontSize: 11, color: MUTED } },
  { text: "3 ", options: { fontSize: 22, bold: true, color: ACCENT } },
  { text: "类分析模块", options: { fontSize: 11, color: MUTED } },
], { x: 8.2, y: 0.5, w: 4.6, h: 0.9, margin: 0, align: "right", valign: "middle", fontFace: "微软雅黑" });

// ── 三条横向功能行 ──
const rows = [
  {
    img: IMG("1-1_annotated.png"), tag: "01", title: "粉末颗粒统计",
    desc: "自动分割 → 逐颗粒测量 → 粒度分布；适配紧密堆积粉体",
    m1: ["0.5 s / 张", "批量分析速度"], m2: ["D10 / D50 / D90", "颗粒数 + 粒度分布"],
  },
  {
    img: IMG("59-1_layers.png"), tag: "02", title: "涂层 / 膜厚",
    desc: "逐列亚像素边界定位，自动识别层结构并校正界面倾斜",
    m1: ["± 0.45 μm", "主涂层厚度标准差"], m2: ["199.53 μm", "主涂层厚度 (CV 0.2%)"],
  },
  {
    img: IMG("59-10_pores.png"), tag: "03", title: "孔隙参数",
    desc: "按黑色区域占比计算孔隙率，阈值可调，逐孔统计孔径",
    m1: ["4.08 %", "孔隙率（阈值 100）"], m2: ["0.30 μm", "孔径 D50"],
  },
];

const rowH = 1.26, rowGap = 0.12, yStart = 1.55;
rows.forEach((r, i) => {
  const y = yStart + i * (rowH + rowGap);
  // 缩略图
  s.addImage({ path: r.img, x: M, y, w: 1.82, h: rowH - 0.06, sizing: { type: "cover", w: 1.82, h: rowH - 0.06 } });
  // 编号
  s.addText(r.tag, {
    x: M + 1.95, y: y + 0.16, w: 0.55, h: 0.4, margin: 0,
    fontSize: 19, bold: true, color: PRIMARY, fontFace: "Consolas",
  });
  // 标题 + 说明
  s.addText(r.title, {
    x: M + 2.5, y: y + 0.1, w: 3.6, h: 0.36, margin: 0,
    fontSize: 16, bold: true, color: TEXT, fontFace: "微软雅黑",
  });
  s.addText(r.desc, {
    x: M + 2.5, y: y + 0.5, w: 4.2, h: 0.62, margin: 0,
    fontSize: 10, color: MUTED, fontFace: "微软雅黑", valign: "top",
  });
  // 两个指标
  [[7.4, 2.3], [9.85, 2.95]].forEach(([mx, mw], k) => {
    const m = k === 0 ? r.m1 : r.m2;
    s.addText(m[0], {
      x: mx, y: y + 0.26, w: mw, h: 0.42, margin: 0,
      fontSize: 15, bold: true, color: k === 0 ? ACCENT : PRIMARY, fontFace: "微软雅黑",
    });
    s.addText(m[1], {
      x: mx, y: y + 0.7, w: mw, h: 0.3, margin: 0,
      fontSize: 9.5, color: MUTED, fontFace: "微软雅黑",
    });
  });
  // 行分隔线
  if (i < rows.length - 1) {
    s.addShape(pres.shapes.LINE, {
      x: M, y: y + rowH + rowGap / 2, w: W - 2 * M, h: 0,
      line: { color: HAIR, width: 0.75 },
    });
  }
});

// ── 底部浅色带：本周要点 / 下一步 ──
const bandY = 5.85;
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: bandY, w: W, h: H - bandY, fill: { color: TINT }, line: { color: TINT } });

const bu = () => ({ code: "2022", indent: 8, color: PRIMARY });
const buA = () => ({ code: "2022", indent: 8, color: ACCENT });

s.addText("本周要点", {
  x: M, y: bandY + 0.18, w: 2, h: 0.26, margin: 0,
  fontSize: 11.5, bold: true, color: PRIMARY, fontFace: "微软雅黑",
});
s.addText([
  { text: "像素标定全自动：直接读 JEOL 元数据标尺，无需人工量尺", options: { bullet: bu(), breakLine: true } },
  { text: "层厚精度优化：全局初值 + 逐列亚像素定位，CV 低至 0.2%", options: { bullet: bu(), breakLine: true } },
  { text: "修复中文路径 / 缺元数据读图问题，支持手工标定", options: { bullet: bu() } },
], {
  x: M, y: bandY + 0.46, w: 7.0, h: 0.9, margin: 0,
  fontSize: 10, color: TEXT, fontFace: "微软雅黑", paraSpaceAfter: 4, valign: "top",
});

s.addText("下一步", {
  x: 7.95, y: bandY + 0.18, w: 2, h: 0.26, margin: 0,
  fontSize: 11.5, bold: true, color: ACCENT, fontFace: "微软雅黑",
});
s.addText([
  { text: "引入 Cellpose / SAM 深度学习分割，解决弱衬度晶界", options: { bullet: buA(), breakLine: true } },
  { text: "接入 EDS 数据：元素面分布与包覆层厚度", options: { bullet: buA(), breakLine: true } },
  { text: "缺陷检测（裂纹 · 掉料）与 Excel / PDF 自动报告", options: { bullet: buA() } },
], {
  x: 7.95, y: bandY + 0.46, w: 4.88, h: 0.9, margin: 0,
  fontSize: 10, color: TEXT, fontFace: "微软雅黑", paraSpaceAfter: 4, valign: "top",
});

pres.writeFile({ fileName: "D:/vue_project/jinxiangshibie/SEM周进展汇报_浅色版.pptx" }).then(() => console.log("done"));

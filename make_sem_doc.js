const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, Header, Footer,
  AlignmentType, HeadingLevel, PageNumber, BorderStyle, WidthType, TableLayoutType,
  ShadingType, PageBreak, SectionType, NumberFormat, TableOfContents,
} = require("C:\\Users\\13223\\AppData\\Roaming\\npm\\node_modules\\docx");
const fs = require("fs");

/* ===== 调色板 DM-1(Deep Cyan · 科技) ===== */
const P = {
  bg: "162235", accent: "37DCF2",
  titleColor: "FFFFFF", subtitleColor: "B0B8C0", metaColor: "90989F", footerColor: "687078",
  body: "1E293B", primary: "0F2A43", muted: "64748B",
  tbl: { headerBg: "1B6B7A", headerText: "FFFFFF", accentLine: "1B6B7A", innerLine: "BECFCC", surface: "EAF4F5" },
};

const allNoBorders = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.NONE }, insideVertical: { style: BorderStyle.NONE } };
const noBorders = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

/* ===== 封面辅助(R1 配方) ===== */
function splitTitleLines(title, charsPerLine) {
  if (title.length <= charsPerLine) return [title];
  const breakAfter = new Set([..."，。、；：！？", ..."的与和及之在于为", ..."-_—–·/", ..." \t"]);
  const lines = []; let remaining = title;
  while (remaining.length > charsPerLine) {
    let breakAt = -1;
    for (let i = charsPerLine; i >= Math.floor(charsPerLine * 0.6); i--)
      if (i < remaining.length && breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
    if (breakAt === -1) {
      const limit = Math.min(remaining.length, Math.ceil(charsPerLine * 1.3));
      for (let i = charsPerLine + 1; i < limit; i++) if (breakAfter.has(remaining[i - 1])) { breakAt = i; break; }
    }
    if (breakAt === -1) {
      breakAt = charsPerLine;
      const prev = remaining[breakAt - 1], next = remaining[breakAt];
      if (prev && next && !breakAfter.has(prev) && !breakAfter.has(next) && /[\u4e00-\u9fff]/.test(prev) && /[\u4e00-\u9fff]/.test(next)) breakAt -= 1;
    }
    lines.push(remaining.slice(0, breakAt).trim());
    remaining = remaining.slice(breakAt).trim();
  }
  if (remaining) lines.push(remaining);
  if (lines.length > 1 && lines[lines.length - 1].length <= 2) { const last = lines.pop(); lines[lines.length - 1] += last; }
  return lines;
}
function calcTitleLayout(title, maxWidthTwips, preferredPt = 40, minPt = 24) {
  const charsPerLine = (pt) => Math.floor(maxWidthTwips / (pt * 20));
  let titlePt = preferredPt, lines;
  while (titlePt >= minPt) {
    const cpl = charsPerLine(titlePt);
    if (cpl < 2) { titlePt -= 2; continue; }
    lines = splitTitleLines(title, cpl);
    if (lines.length <= 3) break;
    titlePt -= 2;
  }
  if (!lines || lines.length > 3) { lines = splitTitleLines(title, charsPerLine(minPt)); titlePt = minPt; }
  return { titlePt, titleLines: lines };
}
function calcCoverSpacing({ titleLineCount = 1, titlePt = 36, hasSubtitle = false, hasEnglishLabel = false, metaLineCount = 0, fixedHeight = 800 }) {
  const SAFETY = 1200;
  const usable = 16838 - SAFETY;
  const contentH = titleLineCount * (titlePt * 23 + 200) + (hasSubtitle ? 12 * 23 + 600 : 0) + (hasEnglishLabel ? 9 * 23 + 600 : 0) + metaLineCount * (10 * 23 + 100) + fixedHeight + 3 * 300;
  const remaining = Math.max(usable - contentH, 400);
  const topSpacing = Math.min(Math.round(remaining * 0.42), 4800), bottomSpacing = Math.min(Math.round(remaining * 0.58), 4800);
  return { topSpacing: Math.max(topSpacing, 600), bottomSpacing: Math.max(bottomSpacing, 600) };
}
function buildCoverR1(config) {
  const padL = 1200, padR = 800;
  const { titlePt, titleLines } = calcTitleLayout(config.title, 11906 - padL - padR - 300, 40, 24);
  const spacing = calcCoverSpacing({ titleLineCount: titleLines.length, titlePt, hasSubtitle: !!config.subtitle, hasEnglishLabel: !!config.englishLabel, metaLineCount: (config.metaLines || []).length, fixedHeight: 400 });
  const accentLeft = { style: BorderStyle.SINGLE, size: 8, color: P.accent, space: 12 };
  const children = [];
  children.push(new Paragraph({ spacing: { before: spacing.topSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR }, spacing: { after: 500 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: P.accent, space: 8 } },
    children: [new TextRun({ text: config.englishLabel.split("").join("  "), size: 18, color: P.accent, font: { ascii: "Calibri", eastAsia: "SimHei" }, characterSpacing: 40 })],
  }));
  titleLines.forEach((line, i) => children.push(new Paragraph({
    indent: { left: padL },
    spacing: { after: i < titleLines.length - 1 ? 100 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: line, size: titlePt * 2, bold: true, color: P.titleColor, font: { eastAsia: "SimHei", ascii: "Arial" } })],
  })));
  children.push(new Paragraph({
    indent: { left: padL }, spacing: { after: 800 },
    children: [new TextRun({ text: config.subtitle, size: 24, color: P.subtitleColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
  }));
  for (const line of config.metaLines) children.push(new Paragraph({
    indent: { left: padL + 200 }, spacing: { after: 80 }, border: { left: accentLeft },
    children: [new TextRun({ text: line, size: 24, color: P.metaColor, font: { eastAsia: "Microsoft YaHei", ascii: "Arial" } })],
  }));
  children.push(new Paragraph({ spacing: { before: spacing.bottomSpacing } }));
  children.push(new Paragraph({
    indent: { left: padL, right: padR },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: P.accent, space: 8 } },
    spacing: { before: 200 },
    children: [
      new TextRun({ text: config.footerLeft || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
      new TextRun({ text: "                                        " }),
      new TextRun({ text: config.footerRight || "", size: 16, color: P.footerColor, font: { ascii: "Arial" } }),
    ],
  }));
  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED, borders: allNoBorders,
    rows: [new TableRow({ height: { value: 16838, rule: "exact" }, children: [new TableCell({ shading: { type: ShadingType.CLEAR, fill: P.bg }, borders: noBorders, children })] })],
  })];
}

/* ===== 正文组件 ===== */
const F = { ascii: "Calibri", eastAsia: "Microsoft YaHei" };
function h1(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 160 },
    children: [new TextRun({ text, bold: true, size: 32, color: P.primary, font: F })] });
}
function h2(text) {
  return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 }, keepNext: true,
    children: [new TextRun({ text, bold: true, size: 28, color: P.primary, font: F })] });
}
function body(text, opts = {}) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 420 }, spacing: { line: 312, after: 60 },
    children: [new TextRun({ text, size: 24, color: P.body, font: F, ...opts })] });
}
function bullet(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 312, after: 40 },
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 24, color: P.body, font: F })] });
}
function caption(text) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 160 },
    children: [new TextRun({ text, size: 20, color: P.muted, font: F })] });
}
function makeTable(header, rows, widths) {
  const cell = (t, isHead, i) => new TableCell({
    shading: { type: ShadingType.CLEAR, fill: isHead ? P.tbl.headerBg : (i % 2 === 1 ? P.tbl.surface : "FFFFFF") },
    margins: { top: 80, bottom: 80, left: 140, right: 140 },
    children: [new Paragraph({ alignment: isHead ? AlignmentType.CENTER : AlignmentType.LEFT, spacing: { line: 300 },
      children: [new TextRun({ text: t, size: 22, bold: isHead, color: isHead ? P.tbl.headerText : P.body, font: F })] })],
  });
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE }, layout: TableLayoutType.FIXED,
    borders: { top: { style: BorderStyle.SINGLE, size: 8, color: P.tbl.accentLine }, bottom: { style: BorderStyle.SINGLE, size: 8, color: P.tbl.accentLine }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE }, insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: P.tbl.innerLine }, insideVertical: { style: BorderStyle.SINGLE, size: 2, color: P.tbl.innerLine } },
    columnWidths: widths,
    rows: [
      new TableRow({ tableHeader: true, cantSplit: true, children: header.map((t) => cell(t, true, 0)) }),
      ...rows.map((r, i) => new TableRow({ cantSplit: true, children: r.map((t) => cell(t, false, i)) })),
    ],
  });
}

/* ===== 正文内容 ===== */
const bodyChildren = [];

bodyChildren.push(h1("一、项目概述"));
bodyChildren.push(body("SEM 图像自动定量分析系统是面向电池材料微观表征的一站式图像分析工具。系统以 JEOL 扫描电子显微镜(SEM)输出的 BMP 图像及其同名元数据文件为输入,自动完成像素标定、目标分割与定量测量,覆盖粉末颗粒统计、涂层/膜厚测量、孔隙参数分析三大高频分析场景,并通过 Web 界面实现批量处理与结果可视化。系统已在 118 张真实 SEM 图像(正极/负极粉末、涂层截面、EDS 系列)上完成验证。"));
bodyChildren.push(h2("1.1 现状痛点"));
bodyChildren.push(bullet("颗粒、涂层、孔隙全靠人工在图像软件上逐个测量,单张图耗时数分钟,批量数据难以覆盖;"));
bodyChildren.push(bullet("人工选点主观性强,多人测量结果不可复现,缺乏统一口径;"));
bodyChildren.push(bullet("像素到微米的换算依赖手工量尺,易引入系统误差。"));
bodyChildren.push(h2("1.2 项目目标"));
bodyChildren.push(bullet("读取图像元数据自动完成像素标定,零人工量尺;"));
bodyChildren.push(bullet("颗粒统计、涂层厚度、孔隙参数三类分析全覆盖;"));
bodyChildren.push(bullet("批量分析达到 0.5 秒/张,结果自动标注并可视化;"));
bodyChildren.push(bullet("统一算法口径,测量结果可复现、可追溯。"));

bodyChildren.push(h1("二、技术路径"));
bodyChildren.push(body("系统技术路径为一条从原始图像到可交付数据的全自动流水线,共六个环节:图像接入、像素标定、预处理、目标分割、定量测量、统计输出。"));
bodyChildren.push(makeTable(
  ["环节", "技术方案", "说明"],
  [
    ["1. 图像接入", "BMP + 同名 .txt 元数据", "JEOL SEM 原始输出,批量读取"],
    ["2. 像素标定", "元数据解析", "读取标尺像素长度与物理长度,自动换算 μm/px"],
    ["3. 预处理", "OpenCV", "裁剪信息栏、去噪、衬度归一化"],
    ["4. 目标分割", "Otsu / 梯度分水岭", "灰度梯度标记 + 分水岭拆分粘连颗粒"],
    ["5. 定量测量", "逐颗粒/逐列测量", "亚像素边界定位,多点统计"],
    ["6. 统计输出", "统计与可视化", "D10/D50/D90、标注图、Web 呈现"],
  ],
  [1800, 2800, 7000]
));
bodyChildren.push(caption("表 1  技术路径流水线"));
bodyChildren.push(h2("2.1 三项关键技术"));
bodyChildren.push(body("元数据驱动标定:直接解析 JEOL 元数据中的 $$SM_MICRON_BAR(标尺像素长度)、$$SM_MICRON_MARKER(标尺物理长度)字段完成标定;标尺缺失时按放大倍数($CM_MAG)兜底,并支持手工标定校正。系统同时修复了中文路径、缺元数据等异常场景。"));
bodyChildren.push(body("梯度分水岭分割:针对紧密堆积粉体中颗粒互相粘连的问题,采用灰度梯度提取标记、分水岭算法拆分粘连区域,显著优于传统单一阈值法;颗粒亮暗极性可配置,最小粒径可按物理尺度(μm)过滤碎屑。"));
bodyChildren.push(body("亚像素边界定位:涂层厚度测量采用全局行平均剖面定位界面大致位置作为初值,再在初值附近窗口内逐列寻找灰度梯度极值点,并通过抛物线插值达到亚像素精度;逐列位置以中位数 ± k×MAD 剔除外点,线性拟合吸收界面倾斜,最终以多点统计输出均值 ± 标准差与变异系数 CV。"));

bodyChildren.push(h1("三、核心功能模块"));
bodyChildren.push(h2("3.1 粉末颗粒统计"));
bodyChildren.push(body("面向粉体样品的颗粒形貌与粒度分析。分割后逐颗粒测量等效直径、长径比、圆度等形貌参数(参照 ISO 9276-1 图像分析法),输出颗粒数与粒度分布 D10/D50/D90,并生成带编号标注的分析图。实测批量分析速度约 0.5 秒/张。"));
bodyChildren.push(h2("3.2 涂层/膜厚测量"));
bodyChildren.push(body("面向截面 SEM 图的涂层与膜厚定量。自动识别多层结构,逐列多点测量并以亚像素定位保证精度;样例 Chery 59-1(350×)主涂层测量结果为 199.53 ± 0.45 μm,变异系数低至 0.2%。"));
bodyChildren.push(h2("3.3 孔隙参数分析"));
bodyChildren.push(body("采用 2D 面分析法,孔隙率定义为黑色(孔隙)像素面积与视场有效面积之比。二值化支持固定阈值、全局 Otsu 与自适应三种方法以适应不同衬度图像,阈值可调;同时输出孔径分布 D10/D50/D90。样例孔隙率 4.08%(阈值 100)。"));

bodyChildren.push(h1("四、系统架构"));
bodyChildren.push(body("系统采用轻量三层架构,单一 Python 服务同时提供 REST API 与 Web 界面,无需数据库与 GPU,支持 Windows / Linux / Docker 跨平台部署,一条命令(python run_sem.py)即可启动。"));
bodyChildren.push(makeTable(
  ["层级", "组成", "职责"],
  [
    ["Web 前端层", "单页应用(原生 HTML/JS)", "图像浏览、参数配置、标注图与统计图表展示,由后端直接托管"],
    ["服务层(FastAPI)", "REST API(端口 8001)", "/api/sem/analyze 颗粒分析、/api/sem/thickness 膜厚、/api/sem/porosity 孔隙、/api/sem/calibrate 标定;结果目录挂载静态服务"],
    ["算法层(app/sem)", "四个算法模块", "calibration 元数据标定、particles 颗粒分割与测量、thickness 亚像素膜厚、porosity 孔隙分析;基于 OpenCV + NumPy 实现"],
  ],
  [2200, 3000, 6400]
));
bodyChildren.push(caption("表 2  系统三层架构"));
bodyChildren.push(body("数据流:BMP/TXT 读入后于内存中完成分析,标注图与 JSON 结果落盘 storage/results 目录,前端经 /results 静态路径直接访问,全过程无状态、可重复。"));

bodyChildren.push(h1("五、验证数据与阶段性成果"));
bodyChildren.push(makeTable(
  ["验证项", "结果", "特性"],
  [
    ["像素标定", "JEOL 标尺元数据直读,无标尺图像按放大倍数兜底;修复中文路径/缺元数据场景,支持手工标定", "全自动"],
    ["涂层厚度", "全局初值 + 逐列亚像素定位;样例主涂层 199.53 ± 0.45 μm,CV 0.2%", "高精度"],
    ["颗粒统计", "等效直径/长径比/圆度/粒度分布 D10-D90;梯度分水岭解决粘连拆分", "批量 0.5 s/张"],
    ["孔隙分析", "2D 面分析孔隙率 + 孔径分布,阈值可调;样例 4.08%(阈值 100)", "多方法可选"],
  ],
  [1600, 7600, 2400]
));
bodyChildren.push(caption("表 3  118 张真实 SEM 图像验证结果汇总"));

bodyChildren.push(h1("六、下一步规划"));
bodyChildren.push(bullet("深度学习分割:引入 Cellpose / SAM 解决弱衬度晶界识别问题,提升复杂显微组织的分割鲁棒性;"));
bodyChildren.push(bullet("EDS 数据接入:解析元素面分布图,实现包覆层成分分析与包覆厚度定量;"));
bodyChildren.push(bullet("报告自动化:Excel / PDF 一键生成,包含标注图、统计图表与批次汇总;"));
bodyChildren.push(bullet("缺陷检测模块:裂纹、掉料等典型缺陷的自动检出与计数,服务产线质量监控。"));

/* ===== 文档组装 ===== */
const pageMargin = { top: 1440, bottom: 1440, left: 1701, right: 1417 };
const footerArabic = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: P.muted, font: F })] })] });
const footerRoman = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: P.muted, font: F })] })] });
const headerBody = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: P.tbl.innerLine, space: 4 } }, children: [new TextRun({ text: "SEM 图像自动定量分析系统 · 项目介绍", size: 18, color: P.muted, font: F })] })] });

const doc = new Document({
  creator: "Xiaruidong",
  title: "SEM 图像自动定量分析系统 项目介绍",
  styles: { default: { document: { run: { font: F, size: 24, color: P.body }, paragraph: { spacing: { line: 312 } } } } },
  numbering: { config: [{ reference: "bullets", levels: [{ level: 0, format: "bullet", text: "▪", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [
    // 封面
    { properties: { page: { margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
      children: buildCoverR1({
        title: "SEM 图像自动定量分析系统项目介绍",
        subtitle: "电池材料微观表征 · 从人工读图到一键定量",
        englishLabel: "SEM QUANTITATIVE ANALYSIS",
        metaLines: ["汇报人:Xiaruidong", "编制日期:2026 年 11 月", "文档版本:V1.0"],
        footerLeft: "SEM Quantitative Analysis System", footerRight: "2026.11",
      }) },
    // 目录(罗马页码)
    { properties: { type: SectionType.NEXT_PAGE, page: { margin: pageMargin, pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } },
      footers: { default: footerRoman },
      children: [
        new Paragraph({ spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "目  录", bold: true, size: 32, color: P.primary, font: F })] }),
        new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 200 },
          children: [new TextRun({ text: "(提示:在 Word 中右键目录,选择\u201c更新域\u201d可刷新页码)", italics: true, size: 18, color: P.muted, font: F })] }),
      ] },
    // 正文(阿拉伯页码)
    { properties: { type: SectionType.NEXT_PAGE, page: { margin: pageMargin, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      headers: { default: headerBody }, footers: { default: footerArabic },
      children: bodyChildren },
  ],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("D:\\vue_project\\jinxiangshibie\\SEM项目介绍.docx", buf); console.log("done"); });

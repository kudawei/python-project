"""
考研择校报告 PDF 生成 API
使用 ReportLab 库将推荐结果导出为精美的 PDF 格式报告。
报告内容包括：用户画像、推荐结果、院校得分明细、分梯度汇总。
"""

import io
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.recommendation import calculate_recommendation

router = APIRouter(prefix="/report", tags=["择校报告"])


def _register_chinese_font():
    """
    注册中文字体，优先使用系统自带的思源黑体或文泉驿微米黑。
    如果都找不到则回退到 Helvetica（中文可能显示异常）。
    """
    font_paths = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/wqy-microhei/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_paths:
        try:
            pdfmetrics.registerFont(TTFont("Chinese", fp))
            return "Chinese"
        except Exception:
            continue
    return "Helvetica"


@router.post("/generate", summary="一键生成考研择校报告 PDF")
def generate_report(
    zydm: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    根据用户画像和指定专业代码，执行推荐算法后生成 PDF 报告。

    报告包含：
    1. 封面：标题 + 用户信息 + 生成时间
    2. 用户画像摘要
    3. 推荐结果分梯度展示（冲刺/稳妥/保底）
    4. 每所院校的详细属性和得分
    """
    font_name = _register_chinese_font()

    # 执行推荐算法获取结果（不保存日志，避免重复记录）
    result = calculate_recommendation(db=db, user=current_user, zydm=zydm, save_log=False)

    # 构建画像信息
    province_str = current_user.target_provinces or "未设置"
    degree_map = {"xs": "学术学位", "zy": "专业学位"}
    study_map = {"1": "全日制", "2": "非全日制"}
    rating_map = {"weak": "一般", "medium": "中等", "strong": "较强"}
    degree_label = degree_map.get(current_user.degree_type or "", current_user.degree_type or "未设置")
    study_label = study_map.get(current_user.study_mode or "", current_user.study_mode or "未设置")
    rating_label = rating_map.get(current_user.self_rating or "", current_user.self_rating or "未设置")

    # 创建 PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleCN", parent=styles["Title"], fontName=font_name, fontSize=22, spaceAfter=10)
    h2_style = ParagraphStyle("H2CN", parent=styles["Heading2"], fontName=font_name, fontSize=14, spaceAfter=6, textColor=colors.HexColor("#409eff"))
    body_style = ParagraphStyle("BodyCN", parent=styles["Normal"], fontName=font_name, fontSize=10, leading=16)
    small_style = ParagraphStyle("SmallCN", parent=styles["Normal"], fontName=font_name, fontSize=9, leading=14, textColor=colors.grey)

    elements = []

    # ========== 封面 ==========
    elements.append(Spacer(1, 60 * mm))
    elements.append(Paragraph("考研择校智能推荐报告", title_style))
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph(f"用户：{current_user.nickname or current_user.username}", body_style))
    elements.append(Paragraph(f"目标专业代码：{zydm}", body_style))
    elements.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("本报告基于用户画像和院校数据，通过多维打分算法自动生成。", small_style))
    elements.append(PageBreak())

    # ========== 用户画像摘要 ==========
    elements.append(Paragraph("一、用户画像", h2_style))
    profile_data = [
        ["项目", "内容"],
        ["意向门类", current_user.target_mlmc or "未设置"],
        ["意向省市", province_str],
        ["学位期望", degree_label],
        ["学习方式", study_label],
        ["实力自评", rating_label],
    ]
    profile_table = Table(profile_data, colWidths=[80 * mm, 80 * mm])
    profile_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), font_name),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#409eff")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(profile_table)
    elements.append(Spacer(1, 8 * mm))

    # ========== 推荐结果 ==========
    tier_config = [
        ("二、冲刺院校", "sprint", "难度系数较高，需要付出更多努力的顶级院校", colors.HexColor("#f56c6c")),
        ("三、稳妥院校", "stable", "难度适中，与您的期望高度匹配的院校", colors.HexColor("#67c23a")),
        ("四、保底院校", "safe", "难度较低，专业匹配且录取把握较大的院校", colors.HexColor("#909399")),
    ]

    for title, key, desc, color in tier_config:
        items = result.get(key, [])
        elements.append(Paragraph(title, h2_style))
        elements.append(Paragraph(f"{desc}（共 {len(items)} 所）", small_style))
        elements.append(Spacer(1, 3 * mm))

        if items:
            header = ["院校名称", "院校代码", "省市", "双一流", "自划线", "博士点", "得分"]
            rows = [header]
            for item in items:
                def _yes(v):
                    return "是" if v in ("是", "1") else "否"
                rows.append([
                    item.get("dwmc", ""),
                    item.get("dwdm", ""),
                    item.get("szss", ""),
                    _yes(item.get("syl", "")),
                    _yes(item.get("zhx", "")),
                    _yes(item.get("bs", "")),
                    str(item.get("score", "")),
                ])

            t = Table(rows, colWidths=[42 * mm, 22 * mm, 18 * mm, 16 * mm, 16 * mm, 16 * mm, 16 * mm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("暂无推荐结果", body_style))

        elements.append(Spacer(1, 8 * mm))

    # ========== 得分说明 ==========
    elements.append(Paragraph("五、得分计算说明", h2_style))
    elements.append(Paragraph("难度系数：自划线 +5分，双一流 +3分，博士点 +1分", body_style))
    elements.append(Paragraph("匹配度：省市匹配 +10分，学习方式匹配 +5分", body_style))
    elements.append(Paragraph("综合得分 = 难度系数 + 匹配度加分", body_style))
    elements.append(Spacer(1, 5 * mm))
    elements.append(Paragraph(
        f"* 本报告由系统自动生成，仅供参考。生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        small_style,
    ))

    doc.build(elements)
    buf.seek(0)

    filename = f"kaoyan_report_{current_user.username}_{zydm}_{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

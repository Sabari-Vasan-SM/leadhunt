import io
from typing import List
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from app.models.lead import Lead

class ExcelExporter:
    @staticmethod
    def _prepare_dataframe(leads: List[Lead]) -> pd.DataFrame:
        data = []
        for lead in leads:
            data.append({
                "Business Name": lead.business_name,
                "Category": lead.category or "",
                "Phone": lead.phone or "N/A",
                "Email": lead.email or "N/A",
                "Website": lead.website_url or "N/A",
                "Google Maps": lead.google_maps_url or "N/A",
                "Address": lead.address or "",
                "City": lead.city or "",
                "Pincode": lead.pincode or "",
                "Confidence Score": f"{int((lead.confidence_score or 0) * 100)}%",
                "Source": lead.source_name or "Public Web",
                "Source Link": lead.source_url or ""
            })
        return pd.DataFrame(data)

    @classmethod
    def export_to_excel(cls, leads: List[Lead], query_name: str = "Leads") -> bytes:
        df = cls._prepare_dataframe(leads)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_name = "Leads"
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]

            # Header styling
            header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

            thin_border = Border(
                left=Side(style="thin", color="E2E8F0"),
                right=Side(style="thin", color="E2E8F0"),
                top=Side(style="thin", color="E2E8F0"),
                bottom=Side(style="thin", color="E2E8F0")
            )

            # Style header cells
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_align
                cell.border = thin_border
            worksheet.row_dimensions[1].height = 28

            # Style body cells and auto-fit column widths
            for col_idx, col in enumerate(worksheet.columns, start=1):
                max_len = 0
                col_letter = get_column_letter(col_idx)
                for cell in col:
                    cell.border = thin_border
                    if cell.row != 1:
                        cell.alignment = Alignment(vertical="center")
                        # Hyperlinks for URLs
                        val = str(cell.value or "")
                        if val.startswith("http://") or val.startswith("https://"):
                            cell.font = Font(name="Calibri", size=10, color="2563EB", underline="single")
                    max_len = max(max_len, len(str(cell.value or "")))
                worksheet.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

        return output.getvalue()

    @classmethod
    def export_to_csv(cls, leads: List[Lead]) -> bytes:
        df = cls._prepare_dataframe(leads)
        # utf-8-sig adds BOM so Excel opens non-ASCII and commas properly
        return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

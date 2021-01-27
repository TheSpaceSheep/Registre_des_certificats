from openpyxl import Workbook
from openpyxl.styles import *
import os

# TODO: font size
# TODO: layout for printability

thin_border = Border(left=Side(style='thin'),
                     right=Side(style='thin'),
                     top=Side(style='thin'),
                     bottom=Side(style='thin'))

thick_border = Border(left=Side(style='thick'),
                      right=Side(style='thick'),
                      top=Side(style='thick'),
                      bottom=Side(style='thick'))

thick_border_left = Border(left=Side(style='thick'),
                           right=Side(style='thin'),
                           top=Side(style='thin'),
                           bottom=Side(style='thin'))

thick_border_right = Border(left=Side(style='thin'),
                           right=Side(style='thick'),
                           top=Side(style='thin'),
                           bottom=Side(style='thin'))

thick_border_bottom = Border(left=Side(style='thin'),
                      right=Side(style='thin'),
                      top=Side(style='thin'),
                      bottom=Side(style='thick'))

thick_border_left_bottom = Border(left=Side(style='thick'),
                           right=Side(style='thin'),
                           top=Side(style='thin'),
                           bottom=Side(style='thick'))

thick_border_right_bottom = Border(left=Side(style='thin'),
                           right=Side(style='thick'),
                           top=Side(style='thin'),
                           bottom=Side(style='thick'))

def cm_to_points(cm):
    """converts centimeters into the weird excel unit : the points
    1 point = 1/72 of an inch... yeah..."""
    return cm*0.393701*72


def generer_registre(registre, file="registre_des_certificats.xls"):
    wb = Workbook()

    # main page
    wb.active.title = "Registre"

    # names cannot be longer than 15 characters
    wb.active.column_dimensions['A'].width = 15

    wb.active.row_dimensions[2].height = cm_to_points(4)

    # first two rows
    j = 2
    cell = wb.active.cell(2, 1)
    cell.value = "Registre des certificats"
    cell.alignment = Alignment(wrap_text=True,
                                               horizontal="center",
                                               vertical="center")
    cell.border = thin_border
    cell.font = Font(name='arial', size=15, underline='single')

    for cat in registre.categories:
        cell = wb.active.cell(1, j)
        cell.value = cat
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thick_border
        first = True
        for c in registre.get_certificats(cat):
            cell = wb.active.cell(2, j)
            cell.value = c.nom
            cell.alignment = Alignment(horizontal="center",
                                       vertical="bottom",
                                       textRotation=90)
            cell.font = Font(name='arial', size=10)
            cell.border = thick_border_left if first else thin_border
            first = False
            wb.active.column_dimensions[chr(64+j)].width = 3
            j += 1
        cell.border = thick_border_right
        wb.active.merge_cells(start_row=1,
                              start_column=j-len(registre.get_certificats(cat)),
                              end_row=1,
                              end_column=j-1)
    i = 3
    # member rows
    for m in registre.membres:
        j = 2
        cell = wb.active.cell(i, 1)
        cell.value = m.id
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thick_border_right_bottom if i%4==2 else thick_border_right
        for cat in registre.categories:
            first = True
            for cert in registre.get_certificats(cat):
                cell = wb.active.cell(i, j)
                cell.value = registre.registre[m, cert]
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if first:
                    cell.border = thick_border_left_bottom if i%4==2 else thick_border_left
                else:
                    cell.border = thick_border_bottom if i%4==2 else thin_border
                first = False
                j += 1
            cell.border = thick_border_right_bottom if i%4==2 else thick_border_right
        i += 1

    # page for each category 
    for cat in registre.categories:
        wb.create_sheet(cat)
        wb.active = wb[cat]

        wb.active.column_dimensions['A'].width = 15
        wb.active.row_dimensions[2].height = cm_to_points(4)

        # first two rows
        cell = wb.active.cell(2, 1)
        cell.value = f"Certificats {cat}"
        cell.alignment = Alignment(wrap_text=True,
                                   horizontal="center",
                                   vertical="center")
        cell.font = Font(name='arial', size=15, underline='single')
        cell.border = thin_border

        cell = wb.active.cell(1, 2)
        cell.value = f"{cat}"
        cell.alignment = Alignment(horizontal="center",
                                   vertical="center")
        cell.border = thick_border

        wb.active.merge_cells(start_row=1,
                              start_column=2,
                              end_row=1,
                              end_column=len(registre.get_certificats(cat))+1)
        j = 2
        first = True
        for cert in registre.get_certificats(cat):
            cell = wb.active.cell(2, j)
            cell.value = cert.nom
            cell.alignment = Alignment(horizontal="center",
                                       vertical="bottom",
                                       textRotation=90)
            cell.font = Font(name='arial', size=10)
            cell.border = thick_border_left if first else thin_border
            first = False
            j += 1
        cell.border = thick_border_right

        i = 3
        # member rows
        for m in registre.membres:
            cell = wb.active.cell(i, 1)
            cell.value = m.id
            cell.alignment = Alignment(horizontal="center",
                                       vertical="center")
            cell.border = thick_border_right_bottom if i%4==2 else thick_border_right
            j = 2
            first = True
            for cert in registre.get_certificats(cat):
                cell = wb.active.cell(i, j)
                cell.value = registre.registre[m, cert]
                cell.alignment = Alignment(horizontal="center",
                                           vertical="center")
                if first:
                    cell.border = thick_border_left_bottom if i%4==2 else thick_border_left
                else:
                    cell.border = thick_border_bottom if i%4==2 else thin_border
                first = False
                wb.active.column_dimensions[chr(64+j)].width = 5
                j += 1
            cell.border = thick_border_right_bottom if i%4==2 else thick_border_right
            i += 1

    wb.save(file)
    os.system(f"libreoffice {file}")


def center_all_cells(wb):
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal="center", vertical="center")


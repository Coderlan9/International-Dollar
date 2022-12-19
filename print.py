import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import re
import qrcode
import subprocess
import time
from pyautogui import hotkey
from PyPDF2 import PdfFileMerger


def print_pdf():
    merger = PdfFileMerger()
    for pdf_file in sorted(os.listdir('print_folder')):
        merger.append(open('print_folder/' + pdf_file, 'rb'))
    with open('print_folder/result.pdf', 'wb') as fout:
        merger.write(fout)
    os.startfile(os.path.normpath('print_folder/result.pdf'))
    time.sleep(5)
    hotkey('ctrl', 'p')
    time.sleep(10)
    for f in os.listdir('print_folder'):
        os.remove('print_folder/' + f)


def full_bill(list_bills):
    global x_pos, y_pos, count, count5
    x_pos = 35
    y_pos = 20
    a4_png = Image.open('img/bills_to_print/a4.png')
    count = 0
    count5 = 0

    def bill_gen_front():
        x_pos2 = 35
        y_pos2 = 20
        c6 = 0
        for c, bill in enumerate(list_bills):
            img = Image.open('img/bills_to_print/' + bill.split('x')[0] + '.png')
            a4_png.paste(img, (x_pos2, y_pos2))
            if c == 5 or c6 == len(list_bills) - 1:
                w, h = a4_png.size
                crop_top = a4_png.crop((0, 0, w - 70, h - 20))
                resized = crop_top.resize((w, h), Image.Resampling.LANCZOS)
                if len(os.listdir('print_folder')) == 0:
                    len_list = 0
                else:
                    len_list = len(os.listdir('print_folder')) + 1
                resized.save('print_folder/' + str(len_list) + '.pdf')
                a4_png.paste(Image.new('L', (1190, 1680), color='white'))
                x_pos2 = 35
                y_pos2 = 20
                c -= c - 1
            elif c == 2:
                y_pos2 += 805
                x_pos2 -= 702
            else:
                x_pos2 += 351
            c6 += 1

    def bill_gen_back(bill):
        global x_pos, y_pos, count, count5
        sm = bill.splitlines()[0]
        img = Image.open('img/bills_to_print/' + sm.split('x')[0] + '_back.png')
        address_qr = qrcode.QRCode(version=1, box_size=6, border=2, error_correction=qrcode.constants.ERROR_CORRECT_L)
        address_qr.add_data(bill)
        qr_make = address_qr.make_image(fill_color='black', back_color='white')
        qr_resize = qr_make.resize((240, 240), Image.Resampling.LANCZOS)

        f = ImageFont.truetype('ind_font.ttf', 27)
        f2 = ImageFont.truetype('ind_font.ttf', 48)
        txt = Image.new('L', (770,310))
        d = ImageDraw.Draw(txt)

        def format_key(s):
            return re.sub("(.{20})", "\\1\n", s, 0, re.DOTALL)

        d.text((5, 120), "Private Key :\n" + format_key(bill.splitlines()[1]),  font=f, fill=255)
        d.text((510, 70), "Public Key :\n" + format_key(bill.splitlines()[2]),  font=f, fill=255)
        d.text((5, 252), sm, font=f2, fill=255)
        d.text((760 - len(sm) * 20, 2), sm, font=f2, fill=255)
        rot = txt.rotate(90,  expand=1)

        img.paste(ImageOps.colorize(rot, (255,255,255), (255,255,255)), (20,10),  rot)
        img.paste(qr_resize.rotate(90, expand=1), (55, 290))
        img.paste(qr_resize.rotate(90, expand=1), (55, 290))
        a4_png.paste(img, (x_pos, y_pos))
        if count == 5 or count5 == len(list_bills) - 1:
            w, h = a4_png.size
            crop_top = a4_png.crop((0, 0, w - 70, h - 20))
            resized = crop_top.resize((w, h), Image.Resampling.LANCZOS)
            resized.save('print_folder/' + str(len(os.listdir('print_folder'))) + '.pdf')
            a4_png.paste(Image.new('L', (1190, 1680), color='white'))
            x_pos = 35
            y_pos = 20
            count = -1
        elif count == 2:
            y_pos += 805
            x_pos -= 702
        else:
            x_pos += 351
        count += 1
        count5 += 1

    bill_gen_front()
    for i in list_bills:
        subprocess.run('python generate_address.py')
        with open('hashing.txt', 'r+') as new_addr:
            new_address = new_addr.read().splitlines(keepends=True)
            bill_gen_back(i + '\n' + ''.join(new_address[1:]))
            new_addr.seek(0)
            new_addr.truncate()
    print_pdf()

def only_qr(list_bills):
    global x_pos_qr, y_pos_qr, c4, c5
    x_pos_qr = 50
    y_pos_qr = 50
    a4_png = Image.open('img/bills_to_print/a4.png')
    c4 = 0
    c5 = 0
    def bill_gen_qr(bill):
        global y_pos_qr, x_pos_qr, c4, c5
        sm = bill.splitlines()[0]
        address_qr = qrcode.QRCode(version=1, box_size=6, border=2, error_correction=qrcode.constants.ERROR_CORRECT_L)
        address_qr.add_data(bill)
        qr_make = address_qr.make_image(fill_color='black', back_color='white')
        qr_resize = qr_make.resize((240, 240), Image.Resampling.LANCZOS)
        f = ImageFont.truetype('ind_font.ttf', 36)
        d = ImageDraw.Draw(a4_png)
        d.text((x_pos_qr + 120 - len(sm) * 7, y_pos_qr - 37), sm, font=f, fill=0)
        a4_png.paste(qr_resize, (x_pos_qr, y_pos_qr))
        if c4 == 23 or c5 == len(list_bills) - 1:
            a4_png.save('print_folder/' + str(len(os.listdir('print_folder'))) + '.pdf')
            a4_png.paste(Image.new('L', (1190, 1680), color='white'))
            x_pos_qr = 50
            y_pos_qr = 50
            c4 = -1
        elif c4 == 3 or c4 == 7 or c4 == 11 or c4 == 15 or c4 == 19:
            y_pos_qr += 275
            x_pos_qr -= 750
        else:
            x_pos_qr += 250
        c4 += 1
        c5 += 1

    for i in list_bills:
        subprocess.run('python generate_address.py')
        with open('hashing.txt', 'r+') as new_addr:
            new_address = new_addr.read().splitlines(keepends=True)
            bill_gen_qr(i + '\n' + ''.join(new_address[1:]))
            new_addr.seek(0)
            new_addr.truncate()
    print_pdf()

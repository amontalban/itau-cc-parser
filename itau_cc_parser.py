#!/usr/bin/env python

import argparse, csv, os, pdfquery, re, sys
from pdfminer.high_level import extract_text

POSICION_CARGOS_EXTERIOR = "502.230,619.642,519.030,626.642"
POSICION_FECHA_DE_EMISION = "493.500,724.060,541.500,734.060"

# Configurar argparse
parser = argparse.ArgumentParser(description="Extraer compras del extracto de tarjeta VISA del banco Itaú en formato PDF a formato CSV.")
parser.add_argument("-i", "--input", dest="input", help="Nombre del o los archivos PDF a ser procesados. Valor por defecto 'V_22.pdf'", default="V_22.pdf", type=argparse.FileType('r'), nargs='*')
parser.add_argument("-o", "--output", dest="output", help="Nombre del archivo CSV a ser guardado con el detalle de las compras. Valor por defecto 'itau.csv'", default="itau.csv")
parser.add_argument('--headers', help="Agregar los encabezados al archivo CSV de salida. Activado por defecto.", action=argparse.BooleanOptionalAction, default=True)
parser.add_argument('--force', help="Forzar la sobreescritura del archivo de salida. Desactivado por defecto.", action=argparse.BooleanOptionalAction, default=False)

# Parsear argumentos
args = parser.parse_args()

regexList = [
    "((?P<dia>\d{2})\s(?P<mes>\d{2})\s(?P<ano>\d{2})\s{2}(?P<tarjeta>\d{4})\s{4}(?P<detalle>.{35})(?P<cuotas>.{5})(?P<importe_origen>.{25})(?P<importe_pesos>.{14})(?P<importe_dolares>.{14})?)$",
    "((?P<detalle>(SEGURO DE VIDA SOBRE SALDO))\s+(?P<importe_pesos>[0-9,]+)?\s+(?P<importe_dolares>[0-9,]+)?)"
    ]

# Si el archivo output existe y tenemos la opción --force, borramos el archivo y continuamos
# caso contrario abortamos
if os.path.exists(args.output):
    if args.force:
        os.remove(args.output)
    else:
        print(f"El archivo {args.output} ya existe y la opcion --force no esta activa por lo cual no se puede sobreescribir la información!")
        sys.exit(1)

# Argparse crea un objeto del tipo _io.TextIOWrapper si solo se pasa un archivo
# o genera una lista de objetos _io.TextIOWrapper si son multiples archivos
# por lo cual generamos una lista en cualquier caso para poder iterar
if isinstance(args.input, list):
    files = args.input
else:
    files = [args.input]

for file in files:
    print(f"Procesando el archivo PDF {file.name} y exportando los registros al archivo {args.output}...")

    # Extraer texto del archivo PDF
    text = extract_text(file.name)

    try:
        if len(files) > 1:
            open_options = 'a'
        else:
            open_options = 'w'

        with open(args.output, open_options) as f:
            fieldnames = ['dia', 'mes', 'ano', 'tarjeta', 'detalle', 'cuotas', 'importe_origen', 'importe_pesos', 'importe_dolares']
            w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

            # Solo escribir los encabezados si es un unico archivo o el primero
            # de los archivos que estamos procesando
            if args.headers and files.index(file) == 0:
                w.writeheader()

            # Extraemos la fecha de emision para ser utilizada para las entradas
            # de seguro de vida sobre saldo y recargo por consumos en el exterior
            pdf = pdfquery.PDFQuery(file.name)
            data = pdf.extract([
                ('with_parent', 'LTPage[pageid="1"]'),
                ('with_formatter', 'text'),
                ('fecha_de_emision', f'LTTextBoxHorizontal:in_bbox("{POSICION_FECHA_DE_EMISION}")')
                ])
            fecha_de_emision = data["fecha_de_emision"]

            # Escribir los registros que matchean con las expresiones regulares definidas en regexList
            for regex in regexList:
                pattern = re.compile(regex, re.MULTILINE)
                matches = re.finditer(pattern, text)
                for match in matches:
                    entry = {k: v.strip() if isinstance(v, str) else v for k, v in match.groupdict().items()}
                    if "dia" not in entry.keys():
                        entry.update({'dia':f'{fecha_de_emision}'[0:2]})
                        entry.update({'mes':f'{fecha_de_emision}'[3:5]})
                        entry.update({'ano':f'{fecha_de_emision}'[6:8]})

                    w.writerow(entry)

            # Extraer el recargo por consumo en el exterior (Es siempre en USD con IVA Incluido)
            entry = pdf.extract([
                ('with_parent', 'LTPage[pageid="1"]'),
                ('with_formatter', 'text'),
                ('importe_dolares', f'LTTextBoxHorizontal:in_bbox("{POSICION_CARGOS_EXTERIOR}")'),
                ])
            entry.update({'detalle':'RECARGO POR CONSUMOS EN EL EXTERIOR'})
            entry.update({'dia':f'{fecha_de_emision}'[0:2]})
            entry.update({'mes':f'{fecha_de_emision}'[3:5]})
            entry.update({'ano':f'{fecha_de_emision}'[6:8]})
            w.writerow(entry)
    except:
        print(f"Error al procesar el archivo {file.name}!")
        if os.path.exists(f.name):
            f.close()
            os.remove(f.name)
        sys.exit(1)

print("Procesamiento completado.")
sys.exit(0)

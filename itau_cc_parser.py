#!/usr/bin/env python

import argparse, csv, os, re, sys
from pdfminer.high_level import extract_text

# Configurar argparse
parser = argparse.ArgumentParser(description="Extraer compras del extracto de tarjeta VISA del banco Itaú en formato PDF a formato CSV.")
parser.add_argument("-i", "--input-file", dest="input_file", help="Nombre del archivo PDF a ser procesado. Valor por defecto 'V_22.pdf'", default="V_22.pdf")
parser.add_argument("-o", "--output-file", dest="output_file", help="Nombre del archivo CSV a ser guardado con el detalle de las compras. Valor por defecto 'itau.csv'", default="itau.csv")

# Parsear argumentos
args = parser.parse_args()

regexList = [
    "((?P<dia>\d{2})\s(?P<mes>\d{2})\s(?P<ano>\d{2})\s{2}(?P<tarjeta>\d{4})\s{4}(?P<detalle>.{35})(?P<cuotas>.{5})(?P<importe_origen>.{25})(?P<importe_pesos>.{14})(?P<importe_dolares>.{14})?)$",
    "((?P<detalle>(SEGURO DE VIDA SOBRE SALDO))\s+(?P<importe_pesos>[0-9,]+)?\s+(?P<importe_dolares>[0-9,]+)?)"
    ]

if os.path.exists(args.input_file):
    print(f"Procesando el archivo PDF {args.input_file} y exportando los registros al archivo {args.output_file}...")

    # Extraer texto del archivo PDF
    text = extract_text(args.input_file)

    try:
        with open(args.output_file, 'w') as f:
            fieldnames = ['dia', 'mes', 'ano', 'tarjeta', 'detalle', 'cuotas', 'importe_origen', 'importe_pesos', 'importe_dolares']
            w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            w.writeheader()

            for regex in regexList:
                pattern = re.compile(regex, re.MULTILINE)
                matches = re.finditer(pattern, text)
                for match in matches:
                    entry = {k: v.strip() if isinstance(v, str) else v for k, v in match.groupdict().items()}
                    w.writerow(entry)
    except:
        print(f"Error al procesar el archivo {args.input_file}!")
        sys.exit(1)

    print("Procesamiento completado.")
    sys.exit(0)
else:
    print(f"El archivo {args.input_file} no existe!")
    sys.exit(1)

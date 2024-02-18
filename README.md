# Extractor de Compras de Extracto VISA

Este script Python extrae las compras de un extracto de tarjeta VISA del banco Itaú en formato PDF y las exporta a un archivo en formato CSV.

## Requisitos

Se necesita Python 3.6 o superior. Todos los requisitos de bibliotecas de Python están en el archivo `requirements.txt`.

## Instalación de Dependencias

Primero, clone el repositorio y cambie al directorio del proyecto:

```
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

Luego, instale las dependencias necesarias usando pip:

```
pip install -r requirements.txt
```

## Uso

Para ejecutar el script, utilice el siguiente comando, sustituyendo `<input_file.pdf>` y `<output_file.csv>` por los nombres de archivo deseados:

```
python itau_cc_parser.py -i <input_file.pdf> -o <output_file.csv>
```

Por defecto, si no se especifican archivos, el script buscará un archivo `V_22.pdf` como entrada y exportará a `itau.csv`.

### Ejemplo

```
python itau_cc_parser.py -i mi_extracto.pdf -o mis_compras.csv
```

## Plataformas Soportadas

- macOS
- Linux
- Windows

Asegúrese de tener instalado Python 3.6 o superior antes de ejecutar el script.


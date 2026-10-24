"""Genera las figuras de la práctica como PDF vectoriales, sin dependencias externas.

Uso:  python3 scripts/generar_figuras.py
Crea: figuras/proceso.pdf y figuras/libros_piratas.pdf
"""
import os

# Anchos aproximados de Helvetica (unidades /1000 em). Las vocales con tilde usan el de la base.
_W = {' ': 278, '.': 278, ',': 278, ':': 278, '-': 333, '(': 333, ')': 333, '%': 889, '≈': 584, '≥': 584}
_W.update(dict(zip('abcdefghijklmnopqrstuvwxyz',
                   [556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833,
                    556, 556, 556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500])))
_W.update(dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                   [667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
                    722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611])))
_W.update({d: 556 for d in '0123456789'})
_BASE = str.maketrans('áéíóúÁÉÍÓÚñÑü', 'aeiouAEIOUnNu')


def ancho(texto, tam, negrita=False):
    w = sum(_W.get(c.translate(_BASE), 556) for c in texto)
    return w * tam / 1000 * (1.06 if negrita else 1.0)


def _esc(texto):
    b = texto.replace('≥', '>=').replace('≈', '~').encode('cp1252')
    return b.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)')


class Lienzo:
    def __init__(self, w, h):
        self.w, self.h, self.ops = w, h, []

    def color(self, r, g, b, relleno=True):
        self.ops.append(f'{r:.3f} {g:.3f} {b:.3f} {"rg" if relleno else "RG"}'.encode())

    def rect_redondeado(self, x, y, w, h, r, relleno, borde=None):
        k = 0.5523 * r
        p = [f'{x + r} {y} m', f'{x + w - r} {y} l',
             f'{x + w - r + k} {y} {x + w} {y + r - k} {x + w} {y + r} c',
             f'{x + w} {y + h - r} l',
             f'{x + w} {y + h - r + k} {x + w - r + k} {y + h} {x + w - r} {y + h} c',
             f'{x + r} {y + h} l',
             f'{x + r - k} {y + h} {x} {y + h - r + k} {x} {y + h - r} c',
             f'{x} {y + r} l', f'{x} {y + r - k} {x + r - k} {y} {x + r} {y} c', 'h']
        self.color(*relleno)
        if borde:
            self.color(*borde, relleno=False)
            self.ops.append(b'1.2 w')
        self.ops.append(' '.join(p + ['B' if borde else 'f']).encode())

    def rect(self, x, y, w, h, relleno):
        self.color(*relleno)
        self.ops.append(f'{x} {y} {w} {h} re f'.encode())

    def linea(self, x1, y1, x2, y2, grosor=1, rgb=(0, 0, 0)):
        self.color(*rgb, relleno=False)
        self.ops.append(f'{grosor} w {x1} {y1} m {x2} {y2} l S'.encode())

    def flecha(self, x1, y, x2, rgb=(0.3, 0.3, 0.3)):
        self.linea(x1, y, x2 - 7, y, 2, rgb)
        self.color(*rgb)
        self.ops.append(f'{x2} {y} m {x2 - 9} {y + 5} l {x2 - 9} {y - 5} l h f'.encode())

    def texto(self, x, y, s, tam=11, negrita=False, rgb=(0, 0, 0), alinear='izq'):
        if alinear == 'centro':
            x -= ancho(s, tam, negrita) / 2
        elif alinear == 'der':
            x -= ancho(s, tam, negrita)
        self.color(*rgb)
        self.ops.append(b'BT /F%d %d Tf %.2f %.2f Td (' % (2 if negrita else 1, tam, x, y)
                        + _esc(s) + b') Tj ET')

    def guardar(self, ruta):
        flujo = b'\n'.join(self.ops)
        objs = [
            b'<< /Type /Catalog /Pages 2 0 R >>',
            b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
            (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w} {self.h}] '
             '/Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> /Contents 4 0 R >>').encode(),
            b'<< /Length %d >>\nstream\n' % len(flujo) + flujo + b'\nendstream',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
            b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>',
        ]
        out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        offs = []
        for i, o in enumerate(objs, 1):
            offs.append(len(out))
            out += b'%d 0 obj\n' % i + o + b'\nendobj\n'
        xref = len(out)
        out += b'xref\n0 %d\n0000000000 65535 f \n' % (len(objs) + 1)
        out += b''.join(b'%010d 00000 n \n' % o for o in offs)
        out += b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(objs) + 1, xref)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'wb') as f:
            f.write(out)


def figura_proceso(ruta):
    c = Lienzo(640, 150)
    pasos = [('1. Compra', 'de libros usados', (0.86, 0.92, 0.98), (0.20, 0.40, 0.70)),
             ('2. Corte', 'del lomo', (0.99, 0.90, 0.80), (0.80, 0.45, 0.10)),
             ('3. Escaneo', 'de las páginas', (0.88, 0.96, 0.88), (0.20, 0.55, 0.25)),
             ('4. Reciclaje', 'del papel', (0.97, 0.86, 0.86), (0.70, 0.15, 0.15)),
             ('5. Entrenamiento', 'del modelo de IA', (0.92, 0.88, 0.97), (0.45, 0.30, 0.65))]
    bw, bh, gap, x0, y0 = 108, 70, 20, 10, 50
    for i, (t1, t2, fondo, borde) in enumerate(pasos):
        x = x0 + i * (bw + gap)
        c.rect_redondeado(x, y0, bw, bh, 10, fondo, borde)
        c.texto(x + bw / 2, y0 + 41, t1, 12, True, borde, 'centro')
        c.texto(x + bw / 2, y0 + 22, t2, 10, False, (0.15, 0.15, 0.15), 'centro')
        if i < len(pasos) - 1:
            c.flecha(x + bw + 2, y0 + bh / 2, x + bw + gap - 2)
    c.texto(320, 20, 'El libro físico desaparece: sólo queda la copia digital interna.',
            10, False, (0.35, 0.35, 0.35), 'centro')
    c.guardar(ruta)


def figura_barras(ruta):
    c = Lienzo(560, 250)
    datos = [('LibGen', 5_000_000, '≥ 5.000.000', (0.75, 0.20, 0.20)),
             ('PiLiMi', 2_000_000, '≥ 2.000.000', (0.85, 0.40, 0.30)),
             ('Books3', 196_640, '≈ 196.640', (0.92, 0.60, 0.45)),
             ('Obras del acuerdo', 500_000, '≈ 500.000', (0.25, 0.45, 0.70))]
    x0, ymax, alto, sep, escala = 130, 200, 30, 14, 330 / 5_000_000
    # Rejilla y eje
    for v in range(0, 5_000_001, 1_000_000):
        x = x0 + v * escala
        c.linea(x, 30, x, ymax + 10, 0.4, (0.82, 0.82, 0.82))
        c.texto(x, 16, f'{v // 1_000_000} M', 9, False, (0.4, 0.4, 0.4), 'centro')
    c.linea(x0, 30, x0, ymax + 10, 1.2, (0.2, 0.2, 0.2))
    for i, (nombre, v, etiqueta, rgb) in enumerate(datos):
        y = ymax - (i + 1) * (alto + sep) + sep
        if i == 3:
            y -= 8
            c.linea(20, y + alto + 11, 540, y + alto + 11, 0.6, (0.6, 0.6, 0.6))
        c.rect(x0, y, max(v * escala, 2), alto, rgb)
        c.texto(x0 - 8, y + 11, nombre, 11, True, (0.15, 0.15, 0.15), 'der')
        c.texto(x0 + v * escala + 6, y + 11, etiqueta, 10, False, (0.15, 0.15, 0.15))
    c.texto(280, 236, 'Copias de libros (millones)', 11, True, (0.2, 0.2, 0.2), 'centro')
    c.guardar(ruta)


if __name__ == '__main__':
    raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figuras')
    figura_proceso(os.path.join(raiz, 'proceso.pdf'))
    figura_barras(os.path.join(raiz, 'libros_piratas.pdf'))
    print('Figuras generadas en', os.path.normpath(raiz))

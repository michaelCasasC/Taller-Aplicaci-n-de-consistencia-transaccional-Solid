from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path.cwd(); AS=ROOT/'_report_assets'; AS.mkdir(exist_ok=True)
OUT=ROOT/'Informe_Verificacion_HotelBooking.docx'
REF=ROOT/'Proyecto_AD_CasasCastañoMichael.pdf.docx'
FONT='C:/Windows/Fonts/arial.ttf'; FONT_B='C:/Windows/Fonts/arialbd.ttf'; MONO='C:/Windows/Fonts/consola.ttf'
def pilfont(size=26, bold=False, mono=False):
    path=MONO if mono else FONT_B if bold else FONT
    return ImageFont.truetype(path,size)
def terminal(name, lines, file):
    w=1500; pad=42; titleh=78; lineh=41
    wrapped=[]
    f=pilfont(23,mono=True)
    probe=Image.new('RGB',(w,100),'white'); d=ImageDraw.Draw(probe)
    maxw=w-2*pad
    for line in lines:
        while d.textbbox((0,0),line,font=f)[2] > maxw:
            cut=len(line)
            while cut>10 and d.textbbox((0,0),line[:cut],font=f)[2]>maxw: cut-=1
            wrapped.append(line[:cut]); line='  '+line[cut:]
        wrapped.append(line)
    h=titleh+pad*2+lineh*len(wrapped)
    im=Image.new('RGB',(w,h),'#111827'); d=ImageDraw.Draw(im)
    d.rounded_rectangle((12,12,w-12,h-12),radius=18,fill='#111827',outline='#334155',width=2)
    d.rounded_rectangle((12,12,w-12,titleh),radius=18,fill='#263449')
    for i,c in enumerate(['#ff5f57','#febc2e','#28c840']): d.ellipse((pad+i*32,38,pad+18+i*32,56),fill=c)
    d.text((pad+120,30),name,font=pilfont(24,True),fill='#e2e8f0')
    y=titleh+pad
    for line in wrapped:
        d.text((pad,y),line,font=f,fill='#dbeafe'); y+=lineh
    path=AS/file; im.save(path); return path
def diagram_arch(file):
    w,h=1500,640; im=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im)
    f=pilfont(23,True); small=pilfont(20)
    boxes=[(35,230,220,360,'Cliente\nNavegador / API'),(300,230,500,360,'Flask\napp/main.py'),(580,230,800,360,'BookingService\napp/service.py'),(885,230,1115,360,'Repository\nPostgresBooking'),(1210,230,1460,360,'PostgreSQL\nguests · rooms\nbookings · payments')]
    for x1,y1,x2,y2,t in boxes:
        d.rounded_rectangle((x1,y1,x2,y2),radius=18,fill='#eaf1f8',outline='#24476b',width=4)
        d.multiline_text((x1+14,y1+28),t,font=f,fill='#17365d',align='center',spacing=10)
    for x1,x2 in [(220,300),(500,580),(800,885),(1115,1210)]:
        d.line((x1+4,295,x2-7,295),fill='#245b91',width=5); d.polygon([(x2-7,285),(x2+5,295),(x2-7,305)],fill='#245b91')
    d.rounded_rectangle((395,40,1085,155),radius=16,fill='#f4f7fa',outline='#9ab0c6',width=3)
    d.text((430,65),'Pago: PaymentProxy → HttpPaymentAdapter → CircuitBreaker',font=small,fill='#263d55')
    d.line((690,155,690,225),fill='#6785a3',width=4); d.polygon([(680,215),(690,229),(700,215)],fill='#6785a3')
    d.rounded_rectangle((450,440,1035,555),radius=16,fill='#f4f7fa',outline='#9ab0c6',width=3)
    d.text((485,465),'BOOKING_CONFIRMED → AuditObserver + NotificationObserver',font=small,fill='#263d55')
    d.line((690,360,690,430),fill='#6785a3',width=4); d.polygon([(680,420),(690,434),(700,420)],fill='#6785a3')
    pth=AS/file; im.save(pth); return pth
def diagram_db(file):
    w,h=1500,660; im=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im)
    titles=pilfont(26,True); body=pilfont(20)
    specs=[(40,80,340,320,'guests',['id PK','full_name','email UNIQUE','phone']),(430,80,730,320,'rooms',['id PK','room_number UNIQUE','room_type','nightly_rate CHECK','status']),(820,80,1160,360,'bookings',['id PK','guest_id FK','room_id FK','check_in','check_out CHECK','total_amount','status']),(1190,80,1470,320,'payments',['id PK','booking_id FK','amount CHECK','method','status'])]
    for x1,y1,x2,y2,name,fields in specs:
        d.rounded_rectangle((x1,y1,x2,y2),radius=12,fill='#f7f9fb',outline='#365d7e',width=3)
        d.rectangle((x1,y1,x2,y1+50),fill='#dce8f2'); d.text((x1+16,y1+10),name,font=titles,fill='#17365d')
        for i,item in enumerate(fields): d.text((x1+18,y1+66+i*35),item,font=body,fill='#283747')
    d.line((340,200,810,200),fill='#547894',width=4); d.polygon([(800,191),(814,200),(800,209)],fill='#547894')
    d.line((730,260,810,260),fill='#547894',width=4); d.polygon([(800,251),(814,260),(800,269)],fill='#547894')
    d.line((1160,200,1180,200),fill='#547894',width=4); d.polygon([(1170,191),(1184,200),(1170,209)],fill='#547894')
    d.text((365,170),'1 : N',font=body,fill='#365d7e'); d.text((750,230),'1 : N',font=body,fill='#365d7e')
    pth=AS/file; im.save(pth); return pth
def diagram_patterns(file):
    w,h=1450,500; im=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im); f=pilfont(24,True); b=pilfont(21)
    d.rounded_rectangle((45,65,500,220),radius=16,fill='#eaf1f8',outline='#365d7e',width=4)
    d.multiline_text((75,92),'BookingService\nPaymentGateway.pay(...)',font=f,fill='#17365d',spacing=16)
    d.rounded_rectangle((590,65,1015,220),radius=16,fill='#f7f9fb',outline='#547894',width=4)
    d.multiline_text((625,92),'PaymentProxy\nvalida · audita · delega',font=f,fill='#17365d',spacing=16)
    d.rounded_rectangle((1100,65,1405,220),radius=16,fill='#eaf1f8',outline='#365d7e',width=4)
    d.multiline_text((1125,92),'HttpPaymentAdapter\nProveedor HTTP',font=f,fill='#17365d',spacing=16)
    d.line((500,145,580,145),fill='#245b91',width=5); d.polygon([(575,135),(592,145),(575,155)],fill='#245b91')
    d.line((1015,145,1090,145),fill='#245b91',width=5); d.polygon([(1085,135),(1102,145),(1085,155)],fill='#245b91')
    d.rounded_rectangle((150,315,610,430),radius=16,fill='#f4f7fa',outline='#9ab0c6',width=3)
    d.multiline_text((180,345),'EventBus\nBOOKING_CONFIRMED',font=f,fill='#263d55',spacing=12)
    d.rounded_rectangle((800,315,1340,430),radius=16,fill='#f4f7fa',outline='#9ab0c6',width=3)
    d.multiline_text((835,345),'AuditObserver  +  NotificationObserver',font=b,fill='#263d55',spacing=12)
    d.line((610,372,790,372),fill='#6785a3',width=4); d.polygon([(780,362),(798,372),(780,382)],fill='#6785a3')
    pth=AS/file; im.save(pth); return pth

figs=[]
figs.append(diagram_arch('f01_arch.png'))
figs.append(diagram_db('f02_db.png'))
figs.append(terminal('POST /api/bookings · respuesta',[
 'HTTP 201 Created', '{"booking_id":1,"status":"CONFIRMED","total":"90.00"}',
 'Detalle: habitación 101, 01–03 febrero 2027', 'Pago externo: aprobado · referencia EXT-1'
],'f03_commit.png'))
figs.append(terminal('POST /api/bookings · simulate_error=true',[
 'HTTP 409 Conflict', '{"error":"ERROR SIMULADO: provocar ROLLBACK"}',
 'Antes: bookings=3 payments=3', 'Después: bookings=3 payments=3'
],'f04_rollback.png'))
figs.append(terminal('python scripts/concurrency_demo.py',[
 '(409, habitación ya reservada en esas fechas)', '(201, {"booking_id":3,"status":"CONFIRMED","total":"90.00"})',
 'Esperado: una respuesta 201 y otra 409.'
],'f05_concurrency.png'))
figs.append(terminal('Validación de integridad referencial',[
 'POST guest_id=999, room_id=1', 'HTTP 409 Conflict',
 'La aplicación rechaza el huésped inexistente antes de registrar la reserva.'
],'f06_consistency.png'))
figs.append(terminal('GET /api/data · después de docker compose restart app',[
 'bookings: 3 registros', 'confirmadas: #1, #8 · cancelada: #3',
 'payments: 3 registros aprobados', 'Reserva #8: habitación 201 · total 240.00 · EXT-8'
],'f07_durability.png'))
figs.append(terminal('Proveedor detenido · intentos de pago',[
 'Intento 1: HTTP 409 · conexión externa fallida', 'Intento 2: HTTP 409 · conexión externa fallida',
 'Intento 3: HTTP 409 · conexión externa fallida', 'Intento 4: HTTP 409 · Circuit Breaker OPEN'
],'f08_cb_open.png'))
figs.append(terminal('Recuperación del Circuit Breaker',[
 'Estado inicial: OPEN', '[CircuitBreaker] OPEN -> HALF_OPEN',
 '[CircuitBreaker] HALF_OPEN -> CLOSED', 'Resultado: OK · Estado final: CLOSED'
],'f09_cb_recovery.png'))
figs.append(terminal('python -m unittest discover -s tests -v',[
 'test_breaker_opens ... ok', 'test_observer_two_subscribers ... ok',
 'test_proxy ... ok', 'Ran 3 tests in 0.001s', 'OK'
],'f10_unit_tests.png'))
figs.append(terminal('Pago confirmado a través del adaptador',[
 'HTTP 201 Created', '{"booking_id":8,"status":"CONFIRMED","total":"240.00"}',
 'Referencia devuelta por proveedor: EXT-8', 'Flujo: PaymentProxy → HttpPaymentAdapter → proveedor HTTP'
],'f11_adapter.png'))
figs.insert(9,diagram_patterns('f10_patterns.png'))

# Reutilizar el documento suministrado como base de diseño; conservar portada, márgenes,
# imagen institucional, encabezados y pies; retirar el contenido de la tarea anterior.
doc=Document(REF); body=doc._element.body
cover=[]
for el in list(body):
    if el.tag.endswith('}sectPr'): continue
    if el.tag.endswith('}p') and len(cover)<19: cover.append(el)
    else: body.remove(el)
for el in cover:
    if el.getparent() is None: body.insert(len(body)-1,el)

def setp(paragraph, text):
    if paragraph.runs:
        paragraph.runs[0].text=text
        for r in paragraph.runs[1:]: r.text=''
    else: paragraph.add_run(text)
paras=doc.paragraphs
setp(paras[7],'Taller de consistencia transaccional')
setp(paras[9],'Aplicaciones Distribuidas')
setp(paras[13],'23/11/2026')

sec=doc.sections[0]
sec.page_width=Inches(8.268); sec.page_height=Inches(11.693)
sec.top_margin=Inches(.984); sec.bottom_margin=Inches(.984); sec.left_margin=Inches(1.181); sec.right_margin=Inches(1.181)

def font_run(run, name='Arial', size=11, bold=None, italic=None, color='000000'):
    run.font.name=name; run._element.get_or_add_rPr().rFonts.set(qn('w:ascii'),name); run._element.get_or_add_rPr().rFonts.set(qn('w:hAnsi'),name)
    run.font.size=Pt(size); run.font.color.rgb=RGBColor.from_string(color)
    if bold is not None: run.bold=bold
    if italic is not None: run.italic=italic
def fmt_para(pa, hanging=True, double=True):
    pf=pa.paragraph_format; pf.line_spacing=2 if double else 1.0; pf.space_before=Pt(0); pf.space_after=Pt(0)
    if hanging: pf.left_indent=Inches(.5); pf.first_line_indent=Inches(-.5)
    else: pf.left_indent=Inches(0); pf.first_line_indent=Inches(0)
def add_text(text, boldlead=None):
    pa=doc.add_paragraph(style='Normal'); fmt_para(pa)
    if boldlead and text.startswith(boldlead):
        r=pa.add_run(boldlead); font_run(r,bold=True); r=pa.add_run(text[len(boldlead):]); font_run(r)
    else: font_run(pa.add_run(text))
    return pa
def add_heading(text, level=1):
    pa=doc.add_paragraph(style='Heading 1' if level==1 else 'Heading 2'); fmt_para(pa,False,False)
    pf=pa.paragraph_format; pf.keep_with_next=True; pf.space_before=Pt(14 if level==1 else 9); pf.space_after=Pt(5)
    r=pa.add_run(text); font_run(r,size=11,bold=True,color='000000'); return pa
def pagebreak(): doc.add_page_break()
def add_caption(n,title):
    pa=doc.add_paragraph(); fmt_para(pa,False,False); pa.alignment=WD_ALIGN_PARAGRAPH.LEFT; pa.paragraph_format.keep_with_next=True
    r=pa.add_run(f'Figura {n}'); font_run(r,size=11,bold=True)
    pa2=doc.add_paragraph(); fmt_para(pa2,False,False); pa2.alignment=WD_ALIGN_PARAGRAPH.LEFT; pa2.paragraph_format.keep_with_next=True
    r=pa2.add_run(title); font_run(r,size=11,italic=True)
def add_figure(n,title,path,explain):
    pa=doc.add_paragraph(); fmt_para(pa,False,False); pa.alignment=WD_ALIGN_PARAGRAPH.CENTER; pa.paragraph_format.keep_with_next=True
    pa.add_run().add_picture(str(path),width=Inches(6.1))
    add_caption(n,title); add_text(explain)
def add_code(lines):
    t=doc.add_table(rows=1,cols=1); t.alignment=WD_TABLE_ALIGNMENT.CENTER; c=t.cell(0,0); c.text=''
    tcPr=c._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:fill'),'F1F4F7'); tcPr.append(sh)
    for i,line in enumerate(lines.splitlines()):
        pa=c.paragraphs[0] if i==0 else c.add_paragraph(); pa.paragraph_format.line_spacing=1.0; pa.paragraph_format.space_after=Pt(0)
        r=pa.add_run(line); font_run(r,'Consolas',9,color='17365D')
    doc.add_paragraph()
def add_figure_para(text): add_text(text)

# Typography throughout the document, including retained cover text.
for sname in ['Normal','Heading 1','Heading 2','Caption']:
    st=doc.styles[sname]; st.font.name='Arial'; st.font.size=Pt(11); st.font.color.rgb=RGBColor(0,0,0)
for pa in doc.paragraphs:
    for r in pa.runs: font_run(r,size=11)

pagebreak()
add_heading('Índice de Figuras',1)
for title in ['Arquitectura general del proyecto','Tablas y relaciones de la base de datos','Confirmación de una reserva con pago','Error simulado y rollback','Resultado de la prueba concurrente','Validación de integridad referencial','Consulta de datos tras reinicio de la aplicación','Delegación del Proxy y notificación Observer','Pago integrado mediante el Adapter','Servicio externo fallido y Circuit Breaker OPEN','Recuperación HALF-OPEN a CLOSED','Pruebas unitarias ejecutadas']:
    pa=doc.add_paragraph(); fmt_para(pa,False,True); font_run(pa.add_run(title),size=11)
pagebreak()

add_heading('Introducción',1)
add_text('Las aplicaciones que escriben en una base relacional deben conservar las reglas del negocio aun cuando una operación falle a mitad de camino o coincida con otra solicitud. PostgreSQL ofrece transacciones y mecanismos de bloqueo que permiten agrupar cambios y coordinar accesos concurrentes; la documentación explica que SELECT FOR UPDATE espera por conflictos sobre la misma fila y devuelve su versión actualizada cuando termina la transacción concurrente (PostgreSQL Global Development Group, s. f.).')
add_text('Los patrones de diseño describen soluciones reutilizables para problemas recurrentes de organización del software (Gamma et al., 1994). Los principios de diseño orientado a objetos, incluidos los principios SOLID, buscan que las responsabilidades y dependencias permitan extender y mantener el sistema con menor acoplamiento (Martin, 2003). En los servicios remotos, el patrón Circuit Breaker detiene temporalmente solicitudes a un proveedor que acumula fallos y habilita una llamada de prueba para evaluar la recuperación (Fowler, 2014).')
add_text('Este informe verifica el proyecto Hotel Booking, desarrollado con Python, Flask, PostgreSQL y Docker Compose. Se describe el flujo de reserva y pago, se contrastan sus componentes con la consigna y se registran resultados observados al ejecutar la aplicación. Las pruebas incluidas cubren una reserva confirmada, un rollback provocado, solicitudes concurrentes, persistencia tras reinicio, rechazo por integridad referencial y comportamiento del Circuit Breaker. La revisión también señala los requisitos que permanecen pendientes.')

add_heading('Objetivos',1)
add_heading('Objetivo general',2)
add_text('Comprobar el grado de cumplimiento del proyecto Hotel Booking frente a los requisitos funcionales, arquitectónicos, transaccionales y de entrega establecidos en INSTRUCCIONES.txt, y documentar los resultados con evidencia de ejecución.')
add_heading('Objetivos específicos',2)
for x in [
 'Identificar las tablas, tecnologías, capas y patrones implementados en el código fuente.',
 'Ejecutar y registrar las pruebas de operación normal, rollback, consistencia, concurrencia, durabilidad y fallo externo.',
 'Relacionar cada resultado con las propiedades ACID, los principios SOLID y los patrones solicitados.',
 'Determinar las brechas que deben atenderse antes de la entrega final del proyecto.'
]: add_text(x)

add_heading('Desarrollo',1)
add_heading('3.1 Descripción general',2)
add_text('Hotel Booking es una aplicación pequeña de reservas de hotel. El proyecto declara Python 3.12, Flask, PostgreSQL 16 y Docker Compose. La base de datos implementa guests, rooms, bookings y payments. README.md indica que el archivo recibido no contenía el DDL original de la base asignada; por ello se incluyó un esquema PostgreSQL propio. La relación exacta con el esquema oficial del curso todavía debe confirmarse.')
add_text('La pantalla web presenta formularios para registrar huéspedes y habitaciones, crear una reserva y consultar las cuatro tablas. La API permite consultar los datos, registrar huéspedes y habitaciones, reservar y cancelar reservas. La revisión del código no encontró una operación para editar una entidad, por lo que el CRUD no está completo.')

add_heading('3.2 Arquitectura general',2)
add_text('La aplicación separa rutas Flask, caso de uso, repositorio, pagos, eventos y resiliencia. BookingService recibe un repositorio, una pasarela de pago y un bus de eventos. El repositorio conecta con PostgreSQL; la ruta de pago pasa por PaymentProxy, HttpPaymentAdapter y CircuitBreaker antes de invocar el proveedor HTTP simulado.')
add_figure(1,'Arquitectura general del proyecto',figs[0],'La Figura 1 resume las dependencias observadas en app/main.py, app/service.py, app/repository.py, app/payment.py y app/observers.py. La publicación de BOOKING_CONFIRMED ocurre después de completar la transacción, de modo que los observadores reaccionan a una reserva confirmada.')

add_heading('3.3 Base de datos y relaciones',2)
add_text('El esquema declara cuatro entidades. bookings referencia guests y rooms mediante claves foráneas; payments referencia bookings. El esquema también contiene restricciones UNIQUE para los correos y números de habitación y restricciones CHECK para fechas, montos y estados. Estas reglas protegen los datos incluso si una solicitud llega a la base desde otro punto de acceso.')
add_figure(2,'Tablas y relaciones de la base de datos',figs[1],'La Figura 2 muestra las claves principales, referencias y validaciones relevantes de database/schema.sql. La aplicación realiza una comprobación adicional de disponibilidad antes de insertar una reserva. No existe una restricción de exclusión PostgreSQL que impida por sí sola los solapamientos si otra aplicación escribe directamente en la tabla bookings.')

add_heading('3.4 Flujo principal de reserva y pago',2)
add_text('La operación inicia una transacción y bloquea la fila de la habitación con SELECT FOR UPDATE. Luego valida la existencia de habitación y huésped, verifica solapamientos y fechas, calcula el total, inserta la reserva pendiente, procesa el pago, registra payments y cambia la reserva a CONFIRMED. El contexto de transacción confirma todos los cambios al terminar sin excepción. La literatura sobre PostgreSQL describe que SELECT FOR UPDATE bloquea la fila y coordina las transacciones que pretenden actualizarla concurrentemente (PostgreSQL Global Development Group, s. f.).')
add_code('''with c.transaction():
    room = c.execute("SELECT * FROM rooms WHERE id=%s FOR UPDATE", (room_id,)).fetchone()
    # validar disponibilidad y huésped
    booking_id = insertar_reserva_pendiente(...)
    payment = gateway.pay(total, booking_id)
    insertar_pago(booking_id, total, payment)
    confirmar_reserva(booking_id)''')
add_figure(3,'Confirmación de una reserva con pago',figs[2],'La Figura 3 registra la respuesta observada al reservar la habitación 101 por dos noches. El endpoint devolvió HTTP 201, la reserva quedó CONFIRMED y el total fue 90.00. El pago respondió con la referencia externa EXT-1, evidencia de que el flujo real utilizó el servicio de pago simulado.')

add_heading('3.5 CRUD y manejo controlado de errores',2)
add_text('La consulta GET /api/data y la pantalla principal permiten visualizar huéspedes, habitaciones, reservas y pagos. Los endpoints POST /api/guests, POST /api/rooms y POST /api/bookings cubren registros; POST /api/bookings/{id}/cancel cambia el estado a CANCELLED y constituye una eliminación lógica. La prueba de cancelación de la reserva 3 devolvió cancelled=true. No se encontró una ruta ni formulario de edición, así que el requisito mínimo de edición está pendiente.')
add_text('Los endpoints convierten errores de negocio y persistencia en respuestas HTTP controladas. Por ejemplo, una habitación ocupada o una referencia inválida genera HTTP 409 en la operación de reserva. La aplicación captura excepciones amplias; para una versión final conviene diferenciar errores de validación, conflictos de negocio y fallos del proveedor, y evitar devolver detalles internos del servicio externo al cliente.')

add_heading('3.6 Atomicidad y rollback',2)
add_text('Para comprobar atomicidad se envió simulate_error=true. El repositorio inserta primero la reserva pendiente y luego provoca deliberadamente una excepción antes de procesar el pago. La transacción de PostgreSQL se revirtió. Antes del intento había tres reservas y tres pagos; después seguían existiendo tres reservas y tres pagos.')
add_figure(4,'Error simulado y rollback',figs[3],'La Figura 4 muestra el HTTP 409 y los conteos antes y después del fallo. La ausencia de una reserva parcial y de un pago nuevo confirma, en esta ejecución, la propiedad de atomicidad: los cambios realizados en la transacción se conservaron juntos o se descartaron juntos.')

add_heading('3.7 Consistencia de datos',2)
add_text('La consistencia se apoya en restricciones de base de datos y validaciones de la operación. Se intentó reservar con guest_id=999, que no corresponde a un huésped existente. La API respondió HTTP 409 y no creó la reserva. También se verificaron las restricciones CHECK y las claves foráneas definidas en schema.sql. Estas medidas mantienen las reglas de fechas, montos y referencias en estados válidos.')
add_figure(5,'Validación de integridad referencial',figs[5],'La Figura 5 presenta la respuesta obtenida al enviar una reserva con un huésped inexistente. La aplicación detectó el problema antes de registrar la operación. La prueba confirma el rechazo controlado para este caso; no sustituye una auditoría exhaustiva de todas las restricciones del esquema.')

add_heading('3.8 Aislamiento y concurrencia',2)
add_text('Se ejecutó scripts/concurrency_demo.py, que envía dos solicitudes simultáneas para la habitación 101 en las mismas fechas. Una respuesta fue HTTP 201 y la otra HTTP 409 por conflicto de fechas. El bloqueo FOR UPDATE serializó el acceso a la fila de la habitación; la segunda transacción verificó la reserva confirmada y fue rechazada. El resultado mantuvo la disponibilidad consistente.')
add_figure(6,'Resultado de la prueba concurrente',figs[4],'La Figura 6 conserva la salida de la demostración concurrente. Aunque el orden de las respuestas puede variar, la condición esperada se cumplió: una reserva fue confirmada y la solicitud duplicada no generó un segundo resultado válido.')

add_heading('3.9 Durabilidad',2)
add_text('Después de confirmar una reserva, se reinició únicamente el contenedor app mediante docker compose restart app. PostgreSQL permaneció activo y el volumen hotel_pgdata conservó los registros. La consulta GET /api/data posterior al reinicio devolvió tres reservas y tres pagos, incluidos los datos confirmados antes del reinicio.')
add_figure(7,'Consulta de datos tras reinicio de la aplicación',figs[6],'La Figura 7 resume la consulta posterior al reinicio. Las reservas 1 y 8 permanecieron CONFIRMED y la reserva 3 conservó su estado CANCELLED; los tres pagos aprobados permanecieron asociados a sus reservas. Esto demuestra durabilidad para los COMMIT ejecutados en la prueba.')

add_heading('3.10 Aplicación de principios SOLID',2)
add_text('Responsabilidad única. app/main.py gestiona HTTP; BookingService representa el caso de uso; PostgresBookingRepository ejecuta SQL; y los observadores manejan auditoría y notificación. Sin embargo, el repositorio también coordina el procedimiento transaccional completo, por lo que su responsabilidad es amplia.')
add_text('Abierto/cerrado. PaymentGateway proporciona un contrato al que pueden agregarse nuevas pasarelas con implementaciones independientes. Sustitución de Liskov. FakePaymentGateway y HttpPaymentAdapter implementan el contrato PaymentGateway, aunque el proyecto no prueba el intercambio de ambas en el mismo flujo de servicio.')
add_text('Segregación de interfaces. BookingRepository, PaymentGateway y BookingObserver separan contratos pequeños por necesidad. Inversión de dependencias. BookingService recibe sus colaboraciones por constructor, pero build_services crea tipos concretos. La inversión está presente en el caso de uso y puede reforzarse inyectando también la fábrica de dependencias.')
add_text('La organización refleja los principios de diseño orientado a objetos que Martin (2003) presenta para sostener sistemas extensibles y mantenibles. La aplicación de SOLID es identificable, con las observaciones señaladas como oportunidades de mejora.')

add_heading('3.11 Patrón Proxy y patrón Observer',2)
add_text('PaymentProxy valida que el monto sea positivo, registra la operación y delega el pago al gateway real. Las pruebas unitarias existentes comprobaron que el proxy intercepta el pago mediante FakePaymentGateway. EventBus publica BOOKING_CONFIRMED a AuditObserver y NotificationObserver. La prueba de dos suscriptores confirmó que ambos reciben el evento. Estas implementaciones corresponden a patrones estructurales y de comportamiento descritos por Gamma et al. (1994).')
add_figure(8,'Delegación del Proxy y notificación Observer',figs[9],'La Figura 8 distingue la intercepción del pago y la difusión del evento. PaymentProxy valida y delega al gateway; EventBus envía BOOKING_CONFIRMED a AuditObserver y NotificationObserver. Las pruebas unitarias comprobadas en la Figura 12 verifican que el Proxy intercepte el pago y que ambos observadores reciban el evento.')

add_heading('3.12 Patrón Adapter y Circuit Breaker',2)
add_text('El proveedor externo ofrece executeTransaction(value, code), mientras que la aplicación usa pay(amount, booking_id). HttpPaymentAdapter transforma los argumentos y el resultado para mantener el contrato PaymentGateway. En la reserva confirmada del 23 de noviembre, el proveedor devolvió EXT-8 y la aplicación registró el pago por 240.00.')
add_figure(9,'Pago integrado mediante el Adapter',figs[11],'La Figura 9 muestra el resultado del endpoint tras recuperar el servicio. La referencia EXT-8 provino del proveedor externo y quedó asociada al pago confirmado. Esta ejecución comprueba la conversión entre la interfaz externa y el contrato que espera la aplicación.')
add_text('CircuitBreaker abre el circuito después de tres fallos consecutivos. Para provocar el escenario se detuvo external-service y se enviaron cuatro solicitudes. Las tres primeras fallaron en la conexión; la cuarta fue bloqueada localmente con Circuit Breaker OPEN, sin volver a llamar al proveedor. Fowler (2014) explica que un circuito abierto evita seguir enviando llamadas a un servicio que probablemente no responderá.')
add_figure(10,'Servicio externo fallido y Circuit Breaker OPEN',figs[7],'La Figura 10 muestra tres errores del servicio y el rechazo de la cuarta llamada debido al estado OPEN. Después se reactivó el proveedor y se esperaron más de diez segundos, intervalo de recuperación configurado por el proyecto. Una llamada de prueba terminó con éxito.')
add_text('La transición de recuperación se comprobó directamente con la clase CircuitBreaker en el contenedor: OPEN cambió a HALF_OPEN, una operación de prueba devolvió OK y el estado final fue CLOSED. El flujo real también completó una reserva tras reactivar el servicio. La instancia del circuito es interna y no existe un endpoint que consulte su estado; por ello la demostración de estados se apoya en la salida de consola de la clase y en las respuestas de la API.')
add_figure(11,'Recuperación HALF-OPEN a CLOSED',figs[8],'La Figura 11 registra las transiciones de la máquina de estados y el resultado exitoso de la llamada de prueba. La comprobación aislada demuestra el estado HALF_OPEN y el cierre del circuito; la prueba de integración anterior confirma que el proveedor recuperado procesó un pago real de demostración.')

add_heading('3.13 Pruebas realizadas y límites de la revisión',2)
add_text('Se levantó el proyecto con Docker Compose. Se verificaron la salud de la API, el registro normal, el rollback, la integridad referencial, la concurrencia, la cancelación lógica, la persistencia después de reiniciar app, el fallo del proveedor y la recuperación del Circuit Breaker. Además, se ejecutó la suite unitaria existente: tres pruebas terminaron correctamente.')
add_figure(12,'Pruebas unitarias ejecutadas',figs[10],'La Figura 12 recoge el resultado de unittest. El proyecto aún no tiene pruebas automatizadas específicas de la ruta completa de rollback, durabilidad o Adapter; esos escenarios se comprobaron con llamadas manuales a la API y consultas posteriores.')
add_text('No se encontró una URL real de repositorio en los archivos revisados ni un ZIP de entrega. Hay un SQL reproducible en database/BD_CasasMichael.sql, pero no el archivo custom database/BD_CasasMichael.backup requerido. Además, docker-compose.yml y app/config.py contienen local_demo_password como credencial local fija. El informe se entrega en DOCX por solicitud del estudiante; INSTRUCCIONES.txt pide que el archivo para Moodle sea PDF.')

add_heading('Conclusiones',1)
for x in [
 'La aplicación inicia con Docker Compose, conecta con PostgreSQL y ejecuta la operación de reserva y pago. La prueba normal confirmó una reserva con estado CONFIRMED y un pago aprobado.',
 'La atomicidad, la consistencia referencial, la concurrencia y la durabilidad fueron observadas en ejecución. El rollback mantuvo iguales los conteos de reservas y pagos; la competencia por una habitación produjo una respuesta exitosa y otra de conflicto; los datos confirmados persistieron tras reiniciar la aplicación.',
 'Proxy, Observer, Adapter y Circuit Breaker están implementados y fueron verificados mediante pruebas unitarias o solicitudes de integración. El circuito bloqueó llamadas mientras el servicio fallaba y volvió a CLOSED después de una prueba satisfactoria.',
 'El proyecto no cumple al 100 % la consigna. El CRUD carece de edición; no hay URL de repositorio, ZIP ni backup PostgreSQL custom; falta contrastar el esquema con la base oficial asignada y la contraseña local fija debe trasladarse a una variable de entorno.',
 'La evidencia de ejecución del informe se basa en respuestas HTTP, resultados de consola y consultas reales del contenedor. Los diagramas de arquitectura y datos explican la implementación, mientras que las figuras de pruebas reproducen las salidas observadas.'
]: add_text(x)

add_heading('Recomendaciones',1)
for x in [
 'Implementar y probar edición para una entidad principal, por ejemplo huéspedes, con validación y respuesta de error controlada.',
 'Solicitar o localizar el DDL oficial de Hotel Booking y adaptar database/schema.sql para que las tablas y relaciones correspondan a la base asignada.',
 'Generar database/BD_CasasMichael.backup con pg_dump -F c después de conservar los datos de demostración y comprobar la restauración con pg_restore.',
 'Crear el ZIP del proyecto excluyendo cachés, credenciales y archivos generados; incluir el backup y los archivos necesarios para reconstruir la aplicación.',
 'Añadir la URL real del repositorio a README.md y sustituir local_demo_password por variables de entorno documentadas.',
 'Añadir pruebas automatizadas para atomicidad, Adapter, aislamiento y recuperación HALF_OPEN → CLOSED. Exponer el estado del Circuit Breaker mediante un endpoint de diagnóstico o un logger con salida visible para facilitar la demostración.',
 'Exportar este documento a PDF para la entrega académica y verificar que las capturas y referencias mantengan una resolución legible.'
]: add_text(x)

add_heading('Bibliografía',1)
refs=[
 'Fowler, M. (2014, 6 de marzo). Circuit breaker. https://martinfowler.com/bliki/CircuitBreaker.html',
 'Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). Design patterns: Elements of reusable object-oriented software. Addison-Wesley Professional.',
 'Martin, R. C. (2003). Agile software development: Principles, patterns, and practices. Pearson Prentice Hall.',
 'PostgreSQL Global Development Group. (s. f.). Transaction isolation. En PostgreSQL 18 documentation. https://www.postgresql.org/docs/18/transaction-iso.html'
]
for ref in refs:
    pa=doc.add_paragraph(); fmt_para(pa,True,True); font_run(pa.add_run(ref),size=11)

doc.core_properties.title='Informe de verificación del proyecto Hotel Booking'
doc.core_properties.subject='Aplicación de consistencia transaccional, SOLID, patrones y ACID'
doc.core_properties.author='Casas Castaño Michael Alejandro'
doc.save(OUT)
print(OUT.resolve())

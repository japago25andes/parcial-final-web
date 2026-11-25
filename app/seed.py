"""Datos precargados. Se insertan solo la primera vez (cuando la base está vacía)."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import Autor, Categoria, Libro, Prestamo, Usuario
from app.seguridad import encriptar_password

PORTADA = "https://covers.openlibrary.org/b/id/{}-L.jpg"

USUARIOS = [
    # nombre, correo, contraseña, rol, activo
    ("Administrador General", "admin@biblioteca.com", "admin123", "admin", True),
    ("Carlos Rodríguez", "bibliotecario@biblioteca.com", "biblio123", "admin", True),
    ("Lector Demo", "lector@biblioteca.com", "lector123", "lector", True),
    ("María Gómez", "maria@correo.com", "lector123", "lector", True),
    ("Juan Pérez", "juan@correo.com", "lector123", "lector", True),
    ("Laura Martínez", "laura@correo.com", "lector123", "lector", True),
    ("Andrés Torres", "andres@correo.com", "lector123", "lector", False),
]

CATEGORIAS = [
    ("Literatura latinoamericana", "Novelas y cuentos de autores de América Latina."),
    ("Clásicos universales", "Obras fundamentales de la literatura mundial."),
    ("Ciencia ficción", "Historias sobre el futuro, la tecnología y otros mundos."),
    ("Fantasía", "Mundos imaginarios, magia y aventuras épicas."),
    ("Terror", "Relatos de miedo, monstruos y lo sobrenatural."),
    ("Infantil y juvenil", "Libros pensados para niños y jóvenes lectores."),
    ("Divulgación científica", "La ciencia explicada para todo público."),
    ("Historia", "Libros sobre el pasado de la humanidad."),
    ("Tecnología", "Programación, software y buenas prácticas."),
]

AUTORES = [
    # nombre, nacionalidad, fecha de nacimiento, biografía
    ("Gabriel García Márquez", "Colombiana", "1927-03-06", "Escritor y periodista colombiano, Premio Nobel de Literatura en 1982 y figura central del realismo mágico."),
    ("Isabel Allende", "Chilena", "1942-08-02", "Novelista chilena, una de las autoras en español más leídas del mundo."),
    ("Julio Cortázar", "Argentina", "1914-08-26", "Escritor argentino, maestro del cuento fantástico y autor de novelas experimentales."),
    ("Jorge Luis Borges", "Argentina", "1899-08-24", "Escritor argentino reconocido por sus cuentos sobre laberintos, espejos e infinitos."),
    ("Juan Rulfo", "Mexicana", "1917-05-16", "Escritor y fotógrafo mexicano que con una obra breve marcó la literatura latinoamericana."),
    ("Mario Vargas Llosa", "Peruana", "1936-03-28", "Novelista peruano, Premio Nobel de Literatura en 2010."),
    ("Jorge Isaacs", "Colombiana", "1837-04-01", "Escritor colombiano, autor de María, obra cumbre del romanticismo hispanoamericano."),
    ("José Eustasio Rivera", "Colombiana", "1888-02-19", "Escritor colombiano cuya novela La vorágine denuncia la explotación en las caucherías."),
    ("Miguel de Cervantes", "Española", "1547-09-29", "Novelista, poeta y dramaturgo español, máxima figura de la literatura en español."),
    ("Jane Austen", "Británica", "1775-12-16", "Novelista inglesa conocida por su ironía y su retrato de la sociedad de su época."),
    ("George Orwell", "Británica", "1903-06-25", "Escritor y periodista británico, autor de célebres sátiras políticas."),
    ("Ray Bradbury", "Estadounidense", "1920-08-22", "Escritor estadounidense de ciencia ficción y fantasía."),
    ("Isaac Asimov", "Estadounidense", "1920-01-02", "Escritor y bioquímico, uno de los grandes maestros de la ciencia ficción."),
    ("J. R. R. Tolkien", "Británica", "1892-01-03", "Filólogo y escritor británico, creador de la Tierra Media."),
    ("J. K. Rowling", "Británica", "1965-07-31", "Escritora británica, autora de la saga Harry Potter."),
    ("Mary Shelley", "Británica", "1797-08-30", "Escritora inglesa, autora de Frankenstein y precursora de la ciencia ficción."),
    ("Bram Stoker", "Irlandesa", "1847-11-08", "Novelista irlandés, autor de Drácula."),
    ("Antoine de Saint-Exupéry", "Francesa", "1900-06-29", "Escritor y aviador francés, autor de El principito."),
    ("Carl Sagan", "Estadounidense", "1934-11-09", "Astrónomo y divulgador científico estadounidense."),
    ("Stephen Hawking", "Británica", "1942-01-08", "Físico teórico británico, conocido por sus trabajos sobre los agujeros negros."),
    ("Yuval Noah Harari", "Israelí", "1976-02-24", "Historiador israelí, autor de libros de divulgación sobre la historia de la humanidad."),
    ("Robert C. Martin", "Estadounidense", None, "Ingeniero de software estadounidense conocido como Uncle Bob."),
    ("Andrew Hunt", "Estadounidense", None, "Programador y escritor, coautor de El programador pragmático."),
]

LIBROS = [
    # título, isbn, año, páginas, id portada, ejemplares, autor, categoría, sinopsis
    ("Cien años de soledad", "9788497592208", 1967, 432, 12627383, 5, "Gabriel García Márquez", "Literatura latinoamericana", "La historia de siete generaciones de la familia Buendía en el pueblo de Macondo."),
    ("El amor en los tiempos del cólera", "9780307389732", 1985, 451, 10096404, 3, "Gabriel García Márquez", "Literatura latinoamericana", "Florentino Ariza espera más de cincuenta años para declarar de nuevo su amor a Fermina Daza."),
    ("Crónica de una muerte anunciada", "9789588886176", 1981, 134, 8489859, 4, "Gabriel García Márquez", "Literatura latinoamericana", "La reconstrucción de un asesinato que todo el pueblo sabía que iba a ocurrir."),
    ("La casa de los espíritus", "9789994791521", 1982, 453, 3205226, 3, "Isabel Allende", "Literatura latinoamericana", "La saga de la familia Trueba a lo largo de cuatro generaciones."),
    ("Rayuela", "9788432221552", 1963, 633, 1047466, 2, "Julio Cortázar", "Literatura latinoamericana", "Una novela que puede leerse en distintos órdenes y sigue a Horacio Oliveira entre París y Buenos Aires."),
    ("Ficciones", "9780802190734", 1944, 196, 10832290, 3, "Jorge Luis Borges", "Literatura latinoamericana", "Cuentos con bibliotecas infinitas, laberintos y mundos imaginarios."),
    ("El Aleph", "9789897220715", 1949, 184, 14408958, 2, "Jorge Luis Borges", "Literatura latinoamericana", "Cuentos sobre la inmortalidad, la identidad y un punto que contiene todo el universo."),
    ("Pedro Páramo", "9789500718042", 1955, 131, 5419076, 4, "Juan Rulfo", "Literatura latinoamericana", "Juan Preciado viaja a Comala en busca de su padre y encuentra un pueblo habitado por murmullos."),
    ("La ciudad y los perros", "9789681903978", 1963, 394, 3221667, 2, "Mario Vargas Llosa", "Literatura latinoamericana", "La vida de un grupo de cadetes en un colegio militar de Lima."),
    ("María", "9789684321410", 1867, 305, 1946682, 3, "Jorge Isaacs", "Literatura latinoamericana", "Efraín regresa a la hacienda familiar en el Valle del Cauca y se enamora de su prima María."),
    ("La vorágine", "9788437609355", 1924, 287, 2270418, 2, "José Eustasio Rivera", "Literatura latinoamericana", "Arturo Cova huye a la selva y descubre la brutal explotación de los caucheros."),
    ("Don Quijote de la Mancha", "9788495722799", 1605, 1056, 13478610, 3, "Miguel de Cervantes", "Clásicos universales", "Un hidalgo que ha leído demasiados libros de caballería sale a recorrer el mundo junto a Sancho Panza."),
    ("Orgullo y prejuicio", "9788415083696", 1813, 432, 13574150, 2, "Jane Austen", "Clásicos universales", "Elizabeth Bennet y el señor Darcy deben superar su orgullo y sus prejuicios."),
    ("Rebelión en la granja", "9786070782633", 1945, 152, 13712713, 3, "George Orwell", "Clásicos universales", "Los animales de una granja expulsan a sus dueños, pero los cerdos terminan imponiendo su propia tiranía."),
    ("1984", "9780582777316", 1949, 352, 8745958, 4, "George Orwell", "Ciencia ficción", "Winston Smith vive bajo la vigilancia constante del Gran Hermano."),
    ("Fahrenheit 451", "9780246635716", 1953, 190, 12993656, 3, "Ray Bradbury", "Ciencia ficción", "En una sociedad donde los libros están prohibidos, un bombero encargado de quemarlos empieza a leerlos."),
    ("Crónicas marcianas", "9780898452136", 1950, 262, 9346537, 2, "Ray Bradbury", "Ciencia ficción", "Relatos sobre la colonización humana de Marte y sus consecuencias."),
    ("Yo, robot", "9780451035400", 1950, 245, 12385229, 2, "Isaac Asimov", "Ciencia ficción", "Cuentos sobre la relación entre humanos y robots a partir de las Tres Leyes de la Robótica."),
    ("Fundación", "9789875664586", 1951, 320, 12338424, 2, "Isaac Asimov", "Ciencia ficción", "Hari Seldon predice la caída del Imperio Galáctico y crea un plan para acortar la era oscura."),
    ("El hobbit", "9789505471584", 1937, 310, 12345036, 4, "J. R. R. Tolkien", "Fantasía", "Bilbo Bolsón se une a un grupo de enanos para recuperar un tesoro custodiado por un dragón."),
    ("La comunidad del anillo", "9789505471812", 1954, 576, 15270264, 3, "J. R. R. Tolkien", "Fantasía", "Frodo emprende el viaje para destruir el Anillo Único junto a ocho compañeros."),
    ("Harry Potter y la piedra filosofal", "9781408865606", 1997, 302, 15155833, 5, "J. K. Rowling", "Fantasía", "Harry descubre que es un mago y comienza su primer año en el Colegio Hogwarts."),
    ("Frankenstein", "9781693806766", 1818, 240, 12356249, 2, "Mary Shelley", "Terror", "Victor Frankenstein da vida a una criatura y luego la abandona, con trágicas consecuencias."),
    ("Drácula", "9781840228366", 1897, 384, 12216503, 2, "Bram Stoker", "Terror", "Un grupo de personas se enfrenta al conde Drácula, que ha viajado de Transilvania a Inglaterra."),
    ("El principito", "9788419275271", 1943, 110, 13499066, 5, "Antoine de Saint-Exupéry", "Infantil y juvenil", "Un aviador perdido en el desierto conoce a un pequeño príncipe llegado de otro planeta."),
    ("Cosmos", "9781537058504", 1980, 354, 8283901, 2, "Carl Sagan", "Divulgación científica", "Un recorrido por la historia del universo y de la ciencia que nos ha permitido entenderlo."),
    ("Breve historia del tiempo", "9781558008984", 1988, 241, 10432365, 2, "Stephen Hawking", "Divulgación científica", "El origen del universo, los agujeros negros y la naturaleza del tiempo explicados para todos."),
    ("Sapiens: De animales a dioses", "9788466361903", 2011, 456, 8634250, 3, "Yuval Noah Harari", "Historia", "Breve historia de la humanidad desde la aparición del Homo sapiens hasta hoy."),
    ("Código limpio", "9788441540842", 2008, 464, 8065615, 3, "Robert C. Martin", "Tecnología", "Principios y buenas prácticas para escribir código legible y fácil de mantener."),
    ("El programador pragmático", "9780132119177", 1999, 352, 10143650, 2, "Andrew Hunt", "Tecnología", "Consejos prácticos para convertirse en un mejor desarrollador de software."),
]

PRESTAMOS = [
    # correo del usuario, título del libro, hace cuántos días se prestó, días de plazo, días hasta devolverlo (None = sin devolver)
    ("lector@biblioteca.com", "Cien años de soledad", 3, 14, None),
    ("lector@biblioteca.com", "1984", 25, 14, None),  # vencido
    ("lector@biblioteca.com", "El principito", 60, 14, 9),
    ("maria@correo.com", "Rayuela", 2, 14, None),
    ("maria@correo.com", "Código limpio", 8, 14, None),
    ("maria@correo.com", "Cien años de soledad", 45, 14, 12),
    ("maria@correo.com", "Harry Potter y la piedra filosofal", 70, 14, 10),
    ("juan@correo.com", "Rayuela", 6, 14, None),  # Rayuela queda sin ejemplares
    ("juan@correo.com", "Harry Potter y la piedra filosofal", 10, 14, None),
    ("juan@correo.com", "Pedro Páramo", 30, 14, None),  # vencido
    ("juan@correo.com", "Cien años de soledad", 90, 14, 14),
    ("juan@correo.com", "El hobbit", 50, 14, 7),
    ("laura@correo.com", "El hobbit", 1, 14, None),
    ("laura@correo.com", "El principito", 20, 14, None),  # vencido
    ("laura@correo.com", "Fahrenheit 451", 40, 14, 13),
    ("andres@correo.com", "1984", 120, 14, 11),
]


def cargar_datos_iniciales(db: Session):
    if db.query(Usuario).count() > 0:
        return  # ya hay datos: no se vuelve a cargar

    usuarios = {}
    for nombre, correo, password, rol, activo in USUARIOS:
        usuarios[correo] = Usuario(
            nombre=nombre, correo=correo, password_hash=encriptar_password(password), rol=rol, activo=activo
        )
    categorias = {nombre: Categoria(nombre=nombre, descripcion=desc) for nombre, desc in CATEGORIAS}
    autores = {
        nombre: Autor(
            nombre=nombre,
            nacionalidad=nacionalidad,
            fecha_nacimiento=date.fromisoformat(nacimiento) if nacimiento else None,
            biografia=bio,
        )
        for nombre, nacionalidad, nacimiento, bio in AUTORES
    }
    libros = {}
    for titulo, isbn, anio, paginas, portada, ejemplares, autor, categoria, sinopsis in LIBROS:
        libros[titulo] = Libro(
            titulo=titulo,
            isbn=isbn,
            anio_publicacion=anio,
            paginas=paginas,
            sinopsis=sinopsis,
            portada_url=PORTADA.format(portada),
            ejemplares_totales=ejemplares,
            ejemplares_disponibles=ejemplares,
            autor=autores[autor],
            categoria=categorias[categoria],
        )

    hoy = date.today()
    prestamos = []
    for correo, titulo, hace_dias, plazo, devuelto_en in PRESTAMOS:
        inicio = hoy - timedelta(days=hace_dias)
        limite = inicio + timedelta(days=plazo)
        libro = libros[titulo]
        if devuelto_en is None:
            estado = "vencido" if limite < hoy else "activo"
            devolucion = None
            libro.ejemplares_disponibles -= 1
        else:
            estado = "devuelto"
            devolucion = inicio + timedelta(days=devuelto_en)
        prestamos.append(
            Prestamo(
                usuario=usuarios[correo],
                libro=libro,
                fecha_prestamo=inicio,
                fecha_limite=limite,
                fecha_devolucion=devolucion,
                estado=estado,
            )
        )

    db.add_all([*usuarios.values(), *categorias.values(), *autores.values(), *libros.values(), *prestamos])
    db.commit()
    print("Datos iniciales cargados correctamente")

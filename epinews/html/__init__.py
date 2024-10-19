
from .manipulate import *
import lxml


def pipeline(url):
    # Recibir el HTML con request 
    
    
    # Manejarlo como objeto lxml para la limpieza
    doc = vacuum(doc)
'''
ESTE ES EL CÓDIGO PARA FUNCIONES DE CRAWLING.

Aquí se depositan las funciones utilizadas exclusivamente para
recopilar los archivos PDF o los enlaces de las noticias. Para
este punto, ninguna función ingresa, recopila o preprocesa la
información. Los outputs de este archivos son los archivos crudos.
'''

### Librerías utilizadas
from selenium import webdriver                              # Scraping
from selenium.webdriver.firefox.options import Options      # Scraping
from selenium.webdriver.firefox.service import Service      # Scraping
from bs4 import BeautifulSoup as bs                         # Scraping
import requests                                             # Scraping
import os                                                   # Manejo de archivos
import zipfile                                              # Manejo de archivos
from io import BytesIO                                      # Manejo de archivos
from random import uniform                                  # Utilidad
from itertools import product                               # Utilidad
import multiprocessing as mp                                # Utilidad
import pandas as pd                                         # Utilidad
import time                                                 # Utilidad

'''
Parámetros de Selenium utilizados.

Service: indicador del driver para cuando Bisetti ejecute el código en Linux.
Options:
    - '--headless'                                      : No abrir la pestaña del driver mientras se ejecuta el código.
    - 'permissions.default.image:2'                     : Bloquea la carga de las imágenes.
'''

service = Service("/snap/bin/geckodriver")
options = Options()
options.add_argument('--headless')
options.set_preference('permissions.default.image',2)

def cdc_pdfs(año):
    '''
    Esta función se especializa en recoger cada archivo .zip dispuesto en el servidor del CDC. No se
    revisa el contenido aquí, solo se descarga todo lo que se tenga a disposición para procesarlo
    posteriormente. 
    '''
    
    # Seteo de strings relevantes para la función.
    errors = ''
    año_dir = os.path.join('pdfs',str(año))

    # Confirmación de que existen los directorios; si no, los creas.
    os.makedirs(año_dir,exist_ok=True)

    for sem in range(1,53):
        # Directorio para la semana
        sem_dir = os.path.join(año_dir,str(sem).zfill(2))
        
        if os.path.exists(sem_dir):
            '''
            Si ya existe el directorio, significa que anteriormente fue usado el código
            y se han extraído los documentos. Por lo tanto, no hace falta volver a iterar
            sobre esta semana epidemiológica.
            '''
            continue
        else:
            url = f'https://www.dge.gob.pe/portal/docs/vigilancia/sala/{año}/salaSE{str(sem).zfill(2)}.zip'
            req = requests.get(url)

            if req.status_code == 200:
                try:
                    # Se recupera el .zip y se extrae todo lo que tenga
                    zipped = zipfile.ZipFile(BytesIO(req.content))
                    zipped.extractall(sem_dir)

                except Exception as e:
                    errors += f'{sem_dir}: {e}\n'
    
    '''
    Si hubieran ocurrido errores durante la extracción de los archivos .zip, se exportará
    el log de errores para resolución manual en la carpeta de pdfs/. Si se mantiene vacío,
    no se exportará.
    '''
    if errors=='':
        pass
    else:    
        os.makedirs('logs',exist_ok=True)
        with open(os.path.join('logs',f'{año}_errors.txt'),'a') as f:
            f.writelines(errors)
            print(f'Errores en el año {año}. Mirar el log para más información.')

def google_crawl(disease,query,lock):
    '''
    Esta función acumula todos los hipervínculos hallados para el query de una enfermedad. La estructura
    separada de 'disease' y 'query' está ingeniada para ser procesado con multiprocessing.

    El parámetro lock, heredado del objeto Manager de la librería multiprocessing, permitirá generar una
    cola de espera para la actualización de escritura de archivos y que, por ende, no se genere un error
    o corrupción del archivo exportado final.
    '''
    
    def get_source(url):
        '''
        Dado que Google tiene implementados captchas para restringir las acciones automatizadas, se 
        utiliza un driver de Selenium para ingresar a la página de búsqueda y recoger el código HTML.
        '''
        
        driver = webdriver.Firefox(service=service,options=options)
        driver.get(url)
        time.sleep(uniform(0.5,1.9))
        soup = bs(driver.page_source, 'html.parser')
        driver.close()

        return soup
    
    def google_url(prompt):
        '''
        Configura los parámetros de búsqueda en el URL para facilitar la recolección de noticias.
        
        search?q    : query de consulta para el buscador. Para ser aceptados, los espacios deben ser "+".
        tbm=nws     : sección de noticias.
        tbs=sbd:1   : ordenamiento de resultados por fecha.
        '''

        return f'https://www.google.com/search?q={prompt.replace(' ','+')}&tbm=nws&tbs=sbd:1'
    
    def crawler(url):
        '''
        Realiza el recorrido por las paginaciones halladas para registrar todos los enlaces en un Dataframe.
        '''
        
        i = 2
        collection = {
            'data':[],
            'link':[],
            'date':[]
        }
        
        while True:
            latestSoup = get_source(url)
            
            # Si el enlace provisto genera resultados.
            if latestSoup.find_all('a',{'class':'WlydOe'}):
                for page in latestSoup.find_all('a',{'class':'WlydOe'}):
                    collection['disease'] += [disease]
                    collection['link'] += [page.url]
                    collection['date'] += [page.find_all('span')[-1].text]

                next_page = latestSoup.find('a',{'aria-label':f'Page {i}'})
                
                # Si existe una página luego del parseado.
                if next_page:
                    url = next_page.get('href')
                    i += 1
                else:
                    break
            else:
                break
            
        return pd.DataFrame(collection)
    
    df = crawler(google_url('peru AND ' + disease + query))
    
    # Cola de espera para la exportación de los datos obtenidos.
    with lock:
        df.to_csv('urls.csv',index=False, mode='a', header=not os.path.exists('urls.csv'))

def news_links(prompt: str,cpu: int=6):
    '''
    Esta función integra la arquitectura de multiprocessing para la recopilación de los archivos. Dado
    una enfermedad (que sería una prompt) y, de ser requerido, indicando el número de procesos paralelos
    que se quiere implementar (cpu), la función de google_crawl se ejecutará en simultáneo cpu veces hasta
    acabar con los elementos dados en la lista.
    '''
    
    def resolve_date(datetuple):
        '''
        
        '''
        
        year, month = datetuple
        
        if month!=12:
            return f' after:{year}-{str(month).zfill(2)}-01 before:{year}-{str(month + 1).zfill(2)}-01'
        else:
            return f' after:{year}-{month}-01 before:{year + 1}-01-01'
    
    datecombo = list(product(range(2005,2025),range(1,13)))
    
    with mp.Manager() as manager:
        '''
        Como la función exporta los archivos bajo la misma url, es necesario establecer una cola de escritura
        para evitar corrupciones o errores en el código. Por ello, se activa un objeto Manager para correr un
        servidor virtual donde se ejecutarán las funciones y se preservará la regla del Lock.
        '''
        
        l = manager.Lock()
        queries = [(prompt,resolve_date(datetuple),l) for datetuple in datecombo]

        with mp.Pool(processes=cpu) as pool:
            '''
            Inicio del multiprocessing.
            Sobre un máximo de cpu procesos, se ejecutarán las funciones cada vez que un núcleo se libere de tareas.
            '''
            
            pool.starmap(google_crawl,queries)

if __name__=='__main__':
    '''
    Solo se utiliza el código directamente desde este script para actualizar semanalmente
    con los nuevos reportes. 
    '''
    # cdc_pdfs(2024)
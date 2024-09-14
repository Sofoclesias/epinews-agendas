import requests
import os
import zipfile
from io import BytesIO

def cdc_pdfs(año):
    '''
    Esta función está interesada en recoger cada archivo .zip dispuesto en el servidor del CDC. No se
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
        with open(os.path.join('pdfs',f'{año}_errors.txt'),'a') as f:
            f.writelines(errors)
            print(f'Errores en el año {año}. Mirar el log en "pdfs/" para más información.')

if __name__=='__main__':
    '''
    Solo se utiliza el código directamente desde este script para actualizar semanalmente
    con los nuevos reportes. 
    '''
    cdc_pdfs(2024)
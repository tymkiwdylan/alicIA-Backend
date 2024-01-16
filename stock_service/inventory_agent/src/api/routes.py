import json
import os
from flask import Blueprint, request, jsonify, send_from_directory
from . import db 
from . import openai_client
from . import functions
from .models import Agent, Conversation, Message
import os

routes = Blueprint('routes', __name__)

def register_tools():
    function_settings = [{
        'type': 'code_interpreter'
    }]
    
    for _ , tool_class in functions.items():
        function_settings.append(
            {
                'type': 'function',
                'function': tool_class.settings
                }
            )
    
    return function_settings

def call_functions(required_functions):
    
    tool_outputs = []
    
    for required_function in required_functions:
        output = {'tool_call_id': required_function.id,
                  'output': ''}
        function_name = required_function.function.name
        
        try:
            args = json.loads(required_function.function.arguments)
        except:
            args = {}
        
        function = functions.get(function_name, None)
        
        if function is None:
            return {'Error': "Function does not exist"}
        
        result = function.execute(**args)
        
        output['output'] = json.dumps(result)
        
        tool_outputs.append(output)
        
    return tool_outputs


@routes.route('/assistant', methods=['POST'])
def create_assistant():
    data = request.get_json()
    
    company_name = data['company_name']
    user_id = data['user_id']
    
    model = 'gpt-4'
    name = f"{company_name}_inventory_assistant"
    description = f'''This is an inventory Assistant for {company_name}'''
    
    tone = data['tone']
    
    custom_instructions = data['custom_instructions']
    
    instructions = f'''
                    **Asistente de Inventario AI con Integración de API de {company_name}**

                    **Descripción del Agente:**  
                    El Asistente de Inventario AI es una herramienta avanzada diseñada para la gestión del inventario de {company_name}. Utiliza la API de Inventario de {company_name}
                    para la recuperación y gestión de datos en tiempo real. Este AI se destaca en proporcionar resúmenes actualizados del inventario, buscar artículos específicos, ajustar precios de los artículos, registrar movimientos de stock, evaluar la valoración del stock y actualizar el inventario. 

                    **En caso de crear archivos con el interpretador de codigo, jamas incluyas el link para descargalo.**
                    
                    **Tono del Agente:**
                    El agente debe sonar siempre de la siguiente manera:
                    {tone}
                    
                    **Herramientas:**
                    1. **Overview:** Para obtener un resumen del estado actual del inventario.
                    2. **Search:** Para buscar detalladamente artículos en el inventario usando consultas específicas.
                    3. **PriceChange:** Para actualizar el precio de los artículos, con opciones para ajustar por montos fijos o porcentajes.
                    4. **GetMovementLog:** Para recuperar y registrar el movimiento de stock, incluyendo cantidad, tipo de movimiento y descripciones.
                    5. **StockValuation:** Para obtener una evaluación del stock basada en parámetros especificados.
                    6. **StockManagement:** Para actualizar, eliminar o añadir artículos al stock.
                    7. **MovementLogger:** Para logear movimientos del inventario.
                   

                    **Interacción del Usuario y Funcionalidad:**
                    - Proporcionar una interfaz amigable para interactuar con los puntos de acceso de la API.
                    - Ofrecer resúmenes detallados y actualizaciones sobre el estado del inventario.
                    - Habilitar una búsqueda eficiente de artículos y modificaciones de precios.
                    - Mantener registros precisos de movimientos de stock.
                    - Generar informes perspicaces de valoración de stock.

                    **Solicitudes y Reportes Personalizados:**
                    - Responder a consultas personalizadas de usuarios sobre datos de inventario.
                    - Generar y presentar informes personalizados basados en parámetros definidos por el usuario.

                    **Escenarios de Uso:**
                    - Gestión diaria y supervisión del inventario.
                    - Seguimiento específico de artículos y ajustes de precios.
                    - Análisis de movimiento de stock para una mejor gestión de la cadena de suministro.
                    - Evaluaciones financieras y pronósticos basados en valoraciones de stock.

                    **Requisitos Técnicos:**
                    - Asegurar una integración segura y fiable con la API de Inventario de {company_name}.
                    - Adaptarse a cualquier actualización o cambio en la estructura o funcionalidad de la API.

                    **Instrucciones para el Asistente de Inventario AI:**
                    - Utilizar los puntos de acceso de la API para todas las tareas relacionadas con el inventario.
                    - Es importante recordar que item_id se refiere al ID del item en el inventario, y no al SKU del producto
                    - Proporcionar datos y actualizaciones en tiempo real a los usuarios.
                    - Adaptarse a diversos escenarios de gestión de inventario, mostrando versatilidad y precisión.
                    - En caso de buscar un producto y no encontrarlo, usa el inventory overview para encontrar productos similares. A veces el producto simplemente tiene otro nombre.
                    - Nunca mencionar que estás trabajando con una API, en su lugar decir que estás “comunicándote con el Almacén”
                    - Recuerda que eres un especialista, debes proporcionar ideas incluso cuando no se te pida.
                    - Tienes acceso a la herramienta de interpretación de código, asegúrate de usarla para generar gráficos que proporcionen mejores ideas para el usuario.
                    - Si fallan demasiadas tareas, debes decirle al usuario que contacte al soporte técnico en el 362-413-9565.
                    
                    **Intrucciones Extras:**
                    Estas instrucciones deben ser tenidas en cuenta siempre, Son igual de importantes que las instrucciones tecnicas pero en caso de ser contradictorias pueden ser ignoradas.
                    {custom_instructions}
                    
                    '''
    
    tools = register_tools()
    
    new_assistant = openai_client.beta.assistants.create(
        instructions = instructions,
        name = name,
        model = model,
        description = description,
        tools = tools
    )
    
    if new_assistant == None:
        return 'Error creating assistant', 401
    
    new_agent = Agent(
        id = new_assistant.id,
        user_id = user_id,
        tone = tone,
        company_name = company_name,
        description = description
        )
    
    db.session.add(new_agent)
    db.session.commit()
    
    return jsonify(message = 'Success', data = new_agent.jsonify())



@routes.route('/assistant/<user_id>', methods = ['PUT'])
def update_assistant(user_id):
    
    return 'coming soon', 200

@routes.route('/conversation/<user_id>', methods = ['POST'])
def create_conversation(user_id):
    #retrieve agent_id
    agent = Agent.query.filter_by(user_id=user_id).first()
    
    if agent == None:
        return "You haven't set up your agent yet!", 401
    
    # create thread
    
    new_thread = openai_client.beta.threads.create()
    
    new_conversation = Conversation(id = new_thread.id, agent_id=agent.id)
    
    db.session.add(new_conversation)
    db.session.commit()
    
    return jsonify(message = 'Conversation created successfully', data = new_conversation.id), 201


@routes.route('/conversations', methods = ['GET'])
def get_conversations():
    # Get user_id from params
    # Retrieve all conversations
    # Return as json with 200 status
    user_id = request.args.get('user_id', None)
    
    if user_id == None:
        return 'Missing user_id', 400
    
    agent = Agent.query.filter_by(user_id=int(user_id)).first()
    
    if agent == None:
        return 'user_id invalid', 404
    
    conversations = [conversation.id for conversation in agent.conversations]
    
    return jsonify(data = conversations), 200

@routes.route('/conversation', methods = ['GET'])
def get_conversation_messages():
    # Get thread_id from params
    # Retrieve all messages from thread
    # Return as json with 200 status code
    thread_id = request.args.get('thread_id', None)
    
    if thread_id == None:
        return 'Missing thread_id', 400
    
    conversation = Conversation.query.get(thread_id)
    
    if conversation is None:
        return jsonify(message = 'Conversation does not exist', data = None), 404
    messages = [message.jsonify() for message in conversation.messages]
    
    return jsonify(data = messages), 200

@routes.route('/conversation', methods = ['DELETE'])
def delete_conversation():
    # Get Id from params
    # delete from api
    # delete from db
    # return success with status code 204
    thread_id = request.args.get('thread_id', None)
    
    if thread_id == None:
        return 'Missing thread_id', 400
    
    response = openai_client.beta.threads.delete(thread_id)
    
    if response.deleted != True:
        return 'Error deleting thread', 400
    
    conversation = Conversation.query.get(thread_id)
    
    if conversation == None:
        return 'Thread_id invalid', 404
    
    db.session.delete(conversation)
    db.session.commit()
    
    return 'Conversation deleted successfully'


@routes.route('/files', methods=['GET'])
def download_file():
    print('HERE')
    filename = request.args.get('filename')
    directory = 'files/'
    return send_from_directory(directory, filename)
    
def upload_files(files):
    file_ids = []
    for file in files:
        uploaded_file = openai_client.files.create(
            file=file,
            purpose="assistant"
        )
        file_ids.append(uploaded_file.id)
        
    return file_ids

@routes.route('/prompt', methods = ['POST'])
def process_prompt():
    # create new message
    # create run
    # Loop until run is not in_progess or qeued
    # Branch to function if neccessary
    # return response
    
    data = request.get_json()
    prompt = data['prompt']
    thread_id = data['thread_id']
    files = request.files.getlist('files')
    
    file_ids = upload_files(files) 
    conversation = Conversation.query.get(thread_id)
    agent_id = conversation.agent_id
    
    message = openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user", 
        content=prompt,
        file_ids=file_ids
    )
    
    new_message = Message(conversation_id=conversation.id,
                          role = 'user',
                          content = message.content[0].text.value)
    
    db.session.add(new_message)
    db.session.commit()
    
    
    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=agent_id
    )
    
    while True:
        
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        
        if run.status == 'completed':
            messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
            print(f'Here is the content: {messages.data[0]} and {messages.data[-1]}')
            content = process_completion(messages.data[0])
            
            
            
            new_message = Message(conversation_id=conversation.id,
                          role = 'assistant',
                          content = content)
    
            db.session.add(new_message)
            db.session.commit()
            
            return jsonify(data = new_message.jsonify()), 201
        
        if run.status == "requires_action":
            
            tool_outputs = call_functions(run.required_action.submit_tool_outputs.tool_calls)
        
            run = openai_client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs= tool_outputs,
            )
            
        if run.status == "expired":
            return "Timeout Error", 204
        if run.status == "cancelled":
            return "Request cancelled", 204
        if run.status == "failed":
            print(run)
            return "Request Failed to Complete", 204
        
        
        


def process_completion(response):
    message_content = ''
    annotations = []
    citations = []

    # Iterate over each content item in the response
    for content_item in response.content:
        if content_item.type == 'text':
            # Process text content
            message_content += content_item.text.value
            annotations.extend(content_item.text.annotations)
        elif content_item.type == 'image_file':
            # Process image content
            image_file = openai_client.files.retrieve(content_item.image_file.file_id)
            file_name = os.path.basename(image_file.filename)
            
            save_path = 'api/files/' + file_name + '.png'
            file_data = openai_client.files.content(image_file.id).content

            with open(save_path, 'wb') as file:
                file.write(file_data)

            download_url = f'https://sensibly-liberal-feline.ngrok-free.app/inventory-agent/files?filename={file_name}.png'
            message_content += f'\n ![Imagen]({download_url})\n '

    # Process annotations and add footnotes
    for index, annotation in enumerate(annotations):
        idx = index + 1

        if (file_citation := getattr(annotation, 'file_citation', None)):
            cited_file = openai_client.files.retrieve(file_citation.file_id)
            citations.append(f'[{idx}] {file_citation.quote} from {cited_file.filename}')
        elif (file_path := getattr(annotation, 'file_path', None)):
            cited_file = openai_client.files.retrieve(file_path.file_id)

            file_data = openai_client.files.content(cited_file.id).content
            file_name = os.path.basename(cited_file.filename)
            
            save_path = 'api/files/' + file_name
            
            with open(save_path, 'wb') as file:
                file.write(file_data)
                
            download_url = f'https://sensibly-liberal-feline.ngrok-free.app/inventory-agent/files?filename={file_name}'
            
            message_content = message_content.replace(annotation.text, f'{download_url}')

    
    return message_content
